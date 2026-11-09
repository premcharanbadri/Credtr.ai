# Intervention experiment and governance

## Causal design
Do NOT call the modeled outreach value a realized loss saving. The credit model predicts untreated (observational, synthetic) delinquency propensity, not treatment uplift.

1. Eligible and consenting/support-eligible portfolio defined in advance; separate any regulatory servicing obligation that cannot ethically be withheld.
2. Randomize approved outreach timing or style (e.g. standardized reminder vs additional informational assistance) when legally and ethically permitted. Never withhold mandatory notices or protected support.
3. Stratify randomization by risk decile, balance band, and snapshot month; cluster by account ID to avoid treating the same account as independent across months.
4. Primary outcomes: 30+DPD within 60 days and outreach cost per prevented case; secondary: repayment behavior, complaints, opt-out, hardship uptake, satisfaction, credit loss transitions if observable.
5. Pre-register sample size, effect size, eligible population, analysis intent-to-treat, duration, contact restrictions, early termination conditions.
6. Analyze difference in proportions and confidence intervals; estimate incremental cost/benefit including operational capacity, customer effects, and long-run outcomes.

## Statistical precision illustration
At event rate 20% and target **3 percentage point absolute reduction**, a simple unadjusted two-sided 5%-alpha, 80%-power two-arm test needs roughly ~2,500 cases per arm (normal approximation). Actual sample depends on baseline, loss to follow-up, account clustering, treatment non-compliance, and ethical review.

## Governance checklist
- Business product owner, risk model owner, independent validator, legal/compliance sign-off, servicing owner, data steward.
- Consent/opt-out and frequency constraints; no automated adverse credit decisions.
- Legal basis, data minimization, security, synthetic-only public demonstration.
- Feature representativeness, proxy fairness, review of lawful purposes and protected-group monitoring by authorized personnel.
- Calibration drift threshold, missed-risk monitoring, incident escalation, versioning and rollback.
- Explicit distinction between ***30+ DPD***, ***default***, ***expected loss proxy*** and ***recognized accounting credit loss***.

## Regulatory context
UK PRA SS1/23's scope is defined for certain model-approval banks; its governance and validation principles are useful, but do not automatically apply in full to every financial firm or to this educational project.
