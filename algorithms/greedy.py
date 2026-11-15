"""Greedy approach by score/time ratio (comparison algorithm) and its guaranteed variant.

Technique: greedy choice (always take the locally best module that still fits).

Complexity summary:
    algorithm      best         worst        average      space
    greedy         Θ(n log n)   Θ(n log n)   Θ(n log n)   Θ(n)
    greedy+item    Θ(n log n)   Θ(n log n)   Θ(n log n)   Θ(n)
The merge sort dominates and costs Θ(n log n) regardless of the input order.
"""
from .model import Result
from .sorting import sort_by_ratio


def greedy(modules, budget):
    """Sorts by decreasing score/time and takes every module that still fits.

    Time Θ(n log n) (the sort dominates). NOT optimal: it can be arbitrarily bad.
    """
    counter = [0]                                  # O(1)
    order = sort_by_ratio(modules, counter)        # Θ(n log n): merge sort by ratio
    used_time = value = 0                          # O(1)
    chosen = []                                    # O(1)
    for i in order:                                # exactly n iterations -> Θ(n)
        counter[0] += 1                            # O(1)
        if used_time + modules[i].time <= budget:  # O(1): feasibility test
            used_time += modules[i].time           # O(1)
            value += modules[i].score              # O(1)
            chosen.append(i)                       # amortized O(1)
    return Result("Greedy", value, sorted(chosen), counter[0])  # O(k log k), k = |chosen| <= n
    # Total: Θ(n log n) + Θ(n) + O(n log n) = Θ(n log n).


def greedy_with_best_item(modules, budget):
    """max(greedy, best single module): guarantees at least 1/2 of the optimal value.

    Time Θ(n log n) (greedy) + Θ(n) (scan for the best single module) = Θ(n log n).
    """
    base = greedy(modules, budget)                 # Θ(n log n)
    best = None                                    # O(1)
    for i, m in enumerate(modules):                # exactly n iterations -> Θ(n)
        if m.time <= budget and (best is None or m.score > modules[best].score):  # O(1)
            best = i                               # O(1)
    operations = base.operations + len(modules)    # O(1)
    if best is not None and modules[best].score > base.value:              # O(1)
        return Result("Greedy+item", modules[best].score, [best], operations)  # O(1)
    return Result("Greedy+item", base.value, base.indices, operations)       # O(1)
