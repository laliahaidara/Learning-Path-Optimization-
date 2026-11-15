"""DFS over the prerequisite graph, RUTICO style (optional/extra part of the project).

Enumerates every simple path starting at the source whose total time fits the budget and
returns the one with the highest score. Here there is precedence (edges), unlike 0/1 knapsack.

Technique: graph search (depth-first) with backtracking.

Complexity summary (P = number of paths generated, d = out-degree, L = path length <= n):
    each generated path costs O(d·L) for the successor loop (`nxt not in path` is a linear
    scan of the path) plus an O(L) copy when the best path improves.
    best case    Θ(1)            - the source alone does not fit the budget.
    worst case   O(n²·2^n)       - complete DAG with every time fitting: P = 2^(n-1) paths,
                                   each with up to n successors scanned against a path of up to n
                                   nodes. The number of paths alone is Θ(2^n), which is what the
                                   experiments count.
    space        Θ(n)            - recursion depth and `path` hold at most n nodes.
"""


def dfs_paths(successors, times, scores, source, budget):
    """Returns (best_score, best_path, number_of_paths_generated)."""
    best_score, best_path, generated = -1, [], 0   # O(1)
    path = []                                       # O(1): current path (max n nodes)

    def visit(node, used_time, score):              # each call generates one path
        nonlocal best_score, best_path, generated
        path.append(node)                           # amortized O(1)
        used_time += times[node]                    # O(1)
        score += scores[node]                       # O(1)
        generated += 1                              # O(1)
        if score > best_score:                      # O(1)
            best_score, best_path = score, list(path)  # O(L) copy, only when the best improves
        for nxt in successors.get(node, []):        # d iterations (d = out-degree of `node`)
            if nxt not in path and used_time + times[nxt] <= budget:  # O(L) list scan + O(1) test
                visit(nxt, used_time, score)        # recursive call: one more path
        path.pop()  # backtracking (a detail the paper's pseudocode does not show); O(1)

    if times[source] <= budget:                     # O(1)
        visit(source, 0, 0)                         # whole search: P calls
    return best_score, best_path, generated         # O(1)


def complete_dag(n):
    """Worst case: an edge from i to every j > i. From node 0 there are 2^(n-1) paths.

    Complexity: Θ(n²) time and space (n(n-1)/2 edges are stored).
    """
    return {i: list(range(i + 1, n)) for i in range(n)}  # Σ (n - i - 1) = n(n-1)/2 -> Θ(n²)
