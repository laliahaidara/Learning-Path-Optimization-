"""Exhaustive DFS with time pruning and backtracking (the paper's strategy, knapsack version)."""
from .model import Result


def exhaustive_dfs(modules, budget):
    """Walks the include/exclude decision tree of the modules.

    Pruning: module i is only included if used_time + w_i <= T.
    Worst case Θ(2^n) nodes (everything fits); best case Θ(n) (nothing fits).
    """
    n = len(modules)
    best_value = 0
    best_indices = []
    chosen = []
    nodes = 0

    def explore(i, used_time, score):
        nonlocal best_value, best_indices, nodes
        nodes += 1
        if score > best_value:
            best_value = score
            best_indices = list(chosen)
        if i == n:
            return
        w = modules[i].time
        if used_time + w <= budget:          # "include" branch (with pruning)
            chosen.append(i)
            explore(i + 1, used_time + w, score + modules[i].score)
            chosen.pop()                     # backtracking: undo the choice before the other branch
        explore(i + 1, used_time, score)     # "exclude" branch

    explore(0, 0, 0)
    return Result("DFS", best_value, best_indices, nodes)
