"""Real, anonymized instances from a Brazilian adaptive-learning platform (Sebrae/GuIA).

The CSV in real_data/ is an aggregated, anonymized export: courses and modules
appear as indices only (no titles, no IDs, no learner data). Per module it holds
the median observed study time in minutes (over sessions with recorded start and
completion), the topic count, started/completed counters and the course-level
mean NPS. Modules without a measured time are excluded (they have no feasible wi).

Score definitions (the experiments run all of them):
  conclusao  - completion rate in % (engagement/success proxy);
  conteudo   - number of topics (content-volume proxy, the article's hypothesis);
  nps        - course mean NPS x 10 (satisfaction proxy, constant within a course).

Responsável: Dalila Rezende — revisado por todo o grupo.
"""
import csv
import os

from algorithms import LearningModule

DATA = os.path.join(os.path.dirname(__file__), "real_data", "guia_modules_anon.csv")
DATA_TOPICS = os.path.join(os.path.dirname(__file__), "real_data", "guia_topics_anon.csv")
SCORE_DEFINITIONS = ("conclusao", "conteudo", "nps")
TOPIC_SCORE_DEFINITIONS = ("dominio", "engajamento")


def load_rows():
    """Rows with a measured median time (the only ones that yield a valid wi >= 1)."""
    with open(DATA, newline="", encoding="utf-8") as file:
        rows = [r for r in csv.DictReader(file) if r["mediana_min_real"]]
    return rows


def _score(row, definition):
    if definition == "conclusao":
        return max(0, round(100 * int(row["n_completed"]) / int(row["n_started"])))
    if definition == "conteudo":
        return int(row["n_topics"])
    if definition == "nps":
        return round(10 * float(row["nps_medio"]))
    raise ValueError(f"unknown score definition: {definition}")


def real_instance(score="conclusao", unit_minutes=1, course=None):
    """Builds the module list; times in integer multiples of `unit_minutes`.

    unit_minutes=1 keeps the raw minutes; 15 gives 15-minute blocks; 60 gives hours.
    course=None uses the whole catalog (cross-course path); an int filters one course.
    """
    modules = []
    for row in load_rows():
        if course is not None and int(row["curso_idx"]) != course:
            continue
        minutes = float(row["mediana_min_real"])
        time = max(1, round(minutes / unit_minutes))
        name = f"C{row['curso_idx']}M{row['modulo_idx']}"
        modules.append(LearningModule(name, time, _score(row, score)))
    return modules


def weekly_budgets_minutes():
    """Realistic weekly study budgets, in minutes."""
    return {"2h": 120, "5h": 300, "10h": 600, "20h": 1200}


def _topic_score(row, definition):
    if definition == "dominio":
        return round(float(row["score_medio"]))          # mean activity score, 0..100
    if definition == "engajamento":
        return int(row["n_attempts"])                    # observed demand
    raise ValueError(f"unknown topic score definition: {definition}")


def real_topic_instance(score="dominio", unit_minutes=1):
    """Topic-level instance (finer grain, larger n).

    The platform measures study time per MODULE, not per topic, so each topic
    receives a share of its module's median time proportional to its number of
    generated activities (an observed workload proxy); topics without activity
    data split the remainder evenly. This allocation is the one modeling choice
    of the topic instance and is stated in the report.
    """
    with open(DATA_TOPICS, newline="", encoding="utf-8") as file:
        rows = [r for r in csv.DictReader(file)
                if r["mediana_min_modulo"] and r["score_medio"]]
    by_module = {}
    for row in rows:
        by_module.setdefault((row["curso_idx"], row["modulo_idx"]), []).append(row)
    modules = []
    for (course, module), topics in by_module.items():
        total_minutes = float(topics[0]["mediana_min_modulo"])
        total_activities = sum(int(t["n_activities"] or 0) for t in topics)
        for row in topics:
            if total_activities > 0:
                share = int(row["n_activities"] or 0) / total_activities
            else:
                share = 1 / len(topics)
            time = max(1, round(total_minutes * share / unit_minutes))
            name = f"C{course}M{module}T{row['topico_idx']}"
            modules.append(LearningModule(name, time, _topic_score(row, score)))
    return modules
