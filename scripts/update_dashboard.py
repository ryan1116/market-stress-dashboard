
import io,json,math,urllib.request
from pathlib import Path
from datetime import date,datetime,timedelta
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
LATEST=ROOT/"data/latest.json"; HISTORY=ROOT/"data/history.json"
MANUAL=json.loads((ROOT/"config/manual_metrics.json").read_text(encoding="utf-8"))
EPS_PROXY=ROOT/"data/eps_revision_proxy.json"
POLICY=json.loads((ROOT/"config/data_policy.json").read_text())
TODAY=datetime.now().date()
WARNINGS=[]
def finite(value):
    number=float(value)
    if not math.isfinite(number): raise ValueError("non-finite value")
    return number

def freshness(value, max_days):
    try:
        age=(TODAY-date.fromisoformat(value)).days
        return "FUTURE" if age<0 else ("STALE" if age>max_days else "CURRENT")
    except (ValueError,TypeError): return "INVALID_DATE"

def rounded(value, digits=2):
    return None if value is None else round(value,digits)


def fred(s):
    u=f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={s}"
    with urllib.request.urlopen(u,timeout=30) as r: df=pd.read_csv(io.BytesIO(r.read()))
    df.columns=["date","value"]; df["date"]=pd.to_datetime(df["date"]); df["value"]=pd.to_numeric(df["value"],errors="coerce")
    return df.dropna().query("date <= @TODAY").sort_values("date")
def before(df,t):
    x=df[df.date<=t]; return float(x.iloc[-1].value)
def delta(df,days,asof):
    old=before(df,asof-pd.Timedelta(days=days))
    return round((before(df,asof)-old)*100,1)
def termpremium(asof):
    frame=fred("THREEFYTP10")
    frame=frame[frame.date<=asof]
    if frame.empty: raise ValueError("No term premium observation on or before rates date")
    last=frame.iloc[-1]
    # The term premium has its own publication lag. Anchor its change to its own observation date.
    old=frame[frame.date<=last.date-pd.Timedelta(days=30)]
    change=None if old.empty else round((float(last.value)-float(old.iloc[-1].value))*100,1)
    return round(float(last.value),4),change,last.date.date().isoformat()

def vstate(g): return "HIGH" if g<2.5 else ("ELEVATED" if g<4 else "LOW")
def dstate(r1,r3,tp):
    if r1>=25 or r3>=50 or (tp is not None and tp>=15): return "HIGH"
    if r1<=-25 and r3<=-40: return "EASING"
    return "MODERATE"
def estate(s):
    if s>1: return "STRONG"
    if s>=-1:return "NEUTRAL"
    if s>-3:return "WEAKENING"
    return "NEGATIVE"
def regime(v,d,e):
    if "UNAVAILABLE" in (v,d,e): return "UNDETERMINED"
    if v=="HIGH" and d=="HIGH" and e=="NEGATIVE":return "RED"
    if v=="HIGH" and d=="HIGH" and e=="WEAKENING":return "ORANGE"
    if v=="HIGH" and d=="HIGH" and e=="STRONG":return "YELLOW-ORANGE"
    if v=="HIGH" and d=="HIGH":return "ORANGE"
    if d=="HIGH" and e=="NEGATIVE":return "ORANGE"
    if v=="LOW" and d!="HIGH" and e=="STRONG":return "GREEN"
    return "YELLOW"

dfs={s:fred(s) for s in ["DGS10","DFII10","T10YIE"]}
common=set(dfs["DGS10"].date)
for frame in dfs.values(): common.intersection_update(frame.date)
if not common: raise RuntimeError("No common rates observation date")
asof=max(common)
nom=before(dfs["DGS10"],asof); real=before(dfs["DFII10"],asof); bei=before(dfs["T10YIE"],asof)
r1=delta(dfs["DFII10"],30,asof); r3=delta(dfs["DFII10"],90,asof)
rates_status=freshness(asof.date().isoformat(),POLICY["rates_max_age_days"])
try:
    tp,tp1,tpdate=termpremium(asof)
    tpq="AUTO" if freshness(tpdate,POLICY["rates_max_age_days"])=="CURRENT" else "STALE"
    if tpq=="STALE": WARNINGS.append("Term premium stale: displayed for reference, excluded from shock signal")
except Exception as ex:
    print(type(ex).__name__); tp=tp1=tpdate=None; tpq="UNAVAILABLE"

