# RiskPulseAI : Explainable Credit Early-Warning & Portfolio Strategy

#### Live Demo: https://riskpulseaiapp.streamlit.app/

## Purpose
Predict **30+ days past due within 60 days** using a temporal model evaluation; quantify the incremental value (under explicitly hypothetical efficacy assumptions) of offering **supportive customer outreach** under a constrained team capacity. Never autonomously change card terms, APRs, credit limits, eligibility, or give adverse decisions.

## Reproduce this Project
```bash
pip install -r requirements.txt
python -m src.pipeline
python -m unittest discover -s tests -v
streamlit run app.py
```
`python -m src.pipeline` is deterministic (seed 42). With scikit-learn 1.5 to 1.8 it reproduces every published metric and dollar figure exactly. scikit-learn 1.9 changes the gradient-boosting results slightly (ROC AUC 0.7990 instead of 0.7997), so `requirements.txt` pins `scikit-learn<1.9`.

## Architecture
Synthetic as-of snapshots -> immutable time partitions -> SQL cohort/root cause diagnostics -> transparent credit-risk flags -> logistic baseline -> gradient-boosting challenger -> disjoint-period probability calibration -> out-of-time model selection report -> human-reviewed supportive-outreach prioritization -> scenario risk economics -> executive dashboard.

## Headline finding
The advanced gradient-boosted challenger was selected on validation PR AUC (0.4174 vs logistic regression's 0.4160), but on the untouched future test logistic regression had slightly better ROC AUC, PR AUC, Brier, and top-decile capture. That is a **stop/challenge signal**, not a reason to retrain on the final test. A 2-month contact cooldown also causes a greedy value-first policy to underperform risk-first *slightly* over four months ($60.4K vs $60.5K in hypothetical net value).

## Verified results (Dec 2024 to Mar 2025 holdout, 15,200 account-months)
These were reproduced independently by re-running `src/pipeline.py` and reconciling to `RiskPulse_Financial_Model.xlsx`. All dollar values are **modeled scenario values on synthetic data**, not realized savings.

| Result | Value | Source |
| --- | --- | --- |
| Test ROC AUC / PR AUC: gradient boosting (selected) | 0.7997 / 0.3889 | `outputs/summary.json` |
| Test ROC AUC / PR AUC: logistic regression | 0.8038 / 0.3930 | `outputs/summary.json` |
| Test ROC AUC / PR AUC: rule-based flags | 0.7561 / 0.3055 | `risk_rules()` |
| Top-10% event capture: logistic / boosting / rules | 39.7% / 39.1% / 36.2% | `capture_at_capacity()` |
| Observed 30+ DPD event rate | 10.76% (1,636 events) | `outputs/summary.json` |
| Eligible account-months (consent, dispute, 30-day recency, p30 >= 0.04) | 5,841 | `add_economics()` |
| Net modeled value at 650/month: risk-first / value-first / random | $60,533 / $60,377 / $56,817 | `outputs/strategy_comparison.csv` |
| Value-first gross modeled loss avoidance vs net value | $80,174 gross, $19,797 cost, $60,377 net | `add_economics()` |
| Fixed-cohort break-even outreach effectiveness | about 4.0% | Excel *Sensitivity* method |

The $155 risk-first advantage comes from the 2-month cooldown. With no cooldown, value-first wins by $1,803, so neither ranking is proven better. The decline in event rate over the test window is generated seasonality in `synthetic_snapshots()`, not an outreach effect.

## Claude skills
`.claude/skills/` contains two skills that Claude Code loads automatically in this repository:
- `riskpulse-portfolio-diagnosis`: monthly, cohort and behavioral event rates plus data-integrity checks. Uses the standard-library script `scripts/verify.py`:
  `python .claude/skills/riskpulse-portfolio-diagnosis/scripts/verify.py --data data/synthetic_account_months.csv`
- `riskpulse-independent-review`: a second-pass review checklist that rejects AUC-as-accuracy, target leakage, unsupported savings claims and automated adverse credit actions, and ends in a PASS / PASS WITH QUALIFICATIONS / FAIL verdict.

## Project files
- `src/pipeline.py`: generation, feature processing, model evaluation, scenario policy.
- `data/`: deterministic generated synthetic monthly account snapshots, safe for public hosting.
- `outputs/`: scored holdout, metrics, calibration, deciles, drift, comparisons.
- `sql/credit_portfolio_monitor.sql`: SQL diagnosis and calibration monitoring.
- `app.py`: browser-facing dashboard.
- `docs/`: business case, governance, data dictionary, experiments and reproducibility.
- `.claude/skills/`: Claude skills for portfolio diagnosis and independent review.
- `tests/`: basic unit tests. Tests do **not** establish production model fitness.
- `RiskPulse_Financial_Model.xlsx`: editable scenario assumptions and Excel calculations.

## Critical analytical limits
1. Outcome `dpd30_next_60d` is a 30+ DPD prediction, **not probability of default** (90+ DPD/chargeoff) and not IFRS 9 or CECL ECL.
2. Economics use explicitly assumed conversion from delinquency to eventual loss and assumed efficacy of customer assistance. **The model does not measure the causal effect of outreach.**
3. Multiple monthly observations of the same synthetic account occur in the dataset; out-of-time predictions are repeated account-month predictions, not unique lifetime customers.
4. A fitted classifier on synthetic data is not validated on live credit data. Feature labels and outcome mechanisms were invented for education.
5. Regulatory review, privacy, permitted features, fairness assessment, ongoing monitoring, and independent validation are necessary before live use.

## Deployment without leaving a laptop running
**Instant-on static case study (recommended for recruiters):** Push the repository to GitHub. Open Settings → Pages → Deploy from branch → `main` and `/docs`. The static `docs/index.html` contains precomputed metrics and a browser-only financial sensitivity calculator. It needs no Python server or API key. The exact URL will usually be `https://<github-user>.github.io/<repo>/`.

**Interactive Streamlit version:** Push repository to GitHub, use https://share.streamlit.io/, choose branch `main` and app path `app.py`. Its data is precomputed, so visitor requests do not trigger model retraining; free hosting can still go idle when unused.
