# Learning Paths: 0/1 Knapsack (DP) vs. the Paper's DFS vs. Greedy

Final Project for Design and Complexity of Algorithms (UnB).

## Structure
```
algorithms/               # ALGORITHM files (one module per algorithm)
  model.py                # LearningModule, Result, validation
  sorting.py              # hand-written merge sort (used by greedy and B&B)
  dfs.py                  # exhaustive DFS with pruning + backtracking (the paper's algorithm, knapsack version)
  graph_dfs.py            # DFS over the prerequisite graph (RUTICO style, extra)
  dp.py                   # DP: table (with reconstruction), vector (Θ(T) space) and memoized
  greedy.py               # greedy by score/time + max(greedy, best single module)
  branch_and_bound.py     # extra comparison: B&B with a fractional bound
  meet_in_the_middle.py   # extra comparison: Horowitz–Sahni, Θ(2^(n/2))
  fptas.py                # extra comparison: (1-ε)-approximation
instances.py              # generators (uncorrelated / weakly / strongly correlated)
experiment.py             # EXPERIMENT file: test instance + 8 experiment blocks
results/                  # CSVs, plots (PNG) and the full output of one run
report/                   # the paper: report.pdf (final), report.tex + sections/ (editable LaTeX source),
                          # figures/, make_tables.py (regenerates the tables from results/*.csv)
```

## How to run (Python 3.10+; matplotlib only for the plots)
```
pip install matplotlib
python experiment.py                  # everything (~1 min)
python experiment.py --quick          # reduced version
python experiment.py --only demo correctness
```
Blocks: demo, correctness, time, scale, quality, pseudo, families, fptas, graph.

## Note
Understand and rewrite the code with your own structure and naming before submitting
(automatic plagiarism checker), and every group member must be able to explain every file.
Check the course policy on AI tools and disclose its use if required.

## Report
`report/report.pdf` is the final paper. To edit it (member names are on the cover page and in the
Members section), change `report/report.tex` and `report/sections/*.tex` and run `pdflatex report.tex` twice
inside `report/`. After re-running the experiments, run `python report/make_tables.py` to refresh the tables.
