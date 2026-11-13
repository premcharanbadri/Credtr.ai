"""Build the scenario financial workbook with artifact_tool only."""
from pathlib import Path
import csv
from artifact_tool import Workbook, SpreadsheetFile
from src.pipeline import ASSUMPTIONS, policy_selection
import pandas as pd

ROOT=Path(__file__).resolve().parent
OUT=ROOT/"outputs"
d=pd.read_csv(OUT/"out_of_time_predictions.csv")
# Compute fixed starting policy ranks for Excel scenario sheets; re-ranking lives in Streamlit.
fixed=[]
for name,algo in [("Random eligible","random"),("Highest risk","risk"),("Expected value","value")]:
    g=policy_selection(d,650,algo)
    fixed.append((name,len(g),float((g.p30*g.ead_usd).sum()),float(g.p30.mean())))

w=Workbook.create()
summary=w.worksheets.add("Decision Dashboard")
inputs=w.worksheets.add("Inputs")
strategies=w.worksheets.add("Strategy Economics")
sens=w.worksheets.add("Sensitivity")
sources=w.worksheets.add("Definitions and Sources")
NAVY='#14324F'; BLUE='#2664C4';PALE='#EAF2FD';WHITE='#FFFFFF';DARK='#14202E'; GREEN='#087B54'; GREY='#F1F5F9'
fmt_money='#,##0;[Red](#,##0);-'
fmt_dec='0.0%;[Red](0.0%);-'
fmt_int='#,##0;[Red](#,##0);-'

def title(sh,txt,last='F'):
    sh.merge_cells(f'A1:{last}2')
    sh.get_range('A1').values=[[txt]]
    sh.get_range(f'A1:{last}2').format={'fill':NAVY,'font':{'bold':True,'color':WHITE,'size':16},'vertical_alignment':'center','row_height':24}
    sh.get_range('A:A').format.column_width=34
    sh.get_range('B:F').format.column_width=18

def header(sh,range_):
    sh.get_range(range_).format={'fill':NAVY,'font':{'bold':True,'color':WHITE},'row_height':24}

title(inputs,'CREDTR.AI | Scenario assumptions','D')
inputs.get_range('A4:C4').values=[['Input / parameter','Editable assumption','Rationale / source']]
header(inputs,'A4:C4')
assumptions=[
('P(30+ DPD → eventual loss)',.25,'Illustrative scenario assumption; not an estimated transition model'),
('Loss given default',.70,'Illustrative recovery assumption, not verified LGD'),
('Relative risk reduction from outreach',.16,'Unmeasured and hypothetical; randomized test required'),
('Contact cost per case ($)',7,'Synthetic per-contact operating estimate'),
('Customer friction per case ($)',1.5,'Synthetic expected customer-impact allowance'),
('Capacity per month (accounts)',650,'Synthetic team operations scenario'),
('Evaluation months',4,'Dec 2024–Mar 2025 holdout'),
('EAD unused credit draw factor',.12,'Synthetic exposure sensitivity assumption'),
('Monthly accounts in synthetic population',3800,'Generated synthetic account count'),
]
inputs.get_range('A5:C13').values=[[a,b,c] for a,b,c in assumptions]
inputs.get_range('B5:B13').format.font.color='#0000FF'
inputs.get_range('B5:B13').format.fill='#FFF7D6'
inputs.get_range('B5:B7').set_number_format(fmt_dec)
inputs.get_range('B12').set_number_format(fmt_dec)
inputs.get_range('C:C').format.column_width=66
inputs.get_range('A16:C16').merge_cells('A16:C16') if False else None
inputs.get_range('A16').values=[['IMPORTANT: All inputs are hypothetical unless explicitly marked as measured synthetic data.']]
inputs.get_range('A16:C16').format.wrap_text=True
inputs.get_range('A16:C16').format.font.color='#9A3412'

