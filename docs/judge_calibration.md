# Judge calibration

Goal: check whether the LLM judge (`JUDGE_MODEL`, rubrics in `promptfooconfig.yaml`) agrees with a human reader.

## Method
- `scripts/make_calibration_set.py` picked 10 replies from real eval runs: every reply the judge failed (3 of them),
  plus passing replies from the trickier categories, shuffled. The set is small and was chosen to include judge failures,
  so the agreement figure is not an estimate of accuracy on live traffic.
- The human label is `pass` or `fail`: would this reply pass **all** of accuracy (claims supported by the KB),
  tone, and policy compliance? That is what the judge's three rubrics check together.
- The human labels first, without seeing the judge's verdicts (they are stored separately in `tests/judge_verdicts.csv`).

## Status
**Not yet labelled.** Fill in `human_label` and `human_reason` in `tests/human_labels.csv`, then run:

```bash
python3 scripts/judge_agreement.py
```

## Results
_To be completed after labelling. Paste the agreement percentage and the list of disagreements here, with a short
explanation of each (judge too strict, judge too lenient, or ambiguous rubric). Do not round up or drop disagreements._
