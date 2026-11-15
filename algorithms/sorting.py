"""Hand-written merge sort: Θ(n log n) in every case, stable, with a comparison counter.

Technique: Divide & Conquer.
    divide  - split the list in two halves                 Θ(1) to find the middle (+ Θ(n) to slice)
    conquer - sort each half recursively                   2·C(n/2)
    combine - merge the two sorted halves                  Θ(n)
Recurrence: C(n) = 2·C(n/2) + Θ(n)  =>  Θ(n log n) by the master theorem (case 2).
The cost does not depend on the initial order, so best = worst = average = Θ(n log n).
Space: Θ(n) auxiliary lists alive at any moment + Θ(log n) recursion stack.
"""


def merge(left, right, comes_before, counter):
    """Merges two sorted lists. `comes_before(a, b)` must be a STRICT relation.

    Complexity with a = len(left), b = len(right):
        time Θ(a + b) (every element is appended exactly once);
        comparisons between min(a, b) (best: one list runs out first) and a + b - 1 (worst).
        space Θ(a + b) for the output list.
    """
    output = []                                    # O(1)
    i = j = 0                                      # O(1)
    while i < len(left) and j < len(right):       # at most a + b - 1 iterations
        counter[0] += 1                            # O(1): one comparison counted
        if comes_before(right[j], left[i]):  # right goes first only if strictly before (stable); O(1)
            output.append(right[j])               # amortized O(1)
            j += 1                                 # O(1)
        else:
            output.append(left[i])                # amortized O(1)
            i += 1                                 # O(1)
    output.extend(left[i:])                        # O(elements left over in `left`)
    output.extend(right[j:])                       # O(elements left over in `right`)
    return output                                  # total Θ(a + b)


def merge_sort(items, comes_before, counter):
    """Divide in half, conquer (sort each half) and combine (merge).

    Complexity: T(n) = 2·T(n/2) + Θ(n)  =>  Θ(n log n) in the best, worst and average cases.
    The recursion tree has ⌈log2 n⌉ levels and each level does Θ(n) work (slices + merges).
    """
    if len(items) <= 1:                                         # base case, O(1)
        return list(items)                                      # O(1): copy of 0 or 1 element
    middle = len(items) // 2                                    # divide: O(1)
    left = merge_sort(items[:middle], comes_before, counter)    # slice Θ(n/2) + T(⌊n/2⌋)
    right = merge_sort(items[middle:], comes_before, counter)   # slice Θ(n/2) + T(⌈n/2⌉)
    return merge(left, right, comes_before, counter)            # combine: Θ(n)


def sort_by_ratio(modules, counter):
    """Module indices in decreasing order of score/time (no division, no floating point).

    Complexity: Θ(n) to build the index list + Θ(n log n) for the merge sort = Θ(n log n).
    Space Θ(n).
    """
    def ratio_greater(i, j):
        # v_i/w_i > v_j/w_j  <=>  v_i*w_j > v_j*w_i  (times are always >= 1)
        # Two multiplications and one comparison: O(1) per call.
        return modules[i].score * modules[j].time > modules[j].score * modules[i].time

    return merge_sort(list(range(len(modules))), ratio_greater, counter)  # Θ(n) + Θ(n log n)
