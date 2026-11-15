"""Meet-in-the-middle (Horowitz–Sahni): exact, Θ(2^(n/2)) and independent of T.

Technique: split-and-combine (Divide & Conquer with a single split): enumerate all subsets of
each half separately (2^(n/2) each instead of 2^n together) and combine them with two pointers.

Complexity summary (h = ⌈n/2⌉):
    best case    Θ(n)        - no module fits: both lists stay [(0, 0, 0)] and every merge is O(1).
    worst case   Θ(2^(n/2))  - Σ w_i <= T: nothing is pruned and each list has 2^h subsets.
    average case depends on T (how many subsets are feasible); measured in the report.
    space        O(2^(n/2))  - the two subset lists and the prefix-best array.
"""
from .model import Result
from .sorting import merge


def _subsets_by_time(modules, indices, budget, counter):
    """All feasible subsets of `indices` as (time, score, bitmask), sorted by time.

    The sorting comes for free: for each module, the list is merged with its shifted copy
    (which is already sorted).
    Complexity: after k modules the list has L_k <= 2^k entries and step k costs Θ(L_k), so the
    total is Σ_{k<h} O(2^k) = O(2^h) time and space (no extra log factor from sorting).
    """
    subsets = [(0, 0, 0)]                                    # O(1): only the empty subset
    for bit, i in enumerate(indices):                        # h iterations (h = size of this half)
        w, v = modules[i].time, modules[i].score             # O(1)
        counter[0] += len(subsets)                           # O(1)
        shifted = [(t + w, s + v, mask | (1 << bit)) for (t, s, mask) in subsets if t + w <= budget]  # Θ(L_k)
        subsets = merge(subsets, shifted, lambda a, b: a[0] < b[0], counter)  # Θ(L_k): merge of two sorted lists
    return subsets                                           # at most 2^h entries


def _decode(mask, indices):
    """Bitmask -> list of module indices. Θ(h) time."""
    return [indices[b] for b in range(len(indices)) if (mask >> b) & 1]  # h bit tests, O(1) each


def meet_in_the_middle(modules, budget):
    """Splits the modules into two halves, enumerates the subsets of each and combines them with
    two pointers: for each subset of A, uses the best subset of B that fits in the remaining time."""
    n = len(modules)                                         # O(1)
    half = n // 2                                            # O(1)
    idx_a, idx_b = list(range(half)), list(range(half, n))   # Θ(n)
    counter = [0]                                            # O(1)
    A = _subsets_by_time(modules, idx_a, budget, counter)    # O(2^(n/2))
    B = _subsets_by_time(modules, idx_b, budget, counter)    # O(2^⌈n/2⌉)

    best_up_to = []  # best_up_to[j] = index of the highest-score subset among B[0..j]
    for j, (_, score, _) in enumerate(B):                    # |B| iterations -> Θ(|B|)
        if j == 0 or score > B[best_up_to[-1]][1]:           # O(1)
            best_up_to.append(j)                             # amortized O(1)
        else:
            best_up_to.append(best_up_to[-1])                # amortized O(1)

    best_value, pair = -1, (0, 0)                            # O(1)
    j = len(B) - 1                                           # O(1)
    for a in A:                                  # A is in increasing order of time; |A| iterations
        while B[j][0] + a[0] > budget:           # the pointer in B only moves backwards
            j -= 1                               # O(1); at most |B| decrements over the WHOLE loop
            counter[0] += 1                      # O(1)
        counter[0] += 1                          # O(1)
        k = best_up_to[j]                        # O(1): best B subset that still fits with `a`
        if a[1] + B[k][1] > best_value:          # O(1)
            best_value, pair = a[1] + B[k][1], (a[2], B[k][2])  # O(1)
    # Two-pointer sweep: Θ(|A| + |B|) in total (amortized), not |A|·|B|.

    indices = _decode(pair[0], idx_a) + _decode(pair[1], idx_b)  # Θ(n)
    return Result("MITM", best_value, indices, counter[0])       # O(1)
