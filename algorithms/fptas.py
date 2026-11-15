"""Knapsack FPTAS: (1 - ε)-approximation with time polynomial in n and 1/ε (independent of T).

Technique: Dynamic Programming over the (scaled) VALUE instead of the time, plus rounding.

Complexity summary (n = number of candidate modules, S = Σ v'_i <= n²/ε):
    best case    Θ(n)        - no module fits (no candidates): returns right after the filter.
    worst case   O(n³/ε)     - the table has (n+1)·(S+1) cells and S <= n·(n/ε).
    average case Θ(n·S)      - the loops always run over the whole table once candidates exist.
    space        Θ(n·S)      - the `weight` table.
"""
from .model import Result


def fptas(modules, budget, epsilon):
    """Scales the scores (v' = floor(v/K), K = ε·v_max/n) and runs the DP over the VALUE:
    weight[k][s] = least time needed to reach scaled score s with the first k modules.
    Guarantee: value >= (1 - ε)·optimum. Time Θ(n·S), where S = Σv' <= n²/ε.
    """
    cand = [i for i, m in enumerate(modules) if m.time <= budget and m.score > 0]  # Θ(n) filter
    if not cand:                                                     # O(1)
        return Result(f"FPTAS({epsilon})", 0, [], 0)                 # best case: Θ(n) in total
    n = len(cand)                                                    # O(1)
    K = epsilon * max(modules[i].score for i in cand) / n            # Θ(n) to find v_max
    scaled = [int(modules[i].score / K) for i in cand]               # Θ(n); each v'_i <= n/ε
    S = sum(scaled)                                                  # Θ(n); S <= n²/ε
    inf = budget + 1                         # sentinel larger than any feasible weight; O(1)
    weight = [[inf] * (S + 1) for _ in range(n + 1)]                 # (n+1)·(S+1) cells -> Θ(n·S)
    weight[0][0] = 0                                                 # O(1)
    operations = 0                                                   # O(1)
    for k in range(1, n + 1):                                        # n iterations
        w, e = modules[cand[k - 1]].time, scaled[k - 1]              # O(1)
        for s in range(S + 1):                                       # S + 1 iterations -> n·(S+1) in total
            operations += 1                                          # O(1)
            weight[k][s] = weight[k - 1][s]                          # skip module k; O(1)
            if s >= e and weight[k - 1][s - e] + w <= budget and weight[k - 1][s - e] + w < weight[k][s]:  # O(1)
                weight[k][s] = weight[k - 1][s - e] + w              # take module k; O(1)
    # Filling phase: Θ(n·S) = O(n · n²/ε) = O(n³/ε).

    s = max(x for x in range(S + 1) if weight[n][x] <= budget)       # Θ(S): best reachable scaled score
    chosen = []                                                      # O(1)
    for k in range(n, 0, -1):                # reconstruction; n iterations
        if weight[k][s] != weight[k - 1][s]:                         # O(1)
            chosen.append(cand[k - 1])                               # amortized O(1)
            s -= scaled[k - 1]                                       # O(1)
    value = sum(modules[i].score for i in chosen)                    # O(n): real (unscaled) score
    return Result(f"FPTAS({epsilon})", value, sorted(chosen), operations)  # O(n log n) sort, dominated