pe=finite(MANUAL["forward_pe"]["value"])
if pe<=0: raise ValueError("Forward P/E must be positive")
ey=100/pe; gap=round(ey-real,2)
pe_status=freshness(MANUAL["forward_pe"].get("as_of"),POLICY["forward_pe_max_age_days"])
earn_mode="FALLBACK"; coverage=breadth=posweight=companies=None
fb=MANUAL["eps_fallback"]
rev=bench=None; es_asof=fb.get("as_of"); baseline_mode="FACTSET_FALLBACK"
earnings_status=freshness(es_asof,POLICY["fallback_max_age_days"])
try:
    rev=finite(fb["revision_60d"]); bench=finite(fb["seasonal_benchmark_60d"])
except (ValueError,TypeError,KeyError): earnings_status="INVALID_VALUE"
if EPS_PROXY.exists():
    try:
        p=json.loads(EPS_PROXY.read_text(encoding="utf-8"))
        if not isinstance(p,dict): raise ValueError("proxy must be a JSON object")
        if freshness(p.get("as_of"),POLICY["proxy_max_age_days"])!="CURRENT":
            raise ValueError("proxy date not current")
        candidate_coverage=finite(p["coverage_weight"])
        candidate_companies=finite(p["companies_used"])
        if not POLICY["minimum_coverage_weight"]<=candidate_coverage<=1:
            raise ValueError("insufficient or invalid coverage")
        if candidate_companies<POLICY["minimum_companies"] or not candidate_companies.is_integer():
            raise ValueError("insufficient or invalid company count")
        candidate_rev=finite(p["revision_60d_pct"]); candidate_bench=finite(p["seasonal_benchmark_60d"])
        rev,bench=candidate_rev,candidate_bench; es_asof=p["as_of"]
        coverage=candidate_coverage; companies=int(candidate_companies)
        breadth=p.get("analyst_revision_breadth_30d"); posweight=p.get("positive_company_weight_60d")
        baseline_mode=p.get("baseline_mode"); earn_mode="AUTO_PROXY"; earnings_status="CURRENT"
    except (OSError,ValueError,TypeError,KeyError) as ex:
        WARNINGS.append("Proxy rejected: "+str(ex))
if earnings_status!="CURRENT": WARNINGS.append("Earnings input: "+earnings_status)
surprise=rounded(rev-bench) if earnings_status=="CURRENT" else None
vs=vstate(gap) if pe_status=="CURRENT" and rates_status=="CURRENT" else "UNAVAILABLE"
ds=dstate(r1,r3,tp1 if tpq=="AUTO" else None) if rates_status=="CURRENT" else "UNAVAILABLE"
es=estate(surprise) if surprise is not None else "UNAVAILABLE"
rg=regime(vs,ds,es)

data={"version":"0.2.3","generated_at":datetime.now().astimezone().isoformat(),"rate_sources":{s:f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={s}" for s in dfs},"as_of":asof.date().isoformat(),"regime":rg,
"regime_note":f"{vs} valuation vulnerability + {ds} discount-rate shock + {es} earnings confirmation.",
"pillars":{
 "valuation":{"label":"Valuation Vulnerability","state":vs,"equity_yield_gap":gap,"forward_earnings_yield":round(ey,2),"forward_pe":pe,"as_of":MANUAL["forward_pe"].get("as_of"),"real10y":round(real,2)},
 "discount":{"label":"Discount-Rate Shock","state":ds,"real10y":round(real,2),"real_1m_change_bp":r1,"real_3m_change_bp":r3,"term_premium":tp,"term_premium_1m_change_bp":tp1,"term_premium_as_of":tpdate,"term_premium_quality":tpq,"term_premium_source":"https://fred.stlouisfed.org/series/THREEFYTP10","breakeven10y":round(bei,2)},
 "earnings":{"label":"Earnings Confirmation","state":es,"source_mode":earn_mode,"revision_60d":rounded(rev),"seasonal_benchmark_60d":rounded(bench),"revision_surprise":surprise,"baseline_mode":baseline_mode,"coverage_weight":coverage,"companies_used":companies,"quality":earnings_status,"analyst_revision_breadth":breadth,"positive_company_weight":posweight,"as_of":es_asof}},
"context":{"nominal10y":round(nom,2),"ai_credit_premium_bp":float(MANUAL["ai_credit_premium_bp"]["value"])},
"data_quality":{"rates":"AUTO" if rates_status=="CURRENT" else rates_status,"term_premium":tpq,"forward_pe":"MANUAL" if pe_status=="CURRENT" else pe_status,"earnings":earnings_status,"earnings_source":earn_mode,"ai_credit":"MANUAL","warnings":WARNINGS}}
LATEST.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
hist=json.loads(HISTORY.read_text(encoding="utf-8"))
hist=[row for row in hist if row.get("as_of")!=data["as_of"]]
hist.append(data)
hist.sort(key=lambda row:row["as_of"])
HISTORY.write_text(json.dumps(hist[-730:],ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({"regime":rg,"earnings":data["pillars"]["earnings"]},ensure_ascii=False))
