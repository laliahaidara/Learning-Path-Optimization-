"""Meet-in-the-middle (Horowitz–Sahni): exact, Θ(2^(n/2)) and independent of T."""
from .model import Result
from .sorting import merge


def _subsets_by_time(modules, indices, budget, counter):
    """All feasible subsets of `indices` as (time, score, bitmask), sorted by time.

    The sorting comes for free: for each module, the list is merged with its shifted copy
    (which is already sorted).
    """
    subsets = [(0, 0, 0)]
    for bit, i in enumerate(indices):
        w, v = modules[i].time, modules[i].score
        counter[0] += len(subsets)
        shifted = [(t + w, s + v, mask | (1 << bit)) for (t, s, mask) in subsets if t + w <= budget]
        subsets = merge(subsets, shifted, lambda a, b: a[0] < b[0], counter)
    return subsets


def _decode(mask, indices):
    return [indices[b] for b in range(len(indices)) if (mask >> b) & 1]


def meet_in_the_middle(modules, budget):
    """Splits the modules into two halves, enumerates the subsets of each and combines them with
    two pointers: for each subset of A, uses the best subset of B that fits in the remaining time."""
    n = len(modules)
    half = n // 2
    idx_a, idx_b = list(range(half)), list(range(half, n))
    counter = [0]
    A = _subsets_by_time(modules, idx_a, budget, counter)
    B = _subsets_by_time(modules, idx_b, budget, counter)

    best_up_to = []  # best_up_to[j] = index of the highest-score subset among B[0..j]
    for j, (_, score, _) in enumerate(B):
        if j == 0 or score > B[best_up_to[-1]][1]:
            best_up_to.append(j)
        else:
            best_up_to.append(best_up_to[-1])

    best_value, pair = -1, (0, 0)
    j = len(B) - 1
    for a in A:                                  # A is in increasing order of time
        while B[j][0] + a[0] > budget:           # the pointer in B only moves backwards
            j -= 1
            counter[0] += 1
        counter[0] += 1
        k = best_up_to[j]
        if a[1] + B[k][1] > best_value:
            best_value, pair = a[1] + B[k][1], (a[2], B[k][2])

    indices = _decode(pair[0], idx_a) + _decode(pair[1], idx_b)
    return Result("MITM", best_value, indices, counter[0])
