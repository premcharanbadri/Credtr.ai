# Executive decision memo | RiskPulse AI

**Prepared for:** Head of Credit Risk Strategy / Product & Customer Operations  
**Decision requested:** Approve governed shadow evaluation and design an ethical supportive-outreach experiment. **Do not approve automated portfolio actions or claim savings.**

## Decision headline
A synthetic, temporally evaluated account-risk system demonstrates the analytical workflow for identifying emerging delinquency risk, but the more complex AI challenger **does not outperform** a simpler logistic regression on the final untouched test period. Moreover, a monthly greedy value-first outreach policy is **not superior** to simpler risk-first selection under a 60-day contact cooldown, even though value-based ranking looks appealing in a single month.

That is a decision-making success: the framework identifies when added model or optimization complexity is not justified.

## Scope and evaluation
- 57,000 synthetic account-month snapshots, drawn from 3,800 recurring synthetic account identifiers, Jan 2024–Mar 2025.
- Target = 30+ DPD within the following 60 days; **not default PD**.
- Training Jan–Sep 2024; calibration Oct–Nov 2024; untouched out-of-time test Dec 2024–Mar 2025.
- Model selected using validation PR AUC; evaluate only once on final temporal test.

| Model | Test ROC AUC | Test PR AUC | Brier | Top 10% event capture |
|---|---:|---:|---:|---:|
| Simple risk rules | 0.7561 | 0.3055 | 0.0839 | 36.19% |
| Logistic regression | **0.8038** | **0.3930** | **0.0797** | **39.73%** |
| Gradient boosting (validation-selected) | 0.7997 | 0.3889 | 0.0800 | 39.06% |

The booster won *validation* PR AUC only slightly (0.4174 vs 0.4160). The final holdout does not support complexity for its own sake. Avoid retuning to this holdout; schedule a new holdout or shadow period to decide a future challenger.

## Economic scenario — NOT realized loss savings
Base assumptions: 25% conditional progression to eventual loss, 70% LGD, 16% relative risk mitigation **if a helpful outreach action proves effective**, $7 operational cost and $1.50 customer friction allowance per attempt, up to 650 contacts per month, 60-day per-account cooldown and opt-out/dispute/recency protections.

| Greedy monthly policy | Contact events, four months | Modeled four-month net value |
|---|---:|---:|
| Random eligible | 2,338 | $56,817 |
| Highest predicted risk | 2,341 | **$60,533** |
| Highest immediate scenario net value | 2,329 | $60,377 |

The approximately **$155 difference** between risk-first and greedy value-first is economically immaterial and sensitive to assumptions. It occurs because selecting an account now changes future availability due to repeat-contact controls. A rolling-horizon, forecast-based optimizer would need to use **only information available at the time**, not future realized snapshots.

If the 16% assumed outreach effect were actually **0%**, the policy has costs but no modeled benefit. The financial model is therefore **not proof of return on investment**. Accounting loss provisions and realized cash collections are different from this educational risk-weighted proxy.

## Recommended management actions
1. **Do not deploy an AI challenger automatically.** Subject the logistic benchmark and challenger to independent approval; obtain new out-of-time production-like evidence.
2. **Shadow-test with no adverse customer actions.** Measure calibration, top-N recall, false positives, workload, drift, and policy adherence.
3. **Pre-register a risk-approved randomized outreach trial.** Evaluate causal incremental results; do not withhold mandatory support or legally required communications.
4. **Favor operationally feasible policies.** Enforce no-repeat controls, capacity and consent, and compare rules, risk-first, and value-first on *actual* incremental benefit.
5. **Scale or stop by evidence.** Require statistically and economically credible improvements after costs, with zero compliance breaches and human governance.

## Leadership/communication angle
> “My initial hypothesis was that a more complex machine-learning model and value-based targeting would beat simpler strategies. Rigorous temporal evaluation challenged both assumptions. Rather than defend complexity, I recommended holding the launch, validating the baseline and testing the actual customer benefit before scaling.”

This is an **illustrative interview case**, not a script to claim real professional outcomes.
