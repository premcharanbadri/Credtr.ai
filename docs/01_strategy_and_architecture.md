# RiskPulse AI | Strategy brief and architecture

## Executive problem
Portfolio risk leaders often respond to delinquency after missed-payment statuses show up in reports. They need an early-warning approach using behavior as of **today**, with traceable analytics and bounded operational workload.

## Decisions, not just prediction
1. Which behavior patterns provide a reliable leading signal of near-term delinquency?
2. Which prediction methods deliver incremental out-of-time performance and calibrated risk scores?
3. Which accounts can legitimately receive **supportive** outreach, given opt-out, contact-frequency, dispute, and team-capacity restrictions?
4. Is early outreach worth its cost under realistic best/base/worst assumptions, before launch?
5. How would a randomized pilot separate true incremental impact from observed correlation?

## Architecture
```text
SOURCE (simulated account-month snapshots) -> AS-OF VALIDATION AND FEATURE MART
        |                                                |
        +-- SQL cohort risk diagnostics                  +-- hypothesis tests
        |                                                |
        +-----------------------RISK MODELING-------------+
                                   |
                  Transparent rules | Logistic regression | Histogram gradient boosting
                                   |
                     Oct–Nov 2024 disjoint calibration
                                   |
                       Dec 2024–Mar 2025 time-held-out test
                                   |
                         Risk decile / calibration / drift
                                   |
                         POLICY / ECONOMIC SCENARIOS
                                   |
                   Consent + dispute + recency + 60-day cooldown + capacity
                                   |
                      Human-authorized support outreach
                                   |
                       Randomized pilot / monitoring
                                   |
                    Executive ROI + risk-governance dashboard
```

## Key hypotheses
- Utilization acceleration and payment-ratio deterioration are leading indicators above static balance levels.
- A gradient-boosted model may uncover interactions missed by logistic regression; advantage must be validated out of time.
- The highest-risk accounts are not necessarily the highest **expected impact per outreach dollar** because account exposure and action costs vary.
- More alerts are not inherently better: operations capacity and false positives impose tangible costs.
- A higher ROC AUC does not guarantee calibrated probabilities or positive expected value.

## Data and splits
- As-of account-month snapshots Jan 2024–Mar 2025; 3,800 synthetic recurring accounts.
- Train: Jan–Sep 2024; independent calibrator: Oct–Nov 2024; out-of-time final test: Dec 2024–Mar 2025. All target windows are hypothetical and assumed observable 60 days later.
- Only pre-snapshot features allowed. No target-derived indicators, leakage, personal identifiers or protected-characteristic columns.

## Quality and risk controls
- Group and measurement reporting should be independently reviewed for legally appropriate attributes and privacy constraints (not just exclude columns).
- Uncertain or disputed account states route to human review; no adverse-action automation.
- Monitor event prevalence, Brier/calibration, precision@capacity, top-decile capture, population stability, action costs, complaint rates, opt-outs, and policy drift.
- Model risk management: inventory, versioned data/assumptions, approvals, independent validation and rollback.

## Scale / stop gates (illustrative, to be agreed with policy owners)
- Model chosen only from validation periods, then inspected once on temporal test.
- Pilot must establish actual uplift by randomized controlled outreach; no business claim based only on assumed efficacy.
- Net benefit >0 across plausible sensitivity cases; policy adherence 100%; no material increase in complaints or harm.

## References
- UK PRA model risk management: https://www.bankofengland.co.uk/prudential-regulation/publication/2023/may/model-risk-management-principles-for-banks-ss
- NIST AI RMF Playbook: https://airc.nist.gov/airmf-resources/playbook/
- scikit-learn probability calibration: https://scikit-learn.org/stable/modules/calibration.html
