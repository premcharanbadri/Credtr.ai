"""RiskPulse AI: pure synthetic-data portfolio dashboard; no live banking decisions."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

ROOT=Path(__file__).resolve().parent
st.set_page_config(page_title="RiskPulse AI | Credit Portfolio Decisions",page_icon="📊",layout="wide")

@st.cache_data

def load():
    base=ROOT/"outputs"
    dat={name:pd.read_csv(base/f"{name}.csv") for name in ["out_of_time_predictions","risk_deciles","calibration","strategy_comparison","feature_importance","feature_drift_psi","month_trends"]}
    dat["summary"]=json.loads((base/"summary.json").read_text())
    return dat
D=load();s=D['summary'];d=D['out_of_time_predictions']

st.title("RiskPulse AI")
st.caption("Explainable early warning • Operationally constrained supportive outreach • Financial decision analytics")
st.warning("Note: Modeled loss reductions are assumptions, not observed effects. This is not an automated lending-decision platform.")

with st.sidebar:
    st.header("What-if assumptions")
    st.caption("These change scenario economics only, not trained prediction scores.")
    transition=st.slider("30+ DPD → loss transition assumption",.05,.70,.25,.05)
    lgd=st.slider("Loss given default",.20,.90,.70,.05)
    effect=st.slider("Assumed relative reduction from helpful outreach",.0,.35,.16,.01)
    contact_cost=st.slider("Contact + customer friction cost ($)",0.,30.,8.5,.5)
    monthly_cap=st.slider("Maximum outreach per month",100,1600,650,50)
    min_risk=st.slider("Minimum P(30+ DPD) eligibility",.00,.40,.04,.01)
    st.divider()
    st.caption("Policy selection is illustrative and must be approved by Risk, Compliance, and servicing leadership.")

x=d.copy()
x['ead_usd']=x.balance_usd + .12*np.maximum(x.credit_limit_usd-x.balance_usd,0)
x['sim_benefit']=x.p30*transition*lgd*x.ead_usd*effect
x['sim_net']=x.sim_benefit-contact_cost
x['eligible']=(x.opted_out==0)&(x.open_dispute==0)&(x.days_since_outreach>=30)&(x.p30>=min_risk)&(x.sim_net>0)

def strategy(method):
    eligible=x.loc[x.eligible].copy()
    if method=="Expected value":eligible=eligible.sort_values(['sim_net','account_id'],ascending=[False,True])
    elif method=="Highest risk":eligible=eligible.sort_values(['p30','account_id'],ascending=[False,True])
    else:eligible=eligible.sample(frac=1,random_state=42)
    selected=[];last_selected={}
    for i,month in enumerate(sorted(eligible.snapshot_month.unique())):
        candidates=eligible[eligible.snapshot_month==month]
        allowed=candidates.account_id.map(lambda a: i-last_selected.get(a,-100)>=2)
        chosen=candidates.loc[allowed].head(monthly_cap)
        selected.extend(chosen.index.tolist())
        for a in chosen.account_id:last_selected[a]=i
    chosen=eligible.loc[selected].copy()
    return {"Method":method,"Contacts":len(chosen),"Gross benefit ($)":float(chosen.sim_benefit.sum()),"Scenario net benefit ($)":float(chosen.sim_net.sum()),"Mean predicted risk":float(chosen.p30.mean()) if len(chosen) else 0},chosen

policies=[strategy(s) for s in ("Random eligible","Highest risk","Expected value")]
polsum=pd.DataFrame([p[0] for p in policies]); best=policies[2][1]

t1,t2,t3,t4=st.tabs(["Executive decision", "Credit risk diagnostics", "Model validation", "Implementation & governance"])
with t1:
    st.subheader("The decision: whom should we help first?")
    c1,c2,c3,c4=st.columns(4)
    c1.metric("Holdout snapshots",f"{len(x):,}")
    c2.metric("30+ DPD event rate",f"{x.dpd30_next_60d.mean():.1%}")
    c3.metric("AI ROC AUC",f"{s['metrics'][s['selected_model']]['test']['roc_auc']:.3f}")
    c4.metric("Top 10% event capture",f"{s['metrics'][s['selected_model']]['test']['top_10pct_event_capture']:.1%}")
    st.caption("Holdout = four synthetic account-month snapshots from Dec 2024–Mar 2025; accounts recur across months. This is not four months of realized treatment results.")
    st.markdown("#### Modeled policy value under your assumptions")
    fig=px.bar(polsum,x="Method",y="Scenario net benefit ($)",text="Scenario net benefit ($)",title="Expected value vs. risk-first vs. random selection")
    fig.update_traces(texttemplate='$%{text:,.0f}',textposition='outside')
    fig.update_layout(yaxis_title="Four-month modeled net value (USD)",xaxis_title="Policy",height=380)
    st.plotly_chart(fig,use_container_width=True)
    a,b,c=st.columns(3)
    a.metric("Value-prioritized contacts",f"{len(best):,}")
    b.metric("Four-month modeled net value",f"${polsum.iloc[2]['Scenario net benefit ($)']:,.0f}")
    c.metric("Value vs risk-first",f"${polsum.iloc[2]['Scenario net benefit ($)']-polsum.iloc[1]['Scenario net benefit ($)']:,.0f}")
    st.caption("All benefits depend on unmeasured causal effectiveness and transition assumptions. There is **no demonstrated credit-loss reduction** in this project.")
    display=polsum.copy();display['Mean predicted risk']=display['Mean predicted risk'].map(lambda z:f"{z:.1%}")
    st.dataframe(display,use_container_width=True,hide_index=True)
    st.markdown("#### Recommendation")
    st.info("Use a human-reviewed, supportive-outreach pilot. Start with eligible accounts that have positive estimated net value, enforce operational capacity, and validate the actual treatment effect via a randomized trial. Do not change pricing, account eligibility, credit limits, or adverse-action decisions with this tool.")

with t2:
    st.subheader("Where does portfolio risk concentrate?")
    d1,d2=st.columns(2)
    with d1:
        dec=D['risk_deciles']
        fig=go.Figure()
        fig.add_bar(x=dec.risk_decile,y=dec.observed_30dpd_rate,name='Observed 30+ DPD')
        fig.add_scatter(x=dec.risk_decile,y=dec.mean_predicted_p30,name='Predicted risk',mode='lines+markers')
        fig.update_layout(title="Actual vs predicted by risk decile",xaxis_title="Risk decile (10=highest)",yaxis_tickformat='.0%',height=400)
        st.plotly_chart(fig,use_container_width=True)
    with d2:
        trends=D['month_trends']
        fig=px.line(trends,x='snapshot_month',y='observed_30dpd_rate',markers=True,title="Synthetic monthly realized event rate")
        fig.update_layout(yaxis_tickformat='.0%',xaxis_title='Snapshot month',yaxis_title='30+ DPD rate',height=400)
        st.plotly_chart(fig,use_container_width=True)
    imp=D['feature_importance'].head(10).sort_values('permutation_pr_auc_drop')
    fig=px.bar(imp,x='permutation_pr_auc_drop',y='feature',orientation='h',title='Leading predictive signals (validation-period permutation importance)')
    fig.update_layout(xaxis_title='Drop in validation PR AUC when shuffled',yaxis_title='',height=420)
    st.plotly_chart(fig,use_container_width=True)
    st.caption("Importance describes association in a synthetic predictor. It does not establish the cause of delinquency or justify an adverse credit decision.")

with t3:
    st.subheader("Model challenge, calibration, out-of-time evaluation")
    model_rows=[]
    for name,vals in s['metrics'].items():
        m=vals['test'];model_rows.append({'Model':name,'ROC AUC':m['roc_auc'],'PR AUC':m['pr_auc'],'Brier score ↓':m['brier'],'Top 10% capture':m['top_10pct_event_capture']})
    st.dataframe(pd.DataFrame(model_rows),use_container_width=True,hide_index=True)
    st.caption("Model chosen on pre-test validation PR AUC; final holdout used only to report performance. Probability calibration was fit on a separate time period.")
    cc=D['calibration']
    fig=go.Figure()
    fig.add_scatter(x=[0,.6],y=[0,.6],mode='lines',name='Perfect calibration',line=dict(dash='dash'))
    fig.add_scatter(x=cc.predicted,y=cc.observed,mode='lines+markers',name='Simulated holdout',text=cc.accounts)
    fig.update_layout(title='Predicted probability vs observed 30+ DPD',xaxis_title='Mean predicted risk',yaxis_title='Observed event frequency',xaxis_range=[0,.6],yaxis_range=[0,.6],height=420)
    st.plotly_chart(fig,use_container_width=True)
    st.markdown('#### Stability watch')
    st.dataframe(D['feature_drift_psi'],use_container_width=True,hide_index=True)
    st.caption('PSI is a rough population-shift indicator, not proof of model fairness, validity, or stability.')

with t4:
    st.subheader('Ethical implementation path')
    st.markdown('''
**Phase 1 — Data assurance:** Confirm as-of dates, exposure and product definitions; benchmark simpler early-warning rules.  
**Phase 2 — Shadow validation:** Independently verify the chosen model, calibration, leakage controls, risk deciles, drift, privacy, and proxy fairness.  
**Phase 3 — Compliant experiment:** Randomize *permitted, supportive customer communications* when lawful and ethical; never withhold required servicing or hardship support.  
**Phase 4 — Economic evaluation:** Test the incremental impact of communications and losses avoided, including complaints, opt-outs, capacity, and delivery costs.  
**Phase 5 — Scale or stop:** Obtain human approval, log decisions, monitor outcomes, and roll back if harm/quality thresholds fail.

**Hard guardrails:** No credit-limit cuts, APR changes, underwriting, adverse actions, or automated discriminatory targeting. Future real-data use requires authorizations and independent model-risk validation.
''')
    st.markdown('#### Export the scenario strategy comparison')
    st.download_button('Download scenario comparison CSV',polsum.to_csv(index=False),'riskpulse_strategy_scenario.csv','text/csv')
    st.markdown('#### Reference documents')
    st.markdown('- [UK PRA Model Risk Management Statement](https://www.bankofengland.co.uk/prudential-regulation/publication/2023/may/model-risk-management-principles-for-banks-ss)\n- [NIST AI Risk Management Framework Playbook](https://airc.nist.gov/airmf-resources/playbook/)\n- [scikit-learn Probability Calibration](https://scikit-learn.org/stable/modules/calibration.html)')

st.caption('© Independent educational Case Study • 100% synthetic data • No banking customer records • Not investment, lending, or credit advice.')
