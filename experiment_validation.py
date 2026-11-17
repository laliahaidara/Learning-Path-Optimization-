"""Independent validation of the hand-written algorithms against established libraries.

The other experiments compare the group's algorithms with each other, so an error
shared by all of them would go unnoticed. This script uses external references:

    OR-Tools  - KnapsackSolver (C++; branch and bound for n <= 40, dynamic programming
                above that) as optimum oracle;
    SciPy     - optimize.milp (HiGHS integer programming) as a second oracle,
                and stats.pearsonr for the correlations (with p-value and 95% CI);
    NumPy     - corrcoef, a third implementation of the Pearson correlation;
    Python    - built-in sorted() with exact Fraction keys, against the merge sort.

Usage:
    pip install ortools scipy numpy
    python experiment_validation.py                (all blocks, ~10 min)
    python experiment_validation.py --only optimum (one block)

Blocks: optimum, guarantees, sorting, pearson, runtime, bnb. Outputs: results/validation_*.csv

Responsável: Dalila Rezende — revisado por todo o grupo.
"""
import argparse
import csv
import os
import random
import statistics
import time
from fractions import Fraction

import numpy as np
from ortools.algorithms.python import knapsack_solver
from scipy import stats
from scipy.optimize import Bounds, LinearConstraint, milp

from algorithms import (branch_and_bound, dp_memoized, dp_table, dp_vector, evaluate,
                        exhaustive_dfs, fptas, grasp, greedy, greedy_with_best_item,
                        meet_in_the_middle)
from algorithms.sorting import sort_by_ratio
from instances import FAMILIES, generate_instance
from real_instances import (SCORE_DEFINITIONS, TOPIC_SCORE_DEFINITIONS, real_instance,
                            real_topic_instance)

OUTPUT_DIR = "results"


