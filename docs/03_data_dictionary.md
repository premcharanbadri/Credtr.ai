# Data dictionary (synthetic)

| Field | Meaning | Use |
|---|---|---|
| account_id | Synthetic stable account identifier | Experimental clustering only; never model feature |
| snapshot_month | When predictors are observed | Split / temporal reporting |
| utilization | Current outstanding balance / credit limit | Risk feature |
| util_change_3m | Synthetic recent utilization change | Risk feature |
| payment_to_balance | Recent payment / statement balance | Risk feature |
| payment_ratio_change | Recent movement in payment ratio | Risk feature |
| missed_payments_3m | Count of observed missed payments in previous three months | Risk feature |
| income_volatility | Simulated relative cash-flow instability | Hypothetical permitted-feature review required |
| balance_usd | Balance expressed in **USD equivalent** for scenario modeling | Feature and economic exposure |
| credit_limit_usd | Assumed credit line (USD equivalent) | EAD scenario only, not a predictor |
| months_on_book | Account tenure (months), NOT customer age | Model feature |
| promo_expiring_60d | Promotional offer nearing expiration | Model feature |
| revolver | Revolving balance indicator | Model feature |
| prior_30dpd_flag | Previously observed 30+ DPD | Model feature |
| txn_drop_pct | Simulated prior spending trend | Model feature |
| opted_out | Outreach opt-out | Eligibility only |
| open_dispute | Disputed case | Eligibility only |
| days_since_outreach | Last outreach recency | Eligibility only |
| dpd30_next_60d | **Future 30+ DPD within 60 days** | Outcome only; never feature |
| p30 | Calibrated estimate of that event | Strategy input, NOT regulatory PD |
| ead_usd | Balance + 12% of remaining line (hypothetical) | Economic proxy |
| loss_proxy_usd | p30 × assumed progression to loss × LGD × EAD | Hypothetical risk economics |
| net_scenario_benefit_usd | Proxy loss benefit given assumed causal effect less costs | Ranking; NOT realized value |

All values are synthetic; cohort field A-D is a simulated operational reporting group, not a lawful fairness/protected-attribute proxy and should not be treated as one.
