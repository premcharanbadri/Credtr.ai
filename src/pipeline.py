"""Credtr.ai | deterministic synthetic data, honest temporal evaluation, decision economics.

IMPORTANT: No real persons or client data; no causal treatment effect measured.
Synthetic target: 30+ days past due during next 60 days, NOT regulatory default PD.
Economic analysis adds an assumed 30+DPD-to-loss transition factor.
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.special import expit, logit
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score, average_precision_score, brier_score_loss, log_loss
from sklearn.inspection import permutation_importance

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "outputs"
SEED = 42
FEATURES = [
    "utilization", "util_change_3m", "payment_to_balance", "payment_ratio_change",
    "missed_payments_3m", "income_volatility", "balance_usd", "months_on_book",
    "promo_expiring_60d", "revolver", "prior_30dpd_flag", "txn_drop_pct",
]
ASSUMPTIONS = {
    "transition_to_loss": 0.25,
    "lgd": 0.70,
    "relative_risk_reduction_if_contacted": 0.16,
    "contact_cost_usd": 7.00,
    "customer_friction_cost_usd": 1.50,
    "portfolio_monthly_contact_capacity": 650,
    "eligibility_min_p30": 0.04,
}


def synthetic_snapshots(n_accounts=3800, seed=SEED):
    """Synthetic account-month snapshots, not an empirical UK retail credit dataset."""
    rng = np.random.default_rng(seed)
    months = pd.period_range("2024-01", "2025-03", freq="M")
    base_risk = rng.normal(0, 0.7, n_accounts)
    base_limit = np.clip(rng.lognormal(np.log(5500), 0.6, n_accounts), 1200, 26000)
    base_util = rng.beta(2.7, 4.2, n_accounts)
    base_income_vol = np.clip(rng.beta(2.2, 6.5, n_accounts), .01, 1)
    tenure0 = rng.integers(6, 75, n_accounts)
    region_index = rng.integers(0, 4, n_accounts)  # synthetic anonymized operations cohorts, not protected attributes
    optout = rng.binomial(1, .09, n_accounts)
    frames = []
    prev_util = base_util.copy()
    prev_pay = np.clip(.7 + rng.normal(0, .14, n_accounts), .02, 1.5)
    for t, month in enumerate(months):
        shock = .03 * np.sin(t / 3) + (0.035 if t >= 10 else 0.0)
        utilization = np.clip(.65 * base_util + .35 * prev_util + rng.normal(0,.09,n_accounts) + shock, .03, .99)
        util_change = np.clip(utilization - prev_util + rng.normal(0,.04,n_accounts), -.40, .55)
        income_vol = np.clip(base_income_vol + rng.normal(0,.07,n_accounts), .0, 1.0)
        # Features observed at the snapshot date only; do not include future outcome.
        p_missed = expit(-2.65 + 2.4*utilization + 1.1*income_vol + 0.75*base_risk)
        missed = rng.binomial(3, np.clip(p_missed / 2.3, .008, .54))
        pay_ratio = np.clip(.9 - .62*utilization - .13*missed - .17*income_vol + rng.normal(0,.16,n_accounts), .03, 1.35)
        pay_delta = np.clip(pay_ratio-prev_pay,-.9,.9)
        prior_30 = rng.binomial(1, expit(-3.3 + 1.7*missed + 1.3*utilization + .6*base_risk))
        promo = rng.binomial(1, .08 + .18*(t % 5 == 0) + .03*(base_risk > 0))
        revolver = rng.binomial(1,np.clip(.3+.54*utilization,.05,.97))
        txn_drop = np.clip(.10 + .22*income_vol + .18*(missed>=1) + rng.normal(0,.17,n_accounts),0,.95)
        credit_limit = base_limit * np.clip(1+.015*t,1,1.25)
        balance = np.clip(utilization*credit_limit,50,25000)
        # nonlinear latent outcome: test why challenger adds value over logistic model
        true_logit = (
            -4.15 + 2.25*utilization + 1.15*np.maximum(util_change,0)*3
            + .85*(missed >= 1) + .55*(missed >= 2)
            + .9*prior_30 + .75*income_vol - 1.15*pay_ratio
            - .9*np.maximum(pay_delta,0) + .42*promo*(utilization>.68)
            + .5*revolver + .4*txn_drop + .40*base_risk
            + .2*(t>=10)
        )
        true_p = np.clip(expit(true_logit), .001, .82)
        outcome = rng.binomial(1, true_p)
        flags = rng.binomial(1, np.clip(.035 + .07 * prior_30, 0, .4))  # preexisting open dispute
        last_contact = rng.integers(0, 120, n_accounts)
        frame = pd.DataFrame({
            "account_id": [f"SYN-{i:05d}" for i in range(n_accounts)],
            "snapshot_month": str(month),
            "cohort": np.array(["A","B","C","D"])[region_index],
            "utilization": utilization,
            "util_change_3m": util_change,
            "payment_to_balance": pay_ratio,
            "payment_ratio_change": pay_delta,
            "missed_payments_3m": missed,
            "income_volatility": income_vol,
            "balance_usd": balance,
            "credit_limit_usd": credit_limit,
            "months_on_book": tenure0+t,
            "promo_expiring_60d": promo,
            "revolver": revolver,
            "prior_30dpd_flag": prior_30,
            "txn_drop_pct": txn_drop,
            "opted_out": optout,
            "open_dispute": flags,
            "days_since_outreach": last_contact,
            "dpd30_next_60d": outcome,
        })
        frames.append(frame)
        prev_util = utilization
        prev_pay = pay_ratio
    return pd.concat(frames, ignore_index=True)


def split_data(data):
    train = data[data.snapshot_month <= "2024-09"].copy()
    cal = data[data.snapshot_month.isin(["2024-10", "2024-11"])].copy()
    test = data[data.snapshot_month >= "2024-12"].copy()
    assert train.snapshot_month.max() < cal.snapshot_month.min() < test.snapshot_month.min()
    return train, cal, test


def score_metrics(y, p):
    y = np.asarray(y); p = np.clip(np.asarray(p),1e-7,1-1e-7)
    return {
        "roc_auc": round(float(roc_auc_score(y,p)),4),
        "pr_auc": round(float(average_precision_score(y,p)),4),
        "brier": round(float(brier_score_loss(y,p)),4),
        "log_loss": round(float(log_loss(y,p)),4),
        "event_rate": round(float(y.mean()),4),
    }


def calibrate_on_disjoint_period(pred_cal, y_cal, pred_test):
    # Platt-style calibration on disjoint chronological months; tiny 1-variable logistic model.
    eps=1e-5
    m=LogisticRegression(solver="lbfgs",max_iter=300)
    m.fit(logit(np.clip(pred_cal,eps,1-eps)).reshape(-1,1),y_cal)
    pt=m.predict_proba(logit(np.clip(pred_test,eps,1-eps)).reshape(-1,1))[:,1]
    return np.clip(pt, 1e-5, 1-1e-5), m


def risk_rules(df):
    # A transparent leading-indicator baseline; no model fitting.
    points=(df.utilization>=.85).astype(int)+(df.util_change_3m>=.12).astype(int) + (df.missed_payments_3m>=1).astype(int)*2 + (df.payment_to_balance<.25).astype(int)+df.prior_30dpd_flag.astype(int)*2
    return np.clip(.03+points*.073, .005, .85)


def add_economics(df, assumptions=ASSUMPTIONS):
    d=df.copy()
    # For educational scenario only: projected EAD is NOT a validated credit accounting estimate.
    d["ead_usd"] = d.balance_usd + .12 * np.maximum(d.credit_limit_usd-d.balance_usd,0)
    d["loss_proxy_usd"] = d.p30 * assumptions["transition_to_loss"] * assumptions["lgd"] * d.ead_usd
    d["gross_scenario_benefit_usd"] = d.loss_proxy_usd * assumptions["relative_risk_reduction_if_contacted"]
    d["net_scenario_benefit_usd"] = d.gross_scenario_benefit_usd - assumptions["contact_cost_usd"] - assumptions["customer_friction_cost_usd"]
    d["eligible"] = ((d.opted_out==0)&(d.open_dispute==0)&(d.days_since_outreach>=30)&(d.p30>=assumptions["eligibility_min_p30"]))
    return d


def policy_selection(df, capacity, strategy="value", only_positive=True, cooldown_months=2):
    """Human-reviewed supportive outreach with capacity and repeat-contact guardrails.

    Once selected, a synthetic account cannot be selected in the next 1 month;
    at least 2 calendar months must elapse between scenario outreach selections.
    This reduces (does not eliminate) overlapping-horizon double counting.
    """
    elig=df.loc[df.eligible].copy()
    if only_positive:
        elig=elig[elig.net_scenario_benefit_usd>0]
    if strategy=="value":
        elig=elig.sort_values(["net_scenario_benefit_usd", "account_id"],ascending=[False,True])
    elif strategy=="risk":
        elig=elig.sort_values(["p30", "account_id"],ascending=[False,True])
    elif strategy=="random":
        elig=elig.sample(frac=1,random_state=SEED)
    else:
        raise ValueError("unknown strategy")
    last_selected={}
    selected=[]
    for i,month in enumerate(sorted(elig.snapshot_month.unique())):
        candidates=elig[elig.snapshot_month==month]
        eligible_time=candidates.account_id.map(lambda a: i-last_selected.get(a,-100)>=cooldown_months)
        chosen=candidates.loc[eligible_time].head(int(capacity))
        selected.extend(chosen.index.tolist())
        for acc in chosen.account_id:
            last_selected[acc]=i
    return elig.loc[selected].copy()


def policies_by_month(df, capacity=650):
    rows=[]
    for method in ["random", "risk", "value"]:
        chosen=policy_selection(df,capacity,method)
        rows.append({"strategy":method,"contacts":int(len(chosen)),"months":int(df.snapshot_month.nunique()),
                     "monthly_avg_contacts":round(len(chosen)/df.snapshot_month.nunique(),1),
                     "gross_scenario_benefit_usd":round(float(chosen.gross_scenario_benefit_usd.sum()),2),
                     "costs_usd":round(float(len(chosen)*(ASSUMPTIONS['contact_cost_usd']+ASSUMPTIONS['customer_friction_cost_usd'])),2),
                     "net_scenario_value_usd":round(float(chosen.net_scenario_benefit_usd.sum()),2),
                     "mean_risk":round(float(chosen.p30.mean()),4),
                     "mean_ead_usd":round(float(chosen.ead_usd.mean()),2)})
    return pd.DataFrame(rows)


def capture_at_capacity(y, p, fraction=.1):
    n=max(1,int(np.ceil(len(p)*fraction)))
    idx=np.argsort(-np.asarray(p))[:n]
    return round(float(np.asarray(y)[idx].sum()/max(np.asarray(y).sum(),1)),4)


def generate():
    DATA.mkdir(parents=True,exist_ok=True);OUT.mkdir(parents=True,exist_ok=True)
    raw=synthetic_snapshots()
    train,cal,test=split_data(raw)
    baseline=Pipeline([("scale",StandardScaler()),("lr",LogisticRegression(max_iter=600,C=.7))])
    advanced=HistGradientBoostingClassifier(max_iter=180,max_leaf_nodes=15,learning_rate=.07,l2_regularization=5,min_samples_leaf=70,random_state=SEED)
    models={"Logistic regression":baseline,"Gradient-boosted AI":advanced}
    scores={}; val_predictions={}; test_predictions={}
    for name,model in models.items():
        model.fit(train[FEATURES],train.dpd30_next_60d)
        cal_raw=model.predict_proba(cal[FEATURES])[:,1]
        test_raw=model.predict_proba(test[FEATURES])[:,1]
        test_p,cal_model=calibrate_on_disjoint_period(cal_raw,cal.dpd30_next_60d,test_raw)
        # Do not select on test; select on validation discrimination (pre-calibration).
        val_predictions[name]=cal_raw
        test_predictions[name]=test_p
        scores[name]={"validation":score_metrics(cal.dpd30_next_60d,cal_raw),"test":score_metrics(test.dpd30_next_60d,test_p)}
    rule_test=risk_rules(test)
    scores["Rule-based flags"]={"test":score_metrics(test.dpd30_next_60d,rule_test)}
    # Select advanced model based on validation PR AUC (tie-break Brier).
    winner=max(models, key=lambda name:(scores[name]["validation"]["pr_auc"],-scores[name]["validation"]["brier"]))
    chosen=test_predictions[winner]
    test["p30"]=chosen
    test["rule_risk_score"]=rule_test
    test["logistic_p30"]=test_predictions["Logistic regression"]
    test["boosted_p30"]=test_predictions["Gradient-boosted AI"]
    test=add_economics(test)
    test["risk_decile"]=pd.qcut(test.p30.rank(method="first"),10,labels=list(range(1,11)))
    # Rank 10 means highest risk.
    test["risk_decile"] = test["risk_decile"].astype(int)
    deciles=test.groupby("risk_decile").agg(accounts=("account_id","size"),observed_30dpd_rate=("dpd30_next_60d","mean"),mean_predicted_p30=("p30","mean"),total_exposure_usd=("ead_usd","sum")).reset_index()
    bins=np.linspace(0,1,11)
    test["calibration_bin"]=pd.cut(test.p30,bins,include_lowest=True)
    calibration=test.groupby("calibration_bin",observed=True).agg(accounts=("dpd30_next_60d","size"),predicted=("p30","mean"),observed=("dpd30_next_60d","mean")).reset_index()
    calibration["calibration_bin"]=calibration.calibration_bin.astype(str)
    policy=policies_by_month(test)
    for label,p in [("Rule-based flags",rule_test),("Logistic regression",test_predictions["Logistic regression"]),("Gradient-boosted AI",test_predictions["Gradient-boosted AI"])]:
        scores[label]["test"]["top_10pct_event_capture"] = capture_at_capacity(test.dpd30_next_60d,p,.1)
    # Test data is frozen: permutation explanations are descriptive, not a basis for re-selection.
    perm = permutation_importance(models[winner],cal[FEATURES],cal.dpd30_next_60d,scoring="average_precision", n_repeats=3,random_state=SEED,n_jobs=1)
    importance=pd.DataFrame({"feature":FEATURES,"permutation_pr_auc_drop":perm.importances_mean}).sort_values("permutation_pr_auc_drop",ascending=False)
    # Stability: population change test vs training for raw features using fixed training bins.
    psi=[]
    for feature in ["utilization","payment_to_balance","balance_usd","income_volatility"]:
        tr=train[feature].to_numpy();te=test[feature].to_numpy()
        edges=np.unique(np.quantile(tr,np.linspace(0,1,11)))
        if len(edges)<3: continue
        edges[0]=-np.inf;edges[-1]=np.inf
        a=np.histogram(tr,bins=edges)[0]/len(tr)
        b=np.histogram(te,bins=edges)[0]/len(te)
        a=np.clip(a,1e-6,None);b=np.clip(b,1e-6,None)
        psi.append({"feature":feature,"psi":round(float(np.sum((b-a)*np.log(b/a))),4)})
    selected=policy_selection(test,650,"value")
    test["value_strategy_selected"] = test.index.isin(selected.index).astype(int)
    raw.to_csv(DATA/"synthetic_account_months.csv",index=False)
    test.to_csv(OUT/"out_of_time_predictions.csv",index=False)
    deciles.to_csv(OUT/"risk_deciles.csv",index=False)
    calibration.to_csv(OUT/"calibration.csv",index=False)
    policy.to_csv(OUT/"strategy_comparison.csv",index=False)
    importance.to_csv(OUT/"feature_importance.csv",index=False)
    pd.DataFrame(psi).to_csv(OUT/"feature_drift_psi.csv",index=False)
    month_trends=raw.groupby("snapshot_month").agg(accounts=("account_id","size"),observed_30dpd_rate=("dpd30_next_60d","mean"),avg_utilization=("utilization","mean")).reset_index()
    month_trends.to_csv(OUT/"month_trends.csv",index=False)
    summary={
        "purpose":"30+ DPD in the next 60 days; probabilities are NOT 90+ DPD/default PD",
        "data":"100% synthetic; results are NOT client outcomes",
        "splits":{"train":len(train),"calibration":len(cal),"test":len(test),"train_end":train.snapshot_month.max(),"calibration_end":cal.snapshot_month.max(),"test_start":test.snapshot_month.min(),"test_end":test.snapshot_month.max()},
        "selected_model":winner,
        "metrics":scores,
        "assumptions":ASSUMPTIONS,
        "test_population":{"snapshots":len(test),"monthly_unique_accounts":int(test.account_id.nunique()),"months":int(test.snapshot_month.nunique()),"observed_30dpd_rate":float(test.dpd30_next_60d.mean()),"mean_predicted_p30":float(test.p30.mean())},
        "hypothetical_strategy_value":policy.set_index('strategy')["net_scenario_value_usd"].to_dict(),
        "notes":["Outcomes and action effects are generated/assumed, not measured in a randomized trial.","Do not equate 30+DPD risk with regulatory PD or assert actual ECL savings.","No autonomous credit-limit, pricing, or adverse credit decisions.","Temporal split; same synthetic accounts recur in distinct monthly snapshots and portfolio costs are per account-month, not lifetime unique customers."]
    }
    (OUT/"summary.json").write_text(json.dumps(summary,indent=2))
    print(json.dumps({"selected":winner,"train":len(train),"cal":len(cal),"test":len(test),"metric":scores[winner]['test'],"policies":policy.to_dict(orient="records")},indent=2))
    return summary

if __name__=="__main__":
    generate()
