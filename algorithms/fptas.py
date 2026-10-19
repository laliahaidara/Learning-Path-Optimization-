"""Knapsack FPTAS: (1 - ε)-approximation with time polynomial in n and 1/ε (independent of T)."""
from .model import Result


def fptas(modules, budget, epsilon):
    """Scales the scores (v' = floor(v/K), K = ε·v_max/n) and runs the DP over the VALUE:
    weight[k][s] = least time needed to reach scaled score s with the first k modules.
    Guarantee: value >= (1 - ε)·optimum. Time Θ(n·S), where S = Σv' <= n²/ε.
    """
    cand = [i for i, m in enumerate(modules) if m.time <= budget and m.score > 0]
    if not cand:
        return Result(f"FPTAS({epsilon})", 0, [], 0)
    n = len(cand)
    K = epsilon * max(modules[i].score for i in cand) / n
    scaled = [int(modules[i].score / K) for i in cand]
    S = sum(scaled)
    inf = budget + 1                         # sentinel larger than any feasible weight
    weight = [[inf] * (S + 1) for _ in range(n + 1)]
    weight[0][0] = 0
    operations = 0
    for k in range(1, n + 1):
        w, e = modules[cand[k - 1]].time, scaled[k - 1]
        for s in range(S + 1):
            operations += 1
            weight[k][s] = weight[k - 1][s]
            if s >= e and weight[k - 1][s - e] + w <= budget and weight[k - 1][s - e] + w < weight[k][s]:
                weight[k][s] = weight[k - 1][s - e] + w

    s = max(x for x in range(S + 1) if weight[n][x] <= budget)
    chosen = []
    for k in range(n, 0, -1):                # reconstruction
        if weight[k][s] != weight[k - 1][s]:
            chosen.append(cand[k - 1])
            s -= scaled[k - 1]
    value = sum(modules[i].score for i in chosen)
    return Result(f"FPTAS({epsilon})", value, sorted(chosen), operations)
