"""Branch and Bound with a fractional upper bound (linear relaxation of the knapsack).

Technique: Branch and Bound (the DFS decision tree + pruning by an optimistic estimate).

Complexity summary:
    best case    Θ(n log n)   - the sort dominates; e.g. when no module fits, only the n + 1 "skip"
                                nodes are visited and each bound stops at its first module (O(1)).
    worst case   O(n·2^n)     - up to 2^(n+1) - 1 nodes, each computing an O(n) bound.
    average case depends on how tight the bound is for the instance family (measured in the
                 report: fast on uncorrelated data, slow on strongly correlated data).
    space        Θ(n)         - sorted order, `chosen` and the recursion stack.
"""
from .model import Result
from .sorting import sort_by_ratio


def branch_and_bound(modules, budget):
    """Exact. Explores like the DFS but prunes branches whose upper bound cannot beat the best so far.

    Sorts by decreasing ratio; the upper bound fills the rest of the knapsack with whole modules
    and a fraction of the next one (floored, since scores are integers).
    Worst case Θ(2^n); usually fast on uncorrelated data.
    `operations` = nodes visited + steps spent computing bounds + comparisons of the sort.
    """
    n = len(modules)                          # O(1)
    counter = [0]                             # O(1)
    order = sort_by_ratio(modules, counter)   # Θ(n log n): needed for the fractional bound
    best_value = 0                            # O(1)
    best_indices = []                         # O(1)
    chosen = []                               # O(1)
    nodes = 0                                 # O(1)
    bound_steps = 0  # the cost of computing bounds (O(n) per node) is part of the operation count

    def upper_bound(k, used_time, score):
        """Dantzig's fractional bound for the modules order[k:]. O(n - k) time, O(1) space."""
        nonlocal bound_steps
        room, ub = budget - used_time, score               # O(1)
        for j in range(k, n):                              # at most n - k iterations
            bound_steps += 1                               # O(1)
            m = modules[order[j]]                          # O(1)
            if m.time <= room:                             # O(1): whole module fits
                room -= m.time                             # O(1)
                ub += m.score                              # O(1)
            else:
                return ub + (room * m.score) // m.time  # fraction of the module that did not fit; O(1)
        return ub                                          # O(1)

    def explore(k, used_time, score):                      # each call = one node
        nonlocal best_value, best_indices, nodes
        nodes += 1                                         # O(1)
        if score > best_value:                             # O(1)
            best_value = score                             # O(1)
            best_indices = list(chosen)                    # O(n) copy, only when the incumbent improves
        if k == n or upper_bound(k, used_time, score) <= best_value:  # O(n - k) for the bound
            return  # end of the list, or a branch that cannot improve: prune
        i = order[k]                                       # O(1)
        if used_time + modules[i].time <= budget:          # O(1): "take" branch if it fits
            chosen.append(i)                               # amortized O(1)
            explore(k + 1, used_time + modules[i].time, score + modules[i].score)
            chosen.pop()                                   # backtracking; O(1)
        explore(k + 1, used_time, score)                   # "skip" branch
    # Without pruning this is the DFS tree (<= 2^(n+1) - 1 nodes), and each node pays O(n) for
    # its bound: O(n·2^n). Pruning only removes nodes, so it never makes the worst case worse.

    explore(0, 0, 0)
    return Result("B&B", best_value, sorted(best_indices), nodes + bound_steps + counter[0])  # O(n log n) sort
