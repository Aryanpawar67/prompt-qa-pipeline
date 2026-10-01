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

_Not yet generated. Run `npm run eval`, then `python3 scripts/summarize.py reports/results.json --markdown`
and paste the table here. Only numbers from a real run go in this section._
