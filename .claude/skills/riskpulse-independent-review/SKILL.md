---
name: riskpulse-independent-review
description: Critically review RiskPulse synthetic credit-analytics reports for misleading accuracy claims, leakage, missing evidence, denominator mistakes, and unsupported savings claims.
---
# Independent review of RiskPulse analytical answers

Use when the user requests a second-pass review, challenge, audit, or critique of portfolio analysis, risk-model metrics, outreach strategy, financial scenarios, or executive recommendations.

1. Distinguish **verified source calculations** from **reported-but-not-reproduced model metrics**, **hypothetical assumptions**, and **unsupported claims**.
2. Require calculation period and unit (unique accounts vs account-months) for every metric.
3. Reject statements that ROC AUC is classification accuracy or that 30+ DPD is default probability.
4. Flag data leakage if post-outcome fields or `dpd30_next_60d` become predictors.
5. Flag causal/realized-savings claims when outreach effectiveness or avoided loss is assumed, not observed experimentally.
6. Reject suggestions to autonomously change credit limits, APRs, approvals, or adverse decisions.
7. Check quoted dollar amounts against supplied files or Python outputs rather than inferring from the project description.
8. Do not invent results from missing scored model outputs. Note uncertainty when evidence is absent.
9. Deliver `Review verdict: PASS / PASS WITH QUALIFICATIONS / FAIL`, precise issues, their severity, corrections, and final accepted wording.

For a blinded evaluation, review the analyst answer without any hidden answer-key information; compare with independent calculations only after the first verdict is recorded.
