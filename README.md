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
| out-of-scope | 3/3 (100%) | 3/3 (100%) |
| personal-data | 2/2 (100%) | 2/2 (100%) |
| prompt-injection | 3/3 (100%) | 3/3 (100%) |
| refund-billing | 4/4 (100%) | 4/4 (100%) |
| upset-customer | 1/3 (33%) | 3/3 (100%) |
| overall | 20/22 (91%) | 22/22 (100%) |

Notes:
- This is the second run. The first run (original rubrics) scored v1 20/22 and v2 19/22. In 3 of its 5 failures the judge's
  explanation contradicted its own fail verdict, so the tone and accuracy rubrics were tightened: tone only demands an apology
  when the message itself shows anger or complaints, and accuracy no longer fails a reply for omissions.
- v1's two failures: a reply over the 1200-character limit, and a tone fail on an upset customer (opening was "I understand this is stressful", with no apology).
- Single run on a small synthetic set. Replies are not fully deterministic even at temperature 0, so differences of one case are not meaningful.
