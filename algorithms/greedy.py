"""Greedy approach by score/time ratio (comparison algorithm) and its guaranteed variant."""
from .model import Result
from .sorting import sort_by_ratio


def greedy(modules, budget):
    """Sorts by decreasing score/time and takes every module that still fits.

    Time Θ(n log n) (the sort dominates). NOT optimal: it can be arbitrarily bad.
    """
    counter = [0]
    order = sort_by_ratio(modules, counter)
    used_time = value = 0
    chosen = []
    for i in order:
        counter[0] += 1
        if used_time + modules[i].time <= budget:
            used_time += modules[i].time
            value += modules[i].score
            chosen.append(i)
    return Result("Greedy", value, sorted(chosen), counter[0])


def greedy_with_best_item(modules, budget):
    """max(greedy, best single module): guarantees at least 1/2 of the optimal value."""
    base = greedy(modules, budget)
    best = None
    for i, m in enumerate(modules):
        if m.time <= budget and (best is None or m.score > modules[best].score):
            best = i
    operations = base.operations + len(modules)
    if best is not None and modules[best].score > base.value:
        return Result("Greedy+item", modules[best].score, [best], operations)
    return Result("Greedy+item", base.value, base.indices, operations)
