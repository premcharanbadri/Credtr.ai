import unittest
import numpy as np
import pandas as pd
from src.pipeline import synthetic_snapshots,split_data,add_economics,policy_selection,ASSUMPTIONS,FEATURES

class TestRiskPulse(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d=synthetic_snapshots(200,seed=42)
    def test_chronology(self):
        a,b,c=split_data(self.d)
        self.assertLess(a.snapshot_month.max(),b.snapshot_month.min())
        self.assertLess(b.snapshot_month.max(),c.snapshot_month.min())
    def test_deterministic(self):
        a=synthetic_snapshots(200,seed=42)
        self.assertEqual(a.dpd30_next_60d.sum(),self.d.dpd30_next_60d.sum())
    def test_no_future_features(self):
        self.assertNotIn('dpd30_next_60d',FEATURES)
        self.assertNotIn('p30',FEATURES)
    def test_policy_optout(self):
        x=self.d.iloc[:100].copy();x['p30']=.4
        x=add_economics(x)
        chosen=policy_selection(x,10,'value')
        self.assertTrue((chosen.opted_out==0).all())
        self.assertTrue((chosen.open_dispute==0).all())
    def test_policy_capacity_per_month(self):
        x=self.d.copy();x['p30']=.35;x=add_economics(x)
        v=policy_selection(x,11,'value')
        self.assertTrue((v.groupby('snapshot_month').size()<=11).all())
    def test_net_value_formula(self):
        x=self.d.head(1).copy();x['p30']=.4;x=add_economics(x)
        r=x.iloc[0]
        expected=r.loss_proxy_usd*.16-7-1.5
        self.assertAlmostEqual(r.net_scenario_benefit_usd,expected)
    def test_cooldown(self):
        x=self.d.copy();x['p30']=.35;x=add_economics(x)
        chosen=policy_selection(x,11,'risk')
        for _, g in chosen.groupby('account_id'):
            mi=pd.PeriodIndex(g.snapshot_month,freq='M').asi8
            self.assertTrue((np.diff(np.sort(mi)) >= 2).all())
    def test_valid_risk_range(self):
        self.assertTrue(self.d.dpd30_next_60d.isin([0,1]).all())
        self.assertTrue(self.d.utilization.between(0,1).all())

if __name__=='__main__':unittest.main()
