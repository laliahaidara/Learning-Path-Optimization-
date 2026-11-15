"""Experiments on the real (anonymized) platform instances.

Usage:
    python experiment_real.py                   (all blocks)
    python experiment_real.py --only profile    (one block)

Blocks:
    profile      - dataset description and Pearson correlation time x score,
                   locating the real data among the synthetic families;
    algorithms   - the six algorithms on the real catalog, per weekly budget;
    gap          - greedy gap across a fine sweep of budgets;
    pseudopoly   - same instance in hours / 15-min blocks / minutes (T grows,
                   n fixed): the practical price of the DP's pseudo-polynomiality;
    sweep        - one DP table answers every budget (last row), per score.
"""
import argparse
import csv
import os
import statistics

from algorithms import (LearningModule, branch_and_bound, dp_memoized, dp_table,
                        dp_vector, exhaustive_dfs, fptas, greedy,
                        greedy_with_best_item, meet_in_the_middle)
from instances import generate_instance
from real_instances import (SCORE_DEFINITIONS, real_instance,
                            weekly_budgets_minutes)

OUTPUT_DIR = "results"


def run_dp(modules, budget):
    return dp_table(modules, budget)[0]


def fptas_10(modules, budget):
    return fptas(modules, budget, 0.1)


ALL = {"DFS": exhaustive_dfs, "DP": run_dp, "DP-vector": dp_vector,
       "DP-memo": dp_memoized, "B&B": branch_and_bound, "MITM": meet_in_the_middle,
       "Greedy": greedy, "Greedy+best": greedy_with_best_item, "FPTAS-0.1": fptas_10}
EXACT_REFERENCE = "DP"


def save_csv(name, rows):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(os.path.join(OUTPUT_DIR, name), "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def pearson(xs, ys):
    return statistics.correlation(xs, ys)


# ------------------------------------------------------------------ profile
def exp_profile():
    """Where does the real data sit among the synthetic families?"""
    print("== Real-data profile (times in minutes)")
    rows = []
    for score_def in SCORE_DEFINITIONS:
        modules = real_instance(score=score_def)
        times = [m.time for m in modules]
        scores = [m.score for m in modules]
        try:
            r = pearson(times, scores)
        except statistics.StatisticsError:
            r = float("nan")
        rows.append({"score": score_def, "n": len(modules),
                     "min_time": min(times), "max_time": max(times),
                     "pearson_time_score": round(r, 3)})
        print(f"  {score_def:10s} n={len(modules):2d} "
              f"tempos {min(times)}..{max(times)} min, Pearson r={r:+.3f}")
    # Synthetic references at the same n, for the table in the paper
    for family in ("uncorrelated", "weakly_correlated", "strongly_correlated"):
        sample_r = []
        for seed in range(30):
            modules, _ = generate_instance(12, family, 0.5, seed, max_time=400)
            sample_r.append(pearson([m.time for m in modules],
                                    [m.score for m in modules]))
        mean_r = statistics.mean(sample_r)
        rows.append({"score": f"sintetica:{family}", "n": 12, "min_time": "",
                     "max_time": "", "pearson_time_score": round(mean_r, 3)})
        print(f"  {family:22s} (sintetica, media de 30) r={mean_r:+.3f}")
    save_csv("real_profile.csv", rows)


# --------------------------------------------------------------- algorithms
def exp_algorithms():
    """All algorithms on the real catalog, one line per (score, budget)."""
    print("== All algorithms on the real catalog")
    rows = []
    for score_def in SCORE_DEFINITIONS:
        modules = real_instance(score=score_def)
        for label, budget in weekly_budgets_minutes().items():
            optimum = run_dp(modules, budget).value
            for name, algorithm in ALL.items():
                result = algorithm(modules, budget)
                loss = 0.0 if optimum == 0 else 100 * (optimum - result.value) / optimum
                rows.append({"score": score_def, "orcamento": label,
                             "algoritmo": name, "valor": result.value,
                             "otimo": optimum, "perda_pct": round(loss, 1),
                             "operacoes": result.operations})
            best = [r for r in rows if r["score"] == score_def
                    and r["orcamento"] == label and r["algoritmo"] == "Greedy"][0]
            print(f"  {score_def:10s} T={label:3s} otimo={optimum:4d} "
                  f"greedy perde {best['perda_pct']}%")
    save_csv("real_all_algorithms.csv", rows)


# ---------------------------------------------------------------------- gap
def exp_gap():
    """Greedy gap over a fine budget sweep (every 15 min from 1h to 24h)."""
    print("== Greedy gap, fine budget sweep")
    rows = []
    for score_def in SCORE_DEFINITIONS:
        modules = real_instance(score=score_def)
        worst = (0.0, None)
        for budget in range(60, 24 * 60 + 1, 15):
            optimum = run_dp(modules, budget).value
            if optimum == 0:
                continue
            for name, algorithm in (("Greedy", greedy),
                                    ("Greedy+best", greedy_with_best_item)):
                value = algorithm(modules, budget).value
                g = 100 * (optimum - value) / optimum
                rows.append({"score": score_def, "T_min": budget,
                             "algoritmo": name, "gap_pct": round(g, 2)})
                if name == "Greedy" and g > worst[0]:
                    worst = (g, budget)
        print(f"  {score_def:10s} pior gap do greedy: {worst[0]:.1f}% em T={worst[1]} min")
    save_csv("real_greedy_gap.csv", rows)


# --------------------------------------------------------------- pseudopoly
def exp_pseudopoly():
    """n fixed, finer time unit => larger T: only the DP pays for it."""
    print("== Pseudo-polynomial behavior on the real instance (score=conteudo)")
    rows = []
    for unit, label in ((60, "horas"), (15, "blocos de 15 min"), (5, "blocos de 5 min"),
                        (1, "minutos")):
        modules = real_instance(score="conteudo", unit_minutes=unit)
        budget = max(1, round(600 / unit))  # 10 h in the chosen unit
        for name in ("DFS", "DP", "B&B", "MITM", "Greedy"):
            result = ALL[name](modules, budget)
            rows.append({"unidade": label, "T": budget, "algoritmo": name,
                         "valor": result.value, "operacoes": result.operations})
        dp_ops = [r for r in rows if r["unidade"] == label and r["algoritmo"] == "DP"][0]
        print(f"  {label:18s} T={budget:4d}: DP {dp_ops['operacoes']:6d} ops")
    save_csv("real_pseudopolynomial.csv", rows)


# -------------------------------------------------------------------- sweep
def exp_sweep():
    """One DP table gives the optimal path value for EVERY budget up to 24h."""
    print("== Budget sweep from a single DP table (last row)")
    rows = []
    horizon = 24 * 60
    for score_def in SCORE_DEFINITIONS:
        modules = real_instance(score=score_def)
        _, table = dp_table(modules, horizon)
        last = table[len(modules)]
        for budget in range(0, horizon + 1, 15):
            rows.append({"score": score_def, "T_min": budget, "otimo": last[budget]})
        full = sum(m.time for m in modules)
        print(f"  {score_def:10s} otimo com 2h={last[120]}, 5h={last[300]}, "
              f"10h={last[600]}, tudo cabe a partir de {full} min")
    save_csv("real_budget_sweep.csv", rows)


BLOCKS = {"profile": exp_profile, "algorithms": exp_algorithms, "gap": exp_gap,
          "pseudopoly": exp_pseudopoly, "sweep": exp_sweep}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", nargs="*", choices=sorted(BLOCKS), default=None)
    args = parser.parse_args()
    for name, block in BLOCKS.items():
        if args.only is None or name in args.only:
            block()


if __name__ == "__main__":
    main()
