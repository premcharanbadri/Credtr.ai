-- Generic DuckDB SQL. Synthetic data only.
-- Repeated account-month snapshots: COUNT(*) represents snapshots, not unique customers.
-- Label: 30+ DPD within 60 days, NOT default PD.

-- 1. Exposure by snapshot month and lending risk indicators.
SELECT snapshot_month, COUNT(*) AS account_snapshots,
       ROUND(AVG(utilization), 3) AS avg_utilization,
       ROUND(AVG(CAST(missed_payments_3m > 0 AS INTEGER)), 3) AS any_missed_payment_rate,
       ROUND(AVG(dpd30_next_60d), 3) AS realized_30dpd_rate,
       ROUND(SUM(balance_usd), 2) AS total_balance_usd
FROM read_csv_auto('data/synthetic_account_months.csv')
GROUP BY snapshot_month ORDER BY snapshot_month;

-- 2. Cohort comparison: observed association is not a causal estimate.
SELECT CASE WHEN utilization >= .85 THEN 'High utilization' ELSE 'Other' END AS utilization_group,
       CASE WHEN missed_payments_3m >= 1 THEN 'Prior misses' ELSE 'No recent misses' END AS repayment_group,
       COUNT(*) AS snapshots, ROUND(AVG(dpd30_next_60d), 3) AS rate_30dpd_next60d
FROM read_csv_auto('data/synthetic_account_months.csv')
GROUP BY 1, 2 ORDER BY 1, 2;

-- 3. Model calibration by risk decile on out-of-time holdout.
SELECT risk_decile, COUNT(*) AS snapshots,
       ROUND(AVG(p30), 4) AS mean_predicted_risk,
       ROUND(AVG(dpd30_next_60d), 4) AS observed_outcome_rate
FROM read_csv_auto('outputs/out_of_time_predictions.csv')
GROUP BY risk_decile ORDER BY risk_decile;
