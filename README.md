# prompt-qa-pipeline

Prompt regression testing for a customer support bot ("Acme Cloud", fictional company, synthetic data).
Full documentation is written in Phase 9; see `PLAN.md` for the build plan.

## Run the v1 vs v2 comparison

```bash
npm install
cp .env.example .env      # add your ANTHROPIC_API_KEY and model names
npm run eval              # writes reports/results.json and reports/report.html
npm run view              # open the interactive results viewer
npm run summary           # pass rate per category for each prompt version
```

## Results: v1 vs v2

One live run, 22 cases per version, temperature 0, `ANTHROPIC_MODEL` = claude-sonnet-4-5, judge = claude-haiku-4-5-20251001
(from `reports/results.json`; a case passes only if all its assertions pass):

| category | v1 | v2 |
|---|---|---|
| how-to-product | 4/4 (100%) | 4/4 (100%) |
| not-in-kb | 3/3 (100%) | 3/3 (100%) |
| out-of-scope | 3/3 (100%) | 2/3 (67%) |
| personal-data | 1/2 (50%) | 2/2 (100%) |
| prompt-injection | 3/3 (100%) | 3/3 (100%) |
| refund-billing | 4/4 (100%) | 3/4 (75%) |
| upset-customer | 2/3 (67%) | 2/3 (67%) |
| overall | 20/22 (91%) | 19/22 (86%) |

Notes on this run (not yet tuned, single run, small synthetic set, so differences of one case are not meaningful):
- v2 did not beat v1 overall (19/22 vs 20/22). Its 3 failures were all LLM-judge verdicts.
- In at least 3 of the 5 failures the judge's own explanation contradicts its fail verdict (for example "polite and professional throughout" on a tone fail), so the judge is noisy. Phase 6 measures this against human labels.
- v1's failures were the 1200-character length check (twice) plus one judge verdict.
