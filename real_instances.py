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
"""
import csv
import os

from algorithms import LearningModule

DATA = os.path.join(os.path.dirname(__file__), "real_data", "guia_modules_anon.csv")
SCORE_DEFINITIONS = ("conclusao", "conteudo", "nps")


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
