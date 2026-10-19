"""DFS over the prerequisite graph, RUTICO style (optional/extra part of the project).

Enumerates every simple path starting at the source whose total time fits the budget and
returns the one with the highest score. Here there is precedence (edges), unlike 0/1 knapsack.
"""


def dfs_paths(successors, times, scores, source, budget):
    """Returns (best_score, best_path, number_of_paths_generated)."""
    best_score, best_path, generated = -1, [], 0
    path = []

    def visit(node, used_time, score):
        nonlocal best_score, best_path, generated
        path.append(node)
        used_time += times[node]
        score += scores[node]
        generated += 1
        if score > best_score:
            best_score, best_path = score, list(path)
        for nxt in successors.get(node, []):
            if nxt not in path and used_time + times[nxt] <= budget:
                visit(nxt, used_time, score)
        path.pop()  # backtracking (a detail the paper's pseudocode does not show)

    if times[source] <= budget:
        visit(source, 0, 0)
    return best_score, best_path, generated


def complete_dag(n):
    """Worst case: an edge from i to every j > i. From node 0 there are 2^(n-1) paths."""
    return {i: list(range(i + 1, n)) for i in range(n)}