def save_csv(name, rows):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(os.path.join(OUTPUT_DIR, name), "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


# ------------------------------------------------------------ library oracles
def ortools_optimum(modules, budget):
    """Optimal value according to OR-Tools (independent C++ implementation)."""
    if not modules:
        return 0
    # branch and bound for small n; OR-Tools' own dynamic programming for large n, where its
    # branch and bound runs out of memory on strongly correlated instances
    kind = (knapsack_solver.SolverType.KNAPSACK_MULTIDIMENSION_BRANCH_AND_BOUND_SOLVER if len(modules) <= 40
            else knapsack_solver.SolverType.KNAPSACK_DYNAMIC_PROGRAMMING_SOLVER)
    solver = knapsack_solver.KnapsackSolver(kind, "validation")
    solver.init([m.score for m in modules], [[m.time for m in modules]], [budget])
    return int(solver.solve())


def milp_optimum(modules, budget):
    """Optimal value according to SciPy/HiGHS (integer linear programming)."""
    if not modules:
        return 0
    values = np.array([m.score for m in modules], dtype=float)
    weights = np.array([[m.time for m in modules]], dtype=float)
    result = milp(c=-values, constraints=LinearConstraint(weights, ub=budget),
                  integrality=np.ones(len(modules)), bounds=Bounds(0, 1),
                  options={"mip_rel_gap": 0.0})  # the default 1e-4 gap may stop 1 point short
    if result.x is None:
        raise RuntimeError(f"milp failed: {result.message}")
    chosen = [i for i, x in enumerate(result.x) if x > 0.5]
    used, score = evaluate(modules, chosen)
    assert used <= budget, "milp returned an infeasible selection"
    return score


# --------------------------------------------------------------- instance sets
def protocol_instances(count=1200, seed=2024):
    """The same 1,200 random instances of the article's correctness protocol."""
    rng = random.Random(seed)
    for _ in range(count):
        n = rng.randint(0, 16)
        yield generate_instance(n, rng.choice(FAMILIES), rng.choice([0.1, 0.3, 0.5, 0.7, 1.0]),
                                rng.randrange(10 ** 9), rng.choice([5, 20]))


def grasp_instances():
    """The 1,800 instances of the GRASP protocol (experiment_grasp.py)."""
    for family in FAMILIES:
        for seed in range(40):
            for rho in (0.1, 0.3, 0.5, 0.7, 1.0):
                for n in (8, 12, 16):
                    yield generate_instance(n, family, rho, seed * 1000 + n)


def large_instances():
    for n in (50, 100, 200, 400, 600):
        for family in FAMILIES:
            for rho in (0.3, 0.5):
                for seed in range(3):
                    yield generate_instance(n, family, rho, 7000 + 13 * n + seed)


def real_module_instances():
    for score in SCORE_DEFINITIONS:
        modules = real_instance(score=score)
        for budget in range(30, 24 * 60 + 1, 15):
            yield modules, budget


def real_topic_instances():
    for score in TOPIC_SCORE_DEFINITIONS:
        modules = real_topic_instance(score=score)
        for budget in range(30, 20 * 60 + 1, 15):
            yield modules, budget


SMALL_EXACT = {"DFS": exhaustive_dfs, "DP (memoizada)": dp_memoized, "DP (vetor)": dp_vector,
               "B&B": branch_and_bound, "MITM": meet_in_the_middle}
# the group's B&B is left out of the large synthetic set: on strongly correlated instances it may
# not finish (measured separately in the `bnb` block); it is kept for the real topic instance
LARGE_EXACT = {"DP (memoizada)": dp_memoized, "DP (vetor)": dp_vector}
TOPIC_EXACT = {"DP (memoizada)": dp_memoized, "DP (vetor)": dp_vector, "B&B": branch_and_bound}


# -------------------------------------------------------------------- optimum
def exp_optimum():
    """Every exact algorithm of the group against the two library oracles."""
    print("== Optimum: hand-written exact algorithms vs OR-Tools and SciPy/HiGHS")
    sets = [("protocolo de correção (n<=16)", protocol_instances(), SMALL_EXACT),
            ("protocolo do GRASP (n<=16)", grasp_instances(), SMALL_EXACT),
            ("sintéticas grandes (n=50..600)", large_instances(), LARGE_EXACT),
            ("reais, módulos (n=12)", real_module_instances(), SMALL_EXACT),
            ("reais, tópicos (n=78)", real_topic_instances(), TOPIC_EXACT)]
    rows = []
    for label, instances, extra in sets:
        total = oracle_disagree = infeasible = 0
        mismatches = {name: 0 for name in ["DP (tabela)"] + list(extra)}
        worst = 0
        for modules, budget in instances:
            total += 1
            reference = ortools_optimum(modules, budget)
            if milp_optimum(modules, budget) != reference:
                oracle_disagree += 1
            table = dp_table(modules, budget)[0]
            used, score = evaluate(modules, table.indices)
            if used > budget or score != table.value:
                infeasible += 1
            results = {"DP (tabela)": table.value}
            results.update({name: algorithm(modules, budget).value for name, algorithm in extra.items()})
            for name, value in results.items():
                if value != reference:
                    mismatches[name] += 1
                    worst = max(worst, abs(value - reference))
        row = {"conjunto": label, "instancias": total, "oraculos_divergem": oracle_disagree,
               "selecao_dp_inviavel": infeasible, "maior_diferenca": worst}
        row.update({f"divergencias {name}": mismatches.get(name, "") for name in
                    ["DP (tabela)", "DP (memoizada)", "DP (vetor)", "B&B", "MITM", "DFS"]})
        rows.append(row)
        print(f"  {label:32s} {total:5d} instâncias  divergências: "
              f"{sum(mismatches.values())}  (oráculos entre si: {oracle_disagree})")
    save_csv("validation_optimum.csv", rows)


# ----------------------------------------------------------------- guarantees
def exp_guarantees():
    """Approximation guarantees and GRASP quality, measured against the library optimum."""
    print("== Guarantees of greedy / FPTAS / GRASP against the OR-Tools optimum")
    rows = []
    violations = {"guloso > ótimo": 0, "guloso+item < ótimo/2": 0, "FPTAS(0,1) < 0,9·ótimo": 0,
                  "FPTAS > ótimo": 0}
    total = 0
    for modules, budget in protocol_instances():
        total += 1
        opt = ortools_optimum(modules, budget)
        g, gi = greedy(modules, budget).value, greedy_with_best_item(modules, budget).value
        f = fptas(modules, budget, 0.1).value
        violations["guloso > ótimo"] += g > opt
        violations["guloso+item < ótimo/2"] += 2 * gi < opt or gi > opt
        violations["FPTAS(0,1) < 0,9·ótimo"] += f < 0.9 * opt
        violations["FPTAS > ótimo"] += f > opt
    for name, count in violations.items():
        rows.append({"verificacao": name, "instancias": total, "violacoes": count, "valor": ""})
        print(f"  {name:26s} violações: {count} / {total}")

    hits, gaps, total = 0, [], 0
    for modules, budget in grasp_instances():
        total += 1
        opt = ortools_optimum(modules, budget)
        value = grasp(modules, budget).value
        assert value <= opt, "GRASP above the library optimum"
        hits += value == opt
        gaps.append(0.0 if opt == 0 else 100 * (opt - value) / opt)
    summary = [("GRASP: % de ótimos", round(100 * hits / total, 1)),
               ("GRASP: gap médio (%)", round(statistics.mean(gaps), 3)),
               ("GRASP: pior gap (%)", round(max(gaps), 1))]
    for name, value in summary:
        rows.append({"verificacao": name, "instancias": total, "violacoes": "", "valor": value})
        print(f"  {name:26s} {value}")
    save_csv("validation_guarantees.csv", rows)


# -------------------------------------------------------------------- sorting
def exp_sorting():
    """Hand-written merge sort against Python's sorted() with exact rational keys."""
    print("== Merge sort vs sorted() (exact Fraction keys, both stable)")
    total = different = 0
    sources = list(protocol_instances()) + list(large_instances())
    sources += [(real_instance(score=s), 0) for s in SCORE_DEFINITIONS]
    sources += [(real_topic_instance(score=s), 0) for s in TOPIC_SCORE_DEFINITIONS]
    for modules, _ in sources:
        total += 1
        mine = sort_by_ratio(modules, [0])
        reference = sorted(range(len(modules)),
                           key=lambda i: Fraction(modules[i].score, modules[i].time), reverse=True)
        different += mine != reference
    print(f"  {total} listas ordenadas, ordens diferentes: {different}")
    save_csv("validation_sorting.csv", [{"listas": total, "ordens_diferentes": different}])


# -------------------------------------------------------------------- pearson
def exp_pearson():
    """Correlation of time and score: statistics (used in the report) vs NumPy vs SciPy."""
    print("== Pearson: statistics.correlation vs numpy.corrcoef vs scipy.stats.pearsonr")
    rows = []
    instances = [("modulos", s, real_instance(score=s)) for s in SCORE_DEFINITIONS]
    instances += [("topicos", s, real_topic_instance(score=s)) for s in TOPIC_SCORE_DEFINITIONS]
    for level, score, modules in instances:
        xs = [m.time for m in modules]
        ys = [m.score for m in modules]
        own = statistics.correlation(xs, ys)
        with_numpy = float(np.corrcoef(xs, ys)[0, 1])
        result = stats.pearsonr(xs, ys)
        low, high = result.confidence_interval(0.95)
        rows.append({"instancia": level, "score": score, "n": len(modules), "r_relatorio": round(own, 4),
                     "dif_numpy": f"{abs(own - with_numpy):.1e}",
                     "dif_scipy": f"{abs(own - result.statistic):.1e}",
                     "p_valor": round(result.pvalue, 4), "ic95_inf": round(low, 2), "ic95_sup": round(high, 2)})
        print(f"  {level}/{score:12s} n={len(modules):2d}  r={own:+.3f}  p={result.pvalue:.4f}  "
              f"IC95=[{low:+.2f}, {high:+.2f}]  dif. máx={max(abs(own - with_numpy), abs(own - result.statistic)):.1e}")
    save_csv("validation_pearson.csv", rows)


# -------------------------------------------------------------------- runtime
def measure(function, *args, repetitions=3):
    samples = []
    for _ in range(repetitions):
        start = time.perf_counter()
        function(*args)
        samples.append(time.perf_counter() - start)
    return statistics.median(samples)


def exp_runtime():
    """Wall-clock time of the pure-Python DP against the compiled libraries (same instances)."""
    print("== Runtime: DP in pure Python vs OR-Tools (C++) vs SciPy/HiGHS")
    rows = []
    for n in (50, 100, 200, 400, 600):
        modules, budget = generate_instance(n, "weakly_correlated", 0.5, 7000 + n)
        t_dp = measure(lambda: dp_table(modules, budget))
        t_or = measure(ortools_optimum, modules, budget)
        t_milp = measure(milp_optimum, modules, budget)
        rows.append({"n": n, "T": budget, "dp_python_ms": round(1000 * t_dp, 2),
                     "ortools_ms": round(1000 * t_or, 3), "scipy_milp_ms": round(1000 * t_milp, 2),
                     "dp_sobre_ortools": round(t_dp / t_or, 1), "dp_sobre_milp": round(t_dp / t_milp, 2)})
        print(f"  n={n:3d} T={budget:5d}  DP {1000 * t_dp:8.2f} ms  OR-Tools {1000 * t_or:7.3f} ms  "
              f"HiGHS {1000 * t_milp:7.2f} ms")
    save_csv("validation_runtime.csv", rows)


# ------------------------------------------------------------------------ bnb
def _bnb_worker(n, seed, queue):
    modules, budget = generate_instance(n, "strongly_correlated", 0.5, seed)
    start = time.perf_counter()
    result = branch_and_bound(modules, budget)
    queue.put((result.value, result.operations, time.perf_counter() - start))


def exp_bnb(limit_seconds=20):
    """Does the hand-written B&B finish on large strongly correlated instances? (time limit per run)"""
    import multiprocessing
    print(f"== Hand-written B&B on strongly correlated instances (limit {limit_seconds} s per run)")
    rows = []
    for n in (50, 100, 200, 400, 600):
        for k in range(3):
            seed = 7000 + 13 * n + k
            modules, budget = generate_instance(n, "strongly_correlated", 0.5, seed)
            reference = ortools_optimum(modules, budget)
            t_dp = measure(lambda: dp_table(modules, budget), repetitions=1)
            queue = multiprocessing.Queue()
            process = multiprocessing.Process(target=_bnb_worker, args=(n, seed, queue))
            process.start()
            process.join(limit_seconds)
            if process.is_alive():
                process.terminate()
                process.join()
                outcome = {"bnb_terminou": "não", "bnb_s": f">{limit_seconds}", "bnb_operacoes": "", "bnb_correto": ""}
            else:
                value, operations, seconds = queue.get()
                outcome = {"bnb_terminou": "sim", "bnb_s": round(seconds, 3), "bnb_operacoes": operations,
                           "bnb_correto": "sim" if value == reference else "NÃO"}
            rows.append({"n": n, "T": budget, "semente": seed, **outcome, "dp_s": round(t_dp, 3)})
            print(f"  n={n:3d} T={budget:5d}  B&B: {outcome['bnb_terminou']:3s} {outcome['bnb_s']} s   DP: {t_dp:.3f} s")
    save_csv("validation_bnb.csv", rows)


BLOCKS = {"optimum": exp_optimum, "guarantees": exp_guarantees, "sorting": exp_sorting,
          "pearson": exp_pearson, "runtime": exp_runtime, "bnb": exp_bnb}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--only", nargs="*", choices=sorted(BLOCKS), default=None)
    args = parser.parse_args()
    for name, block in BLOCKS.items():
        if args.only is None or name in args.only:
            block()


if __name__ == "__main__":
    main()
