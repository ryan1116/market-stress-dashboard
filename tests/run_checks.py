"""Offline integration checks; execute unchanged scripts only in temporary copies."""
import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import runpy
import shutil
import tempfile
from datetime import date, timedelta
from unittest.mock import patch
from urllib.parse import urlparse, parse_qs
import pandas as pd

BASE = Path(__file__).resolve().parents[1]
SOURCE = BASE
TODAY = date.today()
RESULTS = []

def digest():
    return {str(p.relative_to(SOURCE)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in SOURCE.rglob('*') if p.is_file() and '.git' not in p.parts and p.name != 'results.json'}

def check(name, fn):
    try:
        ok, observed = fn()
        RESULTS.append(dict(name=name, status='PASS' if ok else 'FAIL', observed=observed))
    except Exception as exc:
        RESULTS.append(dict(name=name, status='ERROR', observed=f'{type(exc).__name__}: {exc}'))

def dashboard(proxy=None, broken=False, stale=False, desync=False, tp_failure=False, fallback_age=0, pe_age=0, tp_age=0):
    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / 'app'
        shutil.copytree(SOURCE, root, ignore=shutil.ignore_patterns(".git", "tests", ".DS_Store"))
        manual=root/'config/manual_metrics.json'
        m=json.loads(manual.read_text())
        m['eps_fallback']['as_of']=(TODAY-timedelta(days=fallback_age)).isoformat()
        m['forward_pe']['as_of']=(TODAY-timedelta(days=pe_age)).isoformat()
        manual.write_text(json.dumps(m))
        if proxy is not None:
            (root/'data/eps_revision_proxy.json').write_text(json.dumps(proxy))
        if broken:
            (root/'data/eps_revision_proxy.json').write_text('{broken')
        if stale:
            p=root/'config/manual_metrics.json'
            m=json.loads(p.read_text())
            m['eps_fallback']['as_of']='2000-01-01'
            p.write_text(json.dumps(m))
        def fetch(url, **kw):
            series=parse_qs(urlparse(url).query)['id'][0]
            if series=='THREEFYTP10':
                if tp_failure: raise RuntimeError('fixture outage')
                return io.BytesIO(f'DATE,value\n{TODAY-timedelta(days=31+tp_age)},0.8\n{TODAY-timedelta(days=tp_age)},0.9'.encode())
            end=TODAY-timedelta(days=1 if desync and series!='DFII10' else 0)
            values={'DGS10':5.0,'DFII10':2.8,'T10YIE':2.2}
            rows=['DATE,value']
            for n in (100,90,30,1,0):
                day=TODAY-timedelta(days=n)
                if day<=end:
                    value=values[series] + (0.1 if desync and series=='DFII10' and n==0 else 0)
                    rows.append(f'{day},{value}')
            return io.BytesIO('\n'.join(rows).encode())
        table=pd.DataFrame({'Date':[TODAY-timedelta(days=31),TODAY], 'THREEFYTP1000':[.8,.9]})
        with patch('urllib.request.urlopen',side_effect=fetch), patch('pandas.read_html',side_effect=RuntimeError('fixture outage') if tp_failure else None,return_value=[table]),contextlib.redirect_stdout(io.StringIO()):
            scope=runpy.run_path(str(root/'scripts/update_dashboard.py'))
        return json.loads((root/'data/latest.json').read_text()),scope

def proxy(**kw):
    p=dict(as_of=TODAY.isoformat(),revision_60d_pct=2.,seasonal_benchmark_60d=-1.7,coverage_weight=.5,companies_used=15,baseline_mode='PROVISIONAL_CONFIG')
    p.update(kw)
    return p

def eps(negative=False, low=False, unsorted=False, repeat=False, current=None, prior=None):
    with tempfile.TemporaryDirectory() as td:
        root=Path(td)/'app'
        shutil.copytree(SOURCE,root,ignore=shutil.ignore_patterns(".git", "tests", ".DS_Store"))
        cfg=root/'config/eps_proxy_config.json'
        c=json.loads(cfg.read_text())
        if unsorted: c['max_holdings']=2
        cfg.write_text(json.dumps(c))
        holdings=([{'symbol':'SMALL','weight':.001}] if low else
                  [{'symbol':'SMALL','weight':.001},{'symbol':'MID','weight':.01},{'symbol':'LARGE','weight':.2}] if unsorted else
                  [{'symbol':'GOOG','weight':.03},{'symbol':'GOOGL','weight':.02},{'symbol':'TEST','weight':.05}])
        def fetch(url,**kw):
            q=parse_qs(urlparse(url).query)
            if q['function'][0]=='ETF_PROFILE': obj={'holdings':holdings}
            else:
                row={'horizon':'fiscal year','date':(TODAY+timedelta(days=180)).isoformat(),
                     'eps_estimate_average':current if current is not None else (-1 if negative else 11),
                     'eps_estimate_average_60_days_ago':prior if prior is not None else (-2 if negative else 10),
                     'eps_estimate_average_30_days_ago':10,'eps_estimate_average_90_days_ago':10,
                     'eps_estimate_revision_up_trailing_30_days':3,'eps_estimate_revision_down_trailing_30_days':1}
                obj={'estimates':[row]}
            return io.BytesIO(json.dumps(obj).encode())
        with patch.dict(os.environ,{'ALPHAVANTAGE_API_KEY':'TEST_NOT_A_SECRET'}),patch('urllib.request.urlopen',side_effect=fetch),patch('time.sleep'),contextlib.redirect_stdout(io.StringIO()):
            for _ in range(2 if repeat else 1):
                runpy.run_path(str(root/'scripts/update_eps_revision.py'))
        return json.loads((root/'data/eps_revision_proxy.json').read_text()),json.loads((root/'data/eps_revision_history.json').read_text())

def matrix():
    _,s=dashboard()
    cases=[('HIGH','HIGH','NEGATIVE','RED'),('HIGH','HIGH','WEAKENING','ORANGE'),('HIGH','HIGH','STRONG','YELLOW-ORANGE'),('LOW','MODERATE','STRONG','GREEN')]
    got=[s['regime'](*x[:3]) for x in cases]
    return got==[x[3] for x in cases],got

def corrupt():
    try:
        d,_=dashboard(broken=True)
        return d['pillars']['earnings']['source_mode']=='FALLBACK',d['pillars']['earnings']
    except json.JSONDecodeError:
        return False,'Invalid proxy JSON aborts the entire dashboard update before fallback.'

before=digest()
check('regime_core_matrix',matrix)
check('fresh_proxy_selected',lambda: ((d:=dashboard(proxy())[0])['pillars']['earnings']['source_mode']=='AUTO_PROXY',d['pillars']['earnings']))
check('expired_proxy_falls_back',lambda: ((d:=dashboard(proxy(as_of=(TODAY-timedelta(days=11)).isoformat()))[0])['pillars']['earnings']['source_mode']=='FALLBACK',d['pillars']['earnings']))
check('term_premium_outage_is_missing_not_zero',lambda: ((d:=dashboard(tp_failure=True)[0])['pillars']['discount']['term_premium'] is None and d['data_quality']['term_premium']=='UNAVAILABLE',d['data_quality']))
check('corrupt_proxy_recovers_to_fallback',corrupt)
check('future_dated_proxy_rejected',lambda: ((d:=dashboard(proxy(as_of=(TODAY+timedelta(days=30)).isoformat()))[0])['pillars']['earnings']['source_mode']!='AUTO_PROXY',d['pillars']['earnings']))
check('obsolete_fallback_does_not_assert_strong_earnings',lambda: ((d:=dashboard(stale=True)[0])['pillars']['earnings']['state']!='STRONG',d['pillars']['earnings']))
check('rate_change_uses_common_asof',lambda: ((d:=dashboard(desync=True)[0])['pillars']['discount']['real_1m_change_bp']==0,{'as_of':d['as_of'],'real':d['pillars']['discount']['real10y'],'delta':d['pillars']['discount']['real_1m_change_bp']}))
check('duplicate_share_classes_preserve_weights',lambda: ((d:=eps()[0])['companies_used']==2 and abs(d['coverage_weight']-.1)<1e-8 and abs(d['revision_60d_pct']-10)<1e-8,d))
check('loss_reduction_not_classified_negative_revision',lambda: ((d:=eps(negative=True)[0])['revision_60d_pct']>=0,d))
check('negligible_coverage_not_accepted_as_market_signal',lambda: ((d:=dashboard(proxy(coverage_weight=.001))[0])['pillars']['earnings']['source_mode']!='AUTO_PROXY',d['pillars']['earnings']))
check('top_holdings_selected_by_weight',lambda: ((lambda d: ('LARGE' in [r['symbol'] for r in d['constituents']],d))(eps(unsorted=True)[0])))
check('same_day_eps_rerun_is_idempotent',lambda: (len(h:=eps(repeat=True)[1])==1,h))
sample=json.loads((SOURCE/'data/latest.json').read_text())
check('packaged_rates_arithmetic',lambda: (abs(sample['context']['nominal10y']-sample['pillars']['discount']['real10y']-sample['pillars']['discount']['breakeven10y'])<.03,{'nominal':sample['context']['nominal10y'],'real':sample['pillars']['discount']['real10y'],'breakeven':sample['pillars']['discount']['breakeven10y']}))
check('loss_worsening_has_negative_direction',lambda: ((d:=eps(current=-3,prior=-2)[0])['revision_60d_pct']==-50,d['revision_60d_pct']))
check('loss_to_profit_has_positive_direction',lambda: ((d:=eps(current=1,prior=-2)[0])['revision_60d_pct']==150,d['revision_60d_pct']))
check('profit_to_loss_has_negative_direction',lambda: ((d:=eps(current=-1,prior=2)[0])['revision_60d_pct']==-150,d['revision_60d_pct']))
check('insufficient_company_count_rejected',lambda: ((d:=dashboard(proxy(companies_used=1))[0])['pillars']['earnings']['source_mode']=='FALLBACK',d['pillars']['earnings']))
check('coverage_and_company_threshold_inclusive',lambda: ((d:=dashboard(proxy(coverage_weight=.3,companies_used=10))[0])['pillars']['earnings']['source_mode']=='AUTO_PROXY',d['pillars']['earnings']))
check('nonfinite_proxy_rejected',lambda: ((d:=dashboard(proxy(revision_60d_pct=float('nan')))[0])['pillars']['earnings']['source_mode']=='FALLBACK',d['pillars']['earnings']))
check('nonobject_proxy_recovers',lambda: ((d:=dashboard(proxy=[])[0])['pillars']['earnings']['source_mode']=='FALLBACK',d['pillars']['earnings']))
check('fallback_age_14_accepted',lambda: ((d:=dashboard(fallback_age=14)[0])['pillars']['earnings']['quality']=='CURRENT',d['pillars']['earnings']))
check('fallback_age_15_blocks_regime',lambda: ((d:=dashboard(fallback_age=15)[0])['regime']=='UNDETERMINED' and d['pillars']['earnings']['revision_surprise'] is None,d['pillars']['earnings']))
check('future_fallback_blocks_regime',lambda: ((d:=dashboard(fallback_age=-1)[0])['regime']=='UNDETERMINED',d['pillars']['earnings']))
check('expired_pe_blocks_regime',lambda: ((d:=dashboard(pe_age=15)[0])['regime']=='UNDETERMINED',d['pillars']['valuation']))
check('bad_proxy_and_stale_fallback_blocks_regime',lambda: ((d:=dashboard(broken=True,stale=True)[0])['regime']=='UNDETERMINED',d['pillars']['earnings']))
check('fred_term_premium_own_date_and_delta',lambda: ((d:=dashboard(tp_age=3)[0])['pillars']['discount']['term_premium_1m_change_bp']==10 and d['pillars']['discount']['term_premium_as_of']==(TODAY-timedelta(days=3)).isoformat(),d['pillars']['discount']))
check('stale_term_premium_visible_but_flagged',lambda: ((d:=dashboard(tp_age=10)[0])['pillars']['discount']['term_premium']==.9 and d['data_quality']['term_premium']=='STALE',d['pillars']['discount']))
check('source_unchanged',lambda: (before==digest(),'SHA-256 comparison of every source file'))
report={'date':TODAY.isoformat(),'mode':'offline fixtures; unchanged scripts in temporary copies','results':RESULTS}
(BASE/'tests/results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
for r in RESULTS: print(r['status'],r['name'])
print(json.dumps({s:sum(r['status']==s for r in RESULTS) for s in ['PASS','FAIL','ERROR']}))

if any(r['status']!='PASS' for r in RESULTS): raise SystemExit(1)
