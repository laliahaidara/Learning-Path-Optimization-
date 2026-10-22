"""Generates the LaTeX tables of the report directly from results/*.csv (no manual transcription)."""
import csv, math, os

RES = os.path.join(os.path.dirname(__file__), "..", "results")
OUT = os.path.join(os.path.dirname(__file__), "sections")


def load(name):
    return list(csv.DictReader(open(os.path.join(RES, name), encoding="utf-8")))


def write(name, lines):
    open(os.path.join(OUT, name), "w", encoding="utf-8").write("\n".join(lines) + "\n")


def i(x):  # integer with thousands separator
    return f"{int(round(float(x))):,}"


def pct(x):
    return f"{100 * float(x):.1f}\\%"


# ---- DFS growth (Section 6.3)
rows = load("exponential_time.csv")
def cell(scn, n, alg, col):
    return [r[col] for r in rows if r["scenario"].startswith(scn) and int(r["n"]) == n and r["algorithm"] == alg][0]
L = ["\\begin{tabular}{@{}r r r r r r r r@{}}", "\\toprule",
     " & \\multicolumn{3}{c}{Worst case ($T=\\sum w_i$)} & \\multicolumn{4}{c}{Average case ($T=50\\%$ of $\\sum w_i$, 5 instances)}\\\\",
     "\\cmidrule(lr){2-4}\\cmidrule(lr){5-8}",
     "$n$ & DFS nodes & $2^{n+1}-1$ & DFS time (s) & DFS nodes & B\\&B ops & MITM ops & DP ops\\\\", "\\midrule"]
for n in sorted({int(r["n"]) for r in rows}):
    L.append(f"{n} & {i(cell('worst', n, 'DFS', 'operations'))} & {i(2 ** (n + 1) - 1)} & "
             f"{float(cell('worst', n, 'DFS', 'time_s')):.4f} & {i(cell('average', n, 'DFS', 'operations'))} & "
             f"{i(cell('average', n, 'B&B', 'operations'))} & {i(cell('average', n, 'MITM', 'operations'))} & "
             f"{i(cell('average', n, 'DP', 'operations'))}\\\\")
L += ["\\bottomrule", "\\end{tabular}"]
write("tab_dfs.tex", L)

# ---- scale (Section 6.4)
rows = load("scale.csv")
L = ["\\begin{tabular}{@{}r r r r r r r r@{}}", "\\toprule",
     "$n$ & $T$ & DP ops $=n(T+1)$ & DP time (s) & DP-vector (s) & Greedy ops & Greedy ops$/(n\\log_2 n)$ & Greedy (s)\\\\", "\\midrule"]
for n in sorted({int(r["n"]) for r in rows}):
    g = {r["algorithm"]: r for r in rows if int(r["n"]) == n}
    assert int(g["DP"]["operations"]) == int(g["DP"]["n_times_T"])
    ratio = int(g["Greedy"]["operations"]) / (n * math.log2(n))
    L.append(f"{n} & {i(g['DP']['T'])} & {i(g['DP']['operations'])} & {float(g['DP']['time_s']):.4f} & "
             f"{float(g['DP-vector']['time_s']):.4f} & {i(g['Greedy']['operations'])} & {ratio:.2f} & {float(g['Greedy']['time_s']):.4f}\\\\")
L += ["\\bottomrule", "\\end{tabular}"]
write("tab_scale.tex", L)

# ---- pseudo-polynomial (Section 6.5)
rows = load("pseudopolynomial.csv")
L = ["\\begin{tabular}{@{}r r r r r r r r@{}}", "\\toprule",
     "Factor & $T$ & DP ops & DP time (s) & DFS ops & B\\&B ops & MITM ops & Greedy ops\\\\", "\\midrule"]
for f in sorted({int(r["factor"]) for r in rows}):
    g = {r["algorithm"]: r for r in rows if int(r["factor"]) == f}
    L.append(f"$\\times{f}$ & {i(g['DP']['T'])} & {i(g['DP']['operations'])} & {float(g['DP']['time_s']):.4f} & "
             f"{i(g['DFS']['operations'])} & {i(g['B&B']['operations'])} & {i(g['MITM']['operations'])} & {i(g['Greedy']['operations'])}\\\\")
