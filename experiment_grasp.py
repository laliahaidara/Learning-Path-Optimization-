"""Bonus experiments: the GRASP metaheuristic (adapted from MAS-Cloud+).

Usage:
    python experiment_grasp.py                  (all blocks)
    python experiment_grasp.py --only quality   (one block)

Blocks:
    correctness - 1,800 random instances checked against the DP (the same
                  protocol as Section VI-B of the paper);
    quality     - mean/worst gap of greedy vs GRASP per family and n
                  (the bonus column for Table VII);
    real        - GRASP on the real platform instances (modules n=12 and
                  topics n=78), fine budget sweep and cost at weekly budgets;
    adversarial - the paper's adversarial instance, where the greedy scores 2.
"""
import argparse
import csv
import os
import statistics

from algorithms import LearningModule, dp_table, grasp, greedy
from instances import FAMILIES, generate_instance
from real_instances import (SCORE_DEFINITIONS, TOPIC_SCORE_DEFINITIONS,
                            real_instance, real_topic_instance,
                            weekly_budgets_minutes)

OUTPUT_DIR = "results"


def save_csv(name, rows):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(os.path.join(OUTPUT_DIR, name), "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def optimum(modules, budget):
    return dp_table(modules, budget)[0].value


def gap(opt, value):
    return 0.0 if opt == 0 else 100 * (opt - value) / opt


# -------------------------------------------------------------- correctness
def exp_correctness():
    print("== GRASP vs DP on 1,800 random instances (protocol of Section VI-B)")
    total = hits = 0
    gaps = []
    for family in FAMILIES:
        for seed in range(40):
            for rho in (0.1, 0.3, 0.5, 0.7, 1.0):
                for n in (8, 12, 16):
                    modules, budget = generate_instance(n, family, rho, seed * 1000 + n)
                    opt = optimum(modules, budget)
                    value = grasp(modules, budget).value
                    assert value <= opt, "GRASP exceeded the optimum: invalid solution"
                    total += 1
                    hits += value == opt
                    gaps.append(gap(opt, value))
    rows = [{"instancias": total, "otimo_pct": round(100 * hits / total, 1),
             "gap_medio_pct": round(statistics.mean(gaps), 3),
             "pior_gap_pct": round(max(gaps), 1)}]
    print(f"  {total} instancias: otimo em {rows[0]['otimo_pct']}%, "
          f"gap medio {rows[0]['gap_medio_pct']}%, pior {rows[0]['pior_gap_pct']}%")
    save_csv("grasp_correctness.csv", rows)


# ------------------------------------------------------------------ quality
def exp_quality(count=30, rho=0.3):
    print(f"== Greedy vs GRASP per family (rho={rho}, {count} instances per cell)")
    rows = []
    for family in FAMILIES:
        for n in (8, 15, 30, 60):
            greedy_gaps, grasp_gaps, cost_ratio = [], [], []
            for seed in range(count):
                modules, budget = generate_instance(n, family, rho, seed)
                opt = optimum(modules, budget)
                g_res = greedy(modules, budget)
                m_res = grasp(modules, budget)
                greedy_gaps.append(gap(opt, g_res.value))
                grasp_gaps.append(gap(opt, m_res.value))
                cost_ratio.append(m_res.operations / max(1, g_res.operations))
            rows.append({"familia": family, "n": n,
                         "greedy_gap_medio": round(statistics.mean(greedy_gaps), 2),
                         "greedy_gap_pior": round(max(greedy_gaps), 1),
                         "grasp_gap_medio": round(statistics.mean(grasp_gaps), 2),
                         "grasp_gap_pior": round(max(grasp_gaps), 1),
                         "custo_grasp_vs_greedy": round(statistics.mean(cost_ratio), 1)})
            r = rows[-1]
            print(f"  {family:20s} n={n:2d}  greedy {r['greedy_gap_medio']:5.2f}%/"
                  f"{r['greedy_gap_pior']:4.1f}%  grasp {r['grasp_gap_medio']:4.2f}%/"
                  f"{r['grasp_gap_pior']:3.1f}%  custo x{r['custo_grasp_vs_greedy']}")
    save_csv("grasp_quality.csv", rows)


# --------------------------------------------------------------------- real
def exp_real():
    print("== GRASP on the real platform instances")
    rows = []
    instances = [("modulos", s, real_instance(score=s)) for s in SCORE_DEFINITIONS]
    instances += [("topicos", s, real_topic_instance(score=s))
                  for s in TOPIC_SCORE_DEFINITIONS]
    for level, score_def, modules in instances:
        worst_greedy = worst_grasp = 0.0
        for budget in range(30, 24 * 60 + 1, 15):
            opt = optimum(modules, budget)
            if opt == 0:
                continue
            worst_greedy = max(worst_greedy, gap(opt, greedy(modules, budget).value))
            worst_grasp = max(worst_grasp, gap(opt, grasp(modules, budget).value))
        ops = {name: alg(modules, weekly_budgets_minutes()["10h"]).operations
               for name, alg in (("greedy", greedy), ("grasp", grasp),
                                 ("dp", lambda m, b: dp_table(m, b)[0]))}
        rows.append({"instancia": level, "score": score_def,
                     "pior_gap_greedy": round(worst_greedy, 1),
                     "pior_gap_grasp": round(worst_grasp, 1),
                     "ops_greedy_10h": ops["greedy"], "ops_grasp_10h": ops["grasp"],
                     "ops_dp_10h": ops["dp"]})
        r = rows[-1]
        print(f"  {level}/{score_def:12s} pior gap: greedy {r['pior_gap_greedy']:5.1f}% "
              f"-> grasp {r['pior_gap_grasp']:4.1f}%   ops 10h: greedy {r['ops_greedy_10h']}, "
              f"grasp {r['ops_grasp_10h']}, DP {r['ops_dp_10h']}")
    save_csv("grasp_real.csv", rows)


# -------------------------------------------------------------- adversarial
def exp_adversarial():
    print("== Adversarial instance of Section IV-C")
    modules = [LearningModule("curto", 1, 2), LearningModule("longo", 1000, 1000)]
    budget = 1000
    rows = [{"algoritmo": "Greedy", "valor": greedy(modules, budget).value},
            {"algoritmo": "GRASP", "valor": grasp(modules, budget).value},
            {"algoritmo": "DP (otimo)", "valor": optimum(modules, budget)}]
    for r in rows:
        print(f"  {r['algoritmo']:10s} {r['valor']}")
    save_csv("grasp_adversarial.csv", rows)


BLOCKS = {"correctness": exp_correctness, "quality": exp_quality,
          "real": exp_real, "adversarial": exp_adversarial}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", nargs="*", choices=sorted(BLOCKS), default=None)
    args = parser.parse_args()
    for name, block in BLOCKS.items():
        if args.only is None or name in args.only:
            block()


if __name__ == "__main__":
    main()
