"""Dynamic Programming for 0/1 knapsack (the proposed algorithm), in three versions.

Recurrence (D[i][t] = best score using the first i modules and t time units):
    D[0][t] = 0
    D[i][t] = D[i-1][t]                              if w_i > t
    D[i][t] = max(D[i-1][t], D[i-1][t-w_i] + v_i)    otherwise

Technique: Dynamic Programming (optimal substructure + overlapping subproblems).
There are (n+1)·(T+1) subproblems and each one is solved in O(1) from the previous row,
so the cost is Θ(n·T): PSEUDO-polynomial, because T is a number, not the input size
(writing T takes only log2(T) bits, so n·T is exponential in the bit length of T).

Complexity summary:
    version      best case   worst case   average     space
    table        Θ(n·T)      Θ(n·T)       Θ(n·T)      Θ(n·T)
    vector       Θ(n·T)*     Θ(n·T)       Θ(n·T)      Θ(T)
    memoized     Θ(n)        O(n·T)       reachable   O(n·T) cache + Θ(n) stack
                                          states
    * the inner loop of the vector version runs T - w_i + 1 times, so in the degenerate input
      where no module fits (w_i > T for all i) it only does Θ(n + T) work.
"""
import sys

from .model import Result


def dp_table(modules, budget):
    """Bottom-up with the full table and solution reconstruction. Θ(n·T) time and space.

    Returns (Result, table) so that the report can display the table.
    The loop bounds do not depend on the data, so best = worst = average = Θ(n·T).
    """
    n = len(modules)                                      # O(1)
    D = [[0] * (budget + 1) for _ in range(n + 1)]        # (n+1)·(T+1) cells -> Θ(n·T) time and space
    operations = 0                                        # O(1)
    for i in range(1, n + 1):                             # n iterations
        w, v = modules[i - 1].time, modules[i - 1].score  # O(1)
        for t in range(budget + 1):                       # T + 1 iterations -> n·(T+1) in total
            operations += 1                               # O(1)
            D[i][t] = D[i - 1][t]                         # do not take module i; O(1)
            if w <= t and D[i - 1][t - w] + v > D[i][t]:  # take module i; O(1)
                D[i][t] = D[i - 1][t - w] + v             # O(1)
    # Filling phase: n·(T+1) cells × O(1) = Θ(n·T).

    chosen = []                        # O(1)
    t = budget                         # O(1)
    for i in range(n, 0, -1):          # reconstruction: walk backwards through the table; n iterations
        if D[i][t] != D[i - 1][t]:     # the value changed, so module i was taken; O(1)
            chosen.append(i - 1)       # amortized O(1)
            t -= modules[i - 1].time   # O(1)
    chosen.reverse()                   # O(n)
    # Reconstruction phase: Θ(n), dominated by the Θ(n·T) filling phase.
    return Result("DP (table)", D[n][budget], chosen, operations), D


def dp_vector(modules, budget):
    """Single-vector version: Θ(n·T) time, Θ(T) space (value only, no reconstruction).

    Keeps only one row of the table: row i overwrites row i-1 in place.
    Inner iterations = Σ max(0, T - w_i + 1) <= n·(T+1).
    """
    d = [0] * (budget + 1)                       # Θ(T) time and space
    operations = 0                               # O(1)
    for m in modules:                            # n iterations
        for t in range(budget, m.time - 1, -1):  # decreasing: each module is used at most once; T - w_i + 1 iterations
            operations += 1                      # O(1)
            if d[t - m.time] + m.score > d[t]:   # d[t - w_i] still holds row i-1 (not yet overwritten); O(1)
                d[t] = d[t - m.time] + m.score   # O(1)
    return Result("DP (vector)", d[budget], [], operations)  # O(1)


def dp_memoized(modules, budget):
    """Top-down: the paper's DFS + memoization of the states (i, remaining time).

    `operations` = number of distinct states actually computed (<= n·(T+1)).
    Each state is computed once in O(1) (dictionary operations are O(1) on average), so:
        best case  Θ(n)    - no module fits: only states (0,T), (1,T), ..., (n-1,T) are reached.
        worst case O(n·T)  - every state (i, t) is reachable.
    Unlike the bottom-up table, it only computes the states that are actually reachable.
    """
    n = len(modules)                                                 # O(1)
    sys.setrecursionlimit(max(sys.getrecursionlimit(), n + 100))     # O(1): recursion depth is n + 1
    memo = {}                                                        # O(1); grows to at most n·(T+1) entries

    def best(i, t):
        if i == n:                                                   # base case; O(1)
            return 0
        if (i, t) in memo:                                           # cache hit: O(1) average
            return memo[(i, t)]
        answer = best(i + 1, t)                                      # "skip" subproblem
        w = modules[i].time                                          # O(1)
        if w <= t:                                                   # O(1)
            answer = max(answer, best(i + 1, t - w) + modules[i].score)  # "take" subproblem; O(1) besides the call
        memo[(i, t)] = answer                                        # O(1) average
        return answer
    # Each distinct state does O(1) work outside its (at most 2) recursive calls, and every
    # repeated call is answered from the cache in O(1): total = O(number of states) = O(n·T).

    value = best(0, budget)                       # O(n·T) worst, Θ(n) best
    chosen = []                                   # O(1)
    t = budget                                    # O(1)
    for i in range(n):                            # reconstruction: n iterations
        if best(i, t) != best(i + 1, t):          # both states are already in the cache -> O(1)
            chosen.append(i)                      # amortized O(1)
            t -= modules[i].time                  # O(1)
    return Result("DP (memoized)", value, chosen, len(memo))  # O(1)
