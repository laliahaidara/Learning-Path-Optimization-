"""Dynamic Programming for 0/1 knapsack (the proposed algorithm), in three versions.

Recurrence (D[i][t] = best score using the first i modules and t time units):
    D[0][t] = 0
    D[i][t] = D[i-1][t]                              if w_i > t
    D[i][t] = max(D[i-1][t], D[i-1][t-w_i] + v_i)    otherwise
"""
import sys

from .model import Result


def dp_table(modules, budget):
    """Bottom-up with the full table and solution reconstruction. Θ(n·T) time and space.

    Returns (Result, table) so that the report can display the table.
    """
    n = len(modules)
    D = [[0] * (budget + 1) for _ in range(n + 1)]
    operations = 0
    for i in range(1, n + 1):
        w, v = modules[i - 1].time, modules[i - 1].score
        for t in range(budget + 1):
            operations += 1
            D[i][t] = D[i - 1][t]                         # do not take module i
            if w <= t and D[i - 1][t - w] + v > D[i][t]:  # take module i
                D[i][t] = D[i - 1][t - w] + v

    chosen = []
    t = budget
    for i in range(n, 0, -1):          # reconstruction: walk backwards through the table
        if D[i][t] != D[i - 1][t]:     # the value changed, so module i was taken
            chosen.append(i - 1)
            t -= modules[i - 1].time
    chosen.reverse()
    return Result("DP (table)", D[n][budget], chosen, operations), D


def dp_vector(modules, budget):
    """Single-vector version: Θ(n·T) time, Θ(T) space (value only, no reconstruction)."""
    d = [0] * (budget + 1)
    operations = 0
    for m in modules:
        for t in range(budget, m.time - 1, -1):  # decreasing: each module is used at most once
            operations += 1
            if d[t - m.time] + m.score > d[t]:
                d[t] = d[t - m.time] + m.score
    return Result("DP (vector)", d[budget], [], operations)


def dp_memoized(modules, budget):
    """Top-down: the paper's DFS + memoization of the states (i, remaining time).

    `operations` = number of distinct states actually computed (<= n·(T+1)).
    """
    n = len(modules)
    sys.setrecursionlimit(max(sys.getrecursionlimit(), n + 100))
    memo = {}

    def best(i, t):
        if i == n:
            return 0
        if (i, t) in memo:
            return memo[(i, t)]
        answer = best(i + 1, t)
        w = modules[i].time
        if w <= t:
            answer = max(answer, best(i + 1, t - w) + modules[i].score)
        memo[(i, t)] = answer
        return answer

    value = best(0, budget)
    chosen = []
    t = budget
    for i in range(n):
        if best(i, t) != best(i + 1, t):
            chosen.append(i)
            t -= modules[i].time
    return Result("DP (memoized)", value, chosen, len(memo))
