"""Exhaustive DFS with time pruning and backtracking (the paper's strategy, knapsack version).

Technique: brute force / backtracking over the binary decision tree (take or skip each module).

Complexity summary (N = number of nodes visited, n + 1 <= N <= 2^(n+1) - 1):
    each node does O(1) work, plus an O(n) copy only when the best solution improves.
    best case    Θ(n)    - no module fits (w_i > T for all i): only the "skip" path, n + 1 nodes.
    worst case   Θ(2^n)  - every module fits together (Σ w_i <= T): the full tree, 2^(n+1) - 1 nodes.
    average case depends on how generous T is (measured empirically in the report).
    space        Θ(n)    - recursion depth n + 1 and the list `chosen` with at most n elements.
"""
from .model import Result


def exhaustive_dfs(modules, budget):
    """Walks the include/exclude decision tree of the modules.

    Pruning: module i is only included if used_time + w_i <= T.
    Worst case Θ(2^n) nodes (everything fits); best case Θ(n) (nothing fits).
    """
    n = len(modules)                         # O(1)
    best_value = 0                           # O(1)
    best_indices = []                        # O(1)
    chosen = []                              # O(1): current partial selection (max n elements)
    nodes = 0                                # O(1)

    def explore(i, used_time, score):        # each call = one node of the decision tree
        nonlocal best_value, best_indices, nodes
        nodes += 1                           # O(1)
        if score > best_value:               # O(1)
            best_value = score               # O(1)
            best_indices = list(chosen)      # O(n) copy, only when the incumbent improves
        if i == n:                           # O(1): leaf, every module was decided
            return
        w = modules[i].time                  # O(1)
        if used_time + w <= budget:          # "include" branch (with pruning); O(1) test
            chosen.append(i)                 # amortized O(1)
            explore(i + 1, used_time + w, score + modules[i].score)  # subtree of size <= 2^(n-i) - 1
            chosen.pop()                     # backtracking: undo the choice before the other branch; O(1)
        explore(i + 1, used_time, score)     # "exclude" branch; always taken, so depth is always n

    # Recurrence for the number of nodes: N(i) = 1 + N_take(i+1) + N(i+1), N(n) = 1.
    # If every "take" is feasible: N(i) = 1 + 2·N(i+1)  =>  N(0) = 2^(n+1) - 1 = Θ(2^n).
    # If no "take" is feasible:    N(i) = 1 + N(i+1)    =>  N(0) = n + 1     = Θ(n).
    explore(0, 0, 0)
    return Result("DFS", best_value, best_indices, nodes)  # O(1)