title(strategies,'STRATEGY ECONOMICS | Fixed selected cohorts','G')
strategies.get_range('A4:G4').values=[['Policy','Contacts (4 months)','Σ P30 × EAD ($)','Mean P30','Gross benefit ($)','Contact/friction ($)','Net scenario value ($)']]
header(strategies,'A4:G4')
strategies.get_range('A5:D7').values=[[a,b,c,dd] for a,b,c,dd in fixed]
for row in range(5,8):
    strategies.get_range(f'E{row}').formulas=[[f'=C{row}*Inputs!$B$5*Inputs!$B$6*Inputs!$B$7']]
    strategies.get_range(f'F{row}').formulas=[[f'=B{row}*(Inputs!$B$8+Inputs!$B$9)']]
    strategies.get_range(f'G{row}').formulas=[[f'=E{row}-F{row}']]
strategies.get_range('C5:C7').set_number_format(fmt_money)
strategies.get_range('D5:D7').set_number_format(fmt_dec)
strategies.get_range('E5:G7').set_number_format(fmt_money)
strategies.get_range('B5:D7').format.font.color='#0000FF'
strategies.get_range('E5:G7').format.font.color='#000000'
strategies.get_range('A9').values=[['SCENARIO CAUTION']]
strategies.get_range('A9:G9').format={'fill':'#FFF0D9','font':{'bold':True,'color':'#9A3412'}}
strategies.merge_cells('A10:G11')
strategies.get_range('A10').values=[['Policy memberships were selected using BASE-case assumptions. Changing assumptions recalculates value but does NOT re-rank accounts: use the Streamlit dashboard for new capacity/rank decisions. No causal uplift was observed.']]
strategies.get_range('A10:G11').format.wrap_text=True
strategies.get_range('A:A').format.column_width=31
strategies.get_range('B:G').format.column_width=21

# sensitivity: 5 assumed effects × 3 outcome transition rates for the expected-value fixed portfolio

title(sens,'SENSITIVITY | Expected-value policy net benefit','F')
sens.get_range('A4:D4').values=[['Assumed outreach effect','Loss progression 15%','Loss progression 25%','Loss progression 35%']]
header(sens,'A4:D4')
for r, eff in enumerate([0,.05,.10,.16,.25],start=5):
    sens.get_range(f'A{r}').values=[[eff]]
    for col,transition in [('B',.15),('C',.25),('D',.35)]:
        head={'B':'B','C':'C','D':'D'}[col]
        # Use header % in row 4? text headers cannot be linked; embed fixed values as formula constants references in B3:D3.
        sens.get_range(f'{col}{r}').formulas=[[f'=\'Strategy Economics\'!$C$7*{col}$3*Inputs!$B$6*$A{r}-\'Strategy Economics\'!$B$7*(Inputs!$B$8+Inputs!$B$9)']]
sens.get_range('B3:D3').values=[[.15,.25,.35]]
sens.get_range('B3:D3').set_number_format(fmt_dec)
sens.get_range('A5:A9').set_number_format(fmt_dec)
sens.get_range('B5:D9').set_number_format(fmt_money)
sens.get_range('A5:A9').format.font.color='#0000FF'
sens.get_range('B3:D3').format.font.color='#0000FF'
sens.get_range('A11').values=[['Negative (red) values indicate the modeled policy would be uneconomic under that assumption.']]
sens.get_range('A:A').format.column_width=42
sens.get_range('B:D').format.column_width=25
sens.get_range('B5:D9').conditional_formats.add_cell_is({'operator':'lessThan','formula':0,'format':{'fill':'#FEE2E2','font':{'color':'#B91C1C'}}})

# executive dashboard with formula links

