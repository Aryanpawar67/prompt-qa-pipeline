"""Regression gate: compare the latest promptfoo results with baseline.json.

Exit codes: 0 = no regression, 1 = regression detected, 2 = bad usage or missing input.

Usage:
  python3 scripts/check_regression.py reports/results.json --prompt v2
  python3 scripts/check_regression.py reports/results.json --prompt v2 --update-baseline --confirm UPDATE
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from summarize import pass_rates  # noqa: E402

CONFIRM_WORD = "UPDATE"


def rates_for(results_path, prompt):
    """Return {category: (passed, total)} for one prompt label in a results file."""
    counts = pass_rates(results_path)
    if prompt is None:
        if len(counts) != 1:
            raise SystemExit(f"error: results contain prompts {sorted(counts)}; choose one with --prompt")
        prompt = next(iter(counts))
    if prompt not in counts:
        raise SystemExit(f"error: prompt '{prompt}' not in results (found {sorted(counts)})")
    return prompt, {c: tuple(v) for c, v in counts[prompt].items()}


def overall(cats):
    passed = sum(p for p, _ in cats.values())
    total = sum(t for _, t in cats.values())
    return passed, total


def pct(passed, total):
    return 100.0 * passed / total if total else 0.0


def compare(current, baseline_cats, max_overall_drop, max_category_drop):
    """Return (list of problem strings, list of report lines). Drops are in percentage points."""
    problems, lines = [], []
    cp, ct = overall(current)
    bp, bt = overall({c: (v["passed"], v["total"]) for c, v in baseline_cats.items()})
    drop = round(pct(bp, bt) - pct(cp, ct), 1) + 0.0
    lines.append(f"overall: baseline {pct(bp, bt):.1f}% -> current {pct(cp, ct):.1f}% (change {-drop + 0.0:+.1f} pts)")
    if drop > max_overall_drop:
        problems.append(f"overall pass rate dropped {drop:.1f} pts (limit {max_overall_drop})")

    for cat in sorted(set(current) | set(baseline_cats)):
        if cat not in current:
            problems.append(f"category '{cat}' is in the baseline but missing from the results")
            continue
        p, t = current[cat]
        if cat not in baseline_cats:
            lines.append(f"{cat}: new category, {p}/{t} (not in baseline)")
            continue
        b = baseline_cats[cat]
        d = round(pct(b["passed"], b["total"]) - pct(p, t), 1) + 0.0
        flag = ""
        if d > max_category_drop:
            flag = "  <-- REGRESSION"
            problems.append(f"category '{cat}' dropped {d:.1f} pts (limit {max_category_drop})")
        lines.append(f"{cat}: baseline {b['passed']}/{b['total']} -> current {p}/{t} (change {-d + 0.0:+.1f} pts){flag}")
    return problems, lines


def write_baseline(path, prompt, current):
    data = {
        "prompt": prompt,
        "categories": {c: {"passed": p, "total": t} for c, (p, t) in sorted(current.items())},
    }
    Path(path).write_text(json.dumps(data, indent=2) + "\n")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("results", help="promptfoo results JSON")
    ap.add_argument("--baseline", default="baseline.json")
    ap.add_argument("--prompt", help="prompt label to check (needed if results hold several prompts)")
    ap.add_argument("--max-overall-drop", type=float, default=5.0, help="allowed overall drop in pct points")
    ap.add_argument("--max-category-drop", type=float, default=15.0, help="allowed per-category drop in pct points")
    ap.add_argument("--update-baseline", action="store_true", help="overwrite the baseline with these results")
    ap.add_argument("--confirm", help=f"must be '{CONFIRM_WORD}' to allow --update-baseline")
    args = ap.parse_args(argv)

    try:
        prompt, current = rates_for(args.results, args.prompt)
    except FileNotFoundError:
        print(f"error: results file not found: {args.results}", file=sys.stderr)
        return 2
    except SystemExit as e:
        print(e, file=sys.stderr)
        return 2

    if args.update_baseline:
        if args.confirm != CONFIRM_WORD:
            print(f"error: --update-baseline needs --confirm {CONFIRM_WORD}", file=sys.stderr)
            return 2
        write_baseline(args.baseline, prompt, current)
        p, t = overall(current)
        print(f"baseline written to {args.baseline} from prompt '{prompt}': {p}/{t} ({pct(p, t):.1f}%)")
        return 0

    if not Path(args.baseline).exists():
        print(f"error: {args.baseline} not found. Create it with --update-baseline --confirm {CONFIRM_WORD}", file=sys.stderr)
        return 2
    baseline = json.loads(Path(args.baseline).read_text())

    problems, lines = compare(current, baseline["categories"], args.max_overall_drop, args.max_category_drop)
    print(f"Regression check: prompt '{prompt}' vs baseline from '{baseline['prompt']}'")
    for line in lines:
        print("  " + line)
    if problems:
        print("\nFAIL: quality regressed")
        for p in problems:
            print("  - " + p)
        return 1
    print("\nOK: no regression")
    return 0


if __name__ == "__main__":
    sys.exit(main())
