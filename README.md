# RiskPulse AI — Explainable Credit Early-Warning & Portfolio Strategy

**Independent portfolio reconstruction; 100% synthetic data. NOT TCS work evidence, NOT a live underwriting/risk platform.**

## Purpose
Predict **30+ days past due within 60 days** using a temporal model evaluation; quantify the incremental value (under explicitly hypothetical efficacy assumptions) of offering **supportive customer outreach** under a constrained team capacity. Never autonomously change card terms, APRs, credit limits, eligibility, or give adverse decisions.

## Reproduce
```bash
pip install -r requirements.txt
python -m src.pipeline
python -m unittest discover -s tests -v
streamlit run app.py
```

The hosted dashboard reads precomputed CSV and JSON files; model training is not required on each visitor request.

## Architecture
Synthetic as-of snapshots -> immutable time partitions -> SQL cohort/root cause diagnostics -> transparent credit-risk flags -> logistic baseline -> gradient-boosting challenger -> disjoint-period probability calibration -> out-of-time model selection report -> human-reviewed supportive-outreach prioritization -> scenario risk economics -> executive dashboard.

## Project files
- `src/pipeline.py`: generation, feature processing, model evaluation, scenario policy.
- `data/`: deterministic generated synthetic monthly account snapshots, safe for public hosting.
- `outputs/`: scored holdout, metrics, calibration, deciles, drift, comparisons.
- `sql/credit_portfolio_monitor.sql`: SQL diagnosis and calibration monitoring.
- `app.py`: browser-facing dashboard.
- `docs/`: business case, governance, data dictionary, experiments and reproducibility.
- `tests/`: basic unit tests. Tests do **not** establish production model fitness.
- `RiskPulse_Financial_Model.xlsx`: editable scenario assumptions and Excel calculations.

## Critical analytical limits
1. Outcome `dpd30_next_60d` is a 30+ DPD prediction, **not probability of default** (90+ DPD/chargeoff) and not IFRS 9 or CECL ECL.
2. Economics use explicitly assumed conversion from delinquency to eventual loss and assumed efficacy of customer assistance. **The model does not measure the causal effect of outreach.**
3. Multiple monthly observations of the same synthetic account occur in the dataset; out-of-time predictions are repeated account-month predictions, not unique lifetime customers.
4. A fitted classifier on synthetic data is not validated on live credit data. Feature labels and outcome mechanisms were invented for education.
5. Regulatory review, privacy, permitted features, fairness assessment, ongoing monitoring, and independent validation are necessary before live use.

## Historical integrity
The candidate can claim this as an **independent portfolio project after personally reproducing and understanding it**, not that it was implemented at TCS. Original bank client achievements need actual work records and approved evidence.

## Deployment without leaving a laptop running
**Instant-on static case study (recommended for recruiters):** Push the repository to GitHub. Open Settings → Pages → Deploy from branch → `main` and `/docs`. The static `docs/index.html` contains precomputed metrics and a browser-only financial sensitivity calculator. It needs no Python server or API key. The exact URL will usually be `https://<github-user>.github.io/<repo>/`.

**Interactive Streamlit version:** Push repository to GitHub, use https://share.streamlit.io/, choose branch `main` and app path `app.py`. Its data is precomputed, so visitor requests do not trigger model retraining; free hosting can still go idle when unused.

## Headline finding
The advanced gradient-boosted challenger was selected on validation PR AUC (0.4174 vs logistic regression's 0.4160), but on the untouched future test logistic regression had slightly better ROC AUC, PR AUC, Brier, and top-decile capture. That is a **stop/challenge signal**, not a reason to retrain on the final test. A 60-day contact cooldown also causes a greedy value-first policy to underperform risk-first *slightly* over four months ($60.4K vs $60.5K in hypothetical net value). These are deliberate examples of critical thinking and evidence-based refusal to over-engineer.