title(summary,'CREDTR.AI | Credit strategy decision case','F')
summary.get_range('A4:B4').values=[['Headline KPI','Illustrative value']]
header(summary,'A4:B4')
rows=[('Test-set account-month snapshots',15200),('Distinct accounts per month',3800),('Months tested',4),('AI ROC AUC',0.7997),('PR AUC',0.3889),('Top-10% event capture',0.3906),('Observed event rate',0.1076)]
summary.get_range('A5:B11').values=[[k,v] for k,v in rows]
summary.get_range('B8:B11').set_number_format(fmt_dec)
summary.get_range('A14:B14').values=[['Economic metric','Scenario value ($)']]
header(summary,'A14:B14')
summary.get_range('A15:A18').values=[['Value-ranked outreach'],['Risk-ranked outreach'],['Random eligible outreach'],['Incremental modeled value vs risk-first']]
summary.get_range('B15').formulas=[["='Strategy Economics'!G7"]]
summary.get_range('B16').formulas=[["='Strategy Economics'!G6"]]
summary.get_range('B17').formulas=[["='Strategy Economics'!G5"]]
summary.get_range('B18').formulas=[['=B15-B16']]
summary.get_range('B15:B18').set_number_format(fmt_money)
summary.get_range('A21:F21').merge_cells('A21:F21') if False else None
summary.merge_cells('A21:F23')
summary.get_range('A21').values=[['Interpretation: Credit prediction is not a causal outreach effect. All dollar amounts are scenario economics based on synthetic accounts, manually chosen assumptions and simulated policy constraints. No realized credit savings or client implementation is claimed.']]
summary.get_range('A21:F23').format={'fill':'#EAF2FD','wrap_text':True,'font':{'color':DARK},'vertical_alignment':'center'}
summary.get_range('A:A').format.column_width=40
summary.get_range('B:B').format.column_width=25
summary.get_range('C:F').format.column_width=17

# source dictionary and appropriate citation URLs in workbook

title(sources,'DEFINITIONS, PROVENANCE & SOURCE NOTES','D')
sources.get_range('A4:D4').values=[['Concept','Meaning','Provenance','Reference URL']]
header(sources,'A4:D4')
notes=[
('Data provenance','All rows and customer attributes are fictional','Deterministic Python generator in package',''),
('Early warning risk','P(30+ DPD in the next 60 days)','Out-of-time synthetic model evaluation',''),
('Default probability','NOT equivalent to a P(30+ DPD) model','Risk modeling caution',''),
('Transition to loss','Assumed conditional progression from delinquency to loss','Editable scenario assumption',''),
('LGD','Share of exposure eventually lost following default','Editable scenario assumption',''),
('Treatment benefit','Relative hypothetical reduction in loss proxy','Not empirically estimated; requires RCT',''),
('Calibration','Probability reliability; separate fitting/calibration','scikit-learn official docs','https://scikit-learn.org/stable/modules/calibration.html'),
('UK model governance','Validation, oversight, independent challenge','PRA SS1/23; check institutional scope','https://www.bankofengland.co.uk/prudential-regulation/publication/2023/may/model-risk-management-principles-for-banks-ss'),
('AI governance','Govern, Map, Measure, Manage','NIST AI RMF playbook','https://airc.nist.gov/airmf-resources/playbook/'),
('Outreach policy','Supportive, compliant communications only','Not automated adverse credit decision',''),
('Currency','All examples in USD equivalents','Convenient synthetic portfolio assumption',''),
]
sources.get_range(f'A5:D{4+len(notes)}').values=[list(v) for v in notes]
sources.get_range('A:A').format.column_width=29
sources.get_range('B:B').format.column_width=48
sources.get_range('C:C').format.column_width=43
sources.get_range('D:D').format.column_width=86
sources.get_range(f'A5:D{4+len(notes)}').format.wrap_text=True

# Export and check
path=ROOT/'Credtr.ai_Financial_Model.xlsx'
print(w.inspect({'kind':'table','range':'Strategy Economics!A4:G7','include':'values,formulas','table_max_rows':8,'table_max_cols':8}).ndjson[:3500])
print(w.inspect({'kind':'match','search_term':'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A','options':{'use_regex':True,'max_results':30},'summary':'finance validation'}).ndjson[:1000])
SpreadsheetFile.export_xlsx(w).save(str(path))
print('EXPORTED',path, path.stat().st_size)