L += ["\\bottomrule", "\\end{tabular}"]
write("tab_pseudo.tex", L)

# ---- greedy quality (Section 6.6)
rows = load("greedy_quality.csv")
names = {"uncorrelated": "Uncorrelated", "weakly_correlated": "Weakly corr.", "strongly_correlated": "Strongly corr."}
L = ["\\begin{tabular}{@{}r l r r r r@{}}", "\\toprule",
     "$n$ & Family & Greedy mean gap & Greedy max gap & Greedy+item mean & Greedy+item max\\\\", "\\midrule"]
for n in (8, 15, 30, 60):
    for fam in names:
        r = [x for x in rows if int(x["n"]) == n and x["family"] == fam and float(x["budget_ratio"]) == 0.3][0]
        L.append(f"{n} & {names[fam]} & {pct(r['greedy_mean_gap'])} & {pct(r['greedy_max_gap'])} & "
                 f"{pct(r['greedy_item_mean_gap'])} & {pct(r['greedy_item_max_gap'])}\\\\")
    if n != 60:
        L.append("\\midrule")
L += ["\\bottomrule", "\\end{tabular}"]
write("tab_quality.tex", L)

L = ["\\begin{tabular}{@{}r l r r r r@{}}", "\\toprule",
     "$n$ & Family & Greedy mean gap & Greedy max gap & Greedy+item mean & Greedy+item max\\\\", "\\midrule"]
for n in (8, 15):
    for fam in names:
        r = [x for x in rows if int(x["n"]) == n and x["family"] == fam and float(x["budget_ratio"]) == 0.1][0]
        L.append(f"{n} & {names[fam]} & {pct(r['greedy_mean_gap'])} & {pct(r['greedy_max_gap'])} & "
                 f"{pct(r['greedy_item_mean_gap'])} & {pct(r['greedy_item_max_gap'])}\\\\")
    if n != 15:
        L.append("\\midrule")
L += ["\\bottomrule", "\\end{tabular}"]
write("tab_quality_item.tex", L)

# ---- exact by family (Section 6.7)
rows = load("exact_by_family.csv")
L = ["\\begin{tabular}{@{}l r r r r r@{}}", "\\toprule",
     "Family & $n$ & B\\&B mean & B\\&B max & MITM & DP\\\\", "\\midrule"]
for fam in ("uncorrelated", "strongly_correlated"):
    for r in [x for x in rows if x["family"] == fam]:
        L.append(f"{names[fam]} & {r['n']} & {i(r['bb_mean'])} & {i(r['bb_max'])} & {i(r['mitm_mean'])} & {i(r['dp_mean'])}\\\\")
    if fam == "uncorrelated":
        L.append("\\midrule")
L += ["\\bottomrule", "\\end{tabular}"]
write("tab_families.tex", L)

# ---- FPTAS (Section 6.8)
rows = load("fptas.csv")
L = ["\\begin{tabular}{@{}l r r r r@{}}", "\\toprule",
     "Algorithm & $\\varepsilon$ & Score & Score / optimum & Operations\\\\", "\\midrule"]
for r in rows:
    eps = "---" if r["epsilon"] == "0" else r["epsilon"]
    L.append(f"{r['algorithm']} & {eps} & {r['value']} & {float(r['ratio_to_optimum']):.4f} & {i(r['operations'])}\\\\")
L += ["\\bottomrule", "\\end{tabular}"]
write("tab_fptas.tex", L)

# ---- graph DFS (Section 6.9)
rows = load("graph_dfs.csv")
L = ["\\begin{tabular}{@{}r " + "r" * len(rows) + "@{}}", "\\toprule",
     "$n$ & " + " & ".join(r["n"] for r in rows) + "\\\\", "\\midrule",
     "Paths generated & " + " & ".join(i(r["paths"]) for r in rows) + "\\\\",
     "$2^{n-1}$ & " + " & ".join(i(r["2^(n-1)"]) for r in rows) + "\\\\", "\\bottomrule", "\\end{tabular}"]
write("tab_graph.tex", L)
print("tables written")
