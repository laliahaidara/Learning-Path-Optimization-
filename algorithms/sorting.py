"""Hand-written merge sort: Θ(n log n) in every case, stable, with a comparison counter."""


def merge(left, right, comes_before, counter):
    """Merges two sorted lists. `comes_before(a, b)` must be a STRICT relation."""
    output = []
    i = j = 0
    while i < len(left) and j < len(right):
        counter[0] += 1
        if comes_before(right[j], left[i]):  # right goes first only if strictly before (stable)
            output.append(right[j])
            j += 1
        else:
            output.append(left[i])
            i += 1
    output.extend(left[i:])
    output.extend(right[j:])
    return output


def merge_sort(items, comes_before, counter):
    """Divide in half, conquer (sort each half) and combine (merge)."""
    if len(items) <= 1:
        return list(items)
    middle = len(items) // 2
    left = merge_sort(items[:middle], comes_before, counter)
    right = merge_sort(items[middle:], comes_before, counter)
    return merge(left, right, comes_before, counter)


def sort_by_ratio(modules, counter):
    """Module indices in decreasing order of score/time (no division, no floating point)."""
    def ratio_greater(i, j):
        # v_i/w_i > v_j/w_j  <=>  v_i*w_j > v_j*w_i  (times are always >= 1)
        return modules[i].score * modules[j].time > modules[j].score * modules[i].time

    return merge_sort(list(range(len(modules))), ratio_greater, counter)
