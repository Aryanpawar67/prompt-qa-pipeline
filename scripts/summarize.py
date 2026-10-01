"""Print pass rate per category for each prompt version from a promptfoo results JSON.

Usage: python3 scripts/summarize.py reports/results.json [--markdown]
Only reports numbers that are in the results file.
"""
import json
import sys
from collections import defaultdict


def pass_rates(path):
    """Return {prompt_label: {category: (passed, total)}} from a promptfoo results file."""
    data = json.load(open(path))
    results = data["results"]["results"]
    labels = [p.get("label", p["id"]) for p in data["config"]["prompts"]]
    counts = defaultdict(lambda: defaultdict(lambda: [0, 0]))
    for r in results:
        label = labels[r["promptIdx"]]
        category = r["testCase"]["metadata"]["category"]
        counts[label][category][1] += 1
        counts[label][category][0] += 1 if r["success"] else 0
    return counts


def main():
    path = sys.argv[1]
    markdown = "--markdown" in sys.argv
    counts = pass_rates(path)
    labels = sorted(counts)
    categories = sorted({c for l in labels for c in counts[l]})

    def cell(label, category):
        p, t = counts[label][category] if category in counts[label] else (0, 0)
        return f"{p}/{t} ({100 * p / t:.0f}%)" if t else "-"

    rows = [["category"] + labels]
    for c in categories:
        rows.append([c] + [cell(l, c) for l in labels])
    totals = []
    for l in labels:
        p = sum(v[0] for v in counts[l].values())
        t = sum(v[1] for v in counts[l].values())
        totals.append(f"{p}/{t} ({100 * p / t:.0f}%)")
    rows.append(["overall"] + totals)

    if markdown:
        print("| " + " | ".join(rows[0]) + " |")
        print("|" + "---|" * len(rows[0]))
        for row in rows[1:]:
            print("| " + " | ".join(row) + " |")
    else:
        widths = [max(len(r[i]) for r in rows) for i in range(len(rows[0]))]
        for row in rows:
            print("  ".join(v.ljust(w) for v, w in zip(row, widths)))


if __name__ == "__main__":
    main()
