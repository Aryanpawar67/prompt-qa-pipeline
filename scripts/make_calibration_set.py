"""Build the judge-calibration set from existing eval results (no API calls).

Writes:
  tests/human_labels.csv     outputs for a human to label (judge verdict NOT included, to avoid bias)
  tests/judge_verdicts.csv   the judge's verdict for the same ids (open only after labelling)

Selection: every reply the judge failed, plus passing replies from the tricky categories, shuffled with a fixed seed.
Run: python3 scripts/make_calibration_set.py reports/results.json reports/results_v3.json
"""
import csv
import json
import random
import sys

TRICKY = ["upset-customer", "personal-data", "prompt-injection", "not-in-kb", "out-of-scope", "refund-billing", "how-to-product"]
N = 10


def judge_rows(path):
    data = json.load(open(path))
    labels = [p if isinstance(p, str) else p.get("label", p["id"]) for p in data["config"]["prompts"]]
    for r in data["results"]["results"]:
        rubrics = [c for c in r["gradingResult"]["componentResults"] if c["assertion"]["type"] == "llm-rubric"]
        failed = [c for c in rubrics if not c["pass"]]
        yield {
            "source": f"{path}:{labels[r['promptIdx']]}",
            "category": r["testCase"]["metadata"]["category"],
            "question": r["vars"]["question"] if "vars" in r else r["testCase"]["vars"]["question"],
            "output": r["response"]["output"],
            "judge": "fail" if failed else "pass",
            "judge_reason": " | ".join(f"{c['assertion']['metric']}: {c.get('reason', '')}" for c in failed),
        }


def main(paths):
    rows = [row for p in paths for row in judge_rows(p)]
    chosen = [r for r in rows if r["judge"] == "fail"]
    seen = {r["category"] for r in chosen}
    passes = [r for r in rows if r["judge"] == "pass"]
    random.Random(7).shuffle(passes)
    for cat in TRICKY:  # one passing reply per category first, then fill up
        if len(chosen) >= N:
            break
        pick = next((r for r in passes if r["category"] == cat and r not in chosen), None)
        if pick:
            chosen.append(pick)
    for r in passes:
        if len(chosen) >= N:
            break
        if r not in chosen:
            chosen.append(r)
    random.Random(11).shuffle(chosen)

    with open("tests/human_labels.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "category", "question", "output", "human_label", "human_reason"])
        for i, r in enumerate(chosen, 1):
            w.writerow([i, r["category"], r["question"], r["output"], "", ""])
    with open("tests/judge_verdicts.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "source", "judge_verdict", "judge_reason"])
        for i, r in enumerate(chosen, 1):
            w.writerow([i, r["source"], r["judge"], r["judge_reason"]])
    print(f"wrote {len(chosen)} rows; judge fails included: {sum(r['judge'] == 'fail' for r in chosen)}")


if __name__ == "__main__":
    main(sys.argv[1:] or ["reports/results.json", "reports/results_v3.json"])
