---
name: credtr-ai-portfolio-diagnosis
description: Analyze uploaded synthetic Credtr.ai account-month CSV data with reproducible Python checks for monthly delinquency, cohorts, duplicate keys, and denominators.
---
# Credtr.ai portfolio diagnosis

Use this skill when the user asks for portfolio events, trends, cohort comparisons, data integrity, or risk-factor associations in the **synthetic Credtr.ai dataset**.

## Required evidence
- Data: `data/synthetic_account_months.csv` in this repository (regenerate with `python -m src.pipeline`), or a copy the user attaches. If neither is available, ask for it.
- Run this skill's script with Python 3 (standard library only), from the repository root:
  `python .claude/skills/credtr-ai-portfolio-diagnosis/scripts/verify.py --data data/synthetic_account_months.csv`
- Do not guess paths; list the actual files first. If the script cannot run, reproduce its algorithm directly and say so. Never invent execution.

## Calculation conventions
- Target: `dpd30_next_60d` means an account-month's **30+ days-past-due event within the next 60 days**, not default, charge-off, or causal result.
- Full-data row count = account-month observations; distinct `account_id` count = unique accounts.
- Treat test reporting window as 2024-12 through 2025-03 inclusive only where relevant; do not conflate with model's true train/validation/test split unless source explicitly confirms it.
- Monthly event rate = number of event rows / number of snapshot rows that month.
- Cohort comparisons use the exact same reporting window and denominator.
- Different months for one account are repeated observations, not independent customers.
- Calculated associations are descriptive. Never describe them as causal.
- Output month counts, cohort event counts and rates, denominator and data-quality flags.

## Output format
1. Concise answer to the user question.
2. Evidence table (month or cohort, observations, events, event rate).
3. Source filename, snapshot range, row-level denominator, method, and whether code ran.
4. Key limitations, especially synthetic data and repeated account observations.
5. **Do not** claim model ROC AUC, PR AUC, or intervention savings from the raw CSV; scored predictions and causal evidence are not available here.

## Benchmark protocol
For timing tests: ask for one question at a time, record elapsed wall-clock time from submission to verified answer, and compare with an unaided session with the same file and tools. Avoid copying a correct answer from one session to the other. Keep review and correction times separate.
