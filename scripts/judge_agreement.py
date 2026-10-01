"""Compare LLM-judge verdicts with human labels.

Usage: python3 scripts/judge_agreement.py [human_labels.csv] [judge_verdicts.csv]
Human label = "pass" or "fail": would this reply pass ALL of accuracy, tone and policy compliance
(the same three rubrics the judge uses; see promptfooconfig.yaml)?
"""
import csv
import sys


def load(path, key):
    with open(path, newline="") as f:
        return {row["id"]: row for row in csv.DictReader(f)}


def main(human_path="tests/human_labels.csv", judge_path="tests/judge_verdicts.csv"):
    human, judge = load(human_path, "id"), load(judge_path, "id")
    unlabeled = [i for i, r in human.items() if r["human_label"].strip().lower() not in ("pass", "fail")]
    if unlabeled:
        print(f"error: human_label must be 'pass' or 'fail'; missing or invalid for ids: {', '.join(unlabeled)}", file=sys.stderr)
        return 2

    agree, disagreements = 0, []
    both = {("pass", "pass"): 0, ("pass", "fail"): 0, ("fail", "pass"): 0, ("fail", "fail"): 0}
    for i, h in human.items():
        hl, jl = h["human_label"].strip().lower(), judge[i]["judge_verdict"]
        both[(hl, jl)] += 1
        if hl == jl:
            agree += 1
        else:
            disagreements.append((i, h, judge[i], hl, jl))

    n = len(human)
    print(f"Agreement: {agree}/{n} = {100 * agree / n:.0f}%")
    print("(human, judge) counts: " + ", ".join(f"{k[0]}/{k[1]}={v}" for k, v in both.items()))
    if disagreements:
        print(f"\nDisagreements ({len(disagreements)}):")
        for i, h, j, hl, jl in disagreements:
            print(f"\n[id {i}] category={h['category']} human={hl} judge={jl}")
            print(f"  question: {h['question']}")
            print(f"  human reason: {h['human_reason']}")
            print(f"  judge reason: {j['judge_reason'] or '(judge passed it)'}")
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:3]))
