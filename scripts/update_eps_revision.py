
import json, math, os, time, urllib.parse, urllib.request
from pathlib import Path
from datetime import date, datetime, timezone, timedelta

ROOT=Path(__file__).resolve().parents[1]
CFG=json.loads((ROOT/"config/eps_proxy_config.json").read_text(encoding="utf-8"))
OUT=ROOT/"data/eps_revision_proxy.json"
HIST=ROOT/"data/eps_revision_history.json"
KEY=os.environ.get("ALPHAVANTAGE_API_KEY")
if not KEY:
    raise SystemExit("ALPHAVANTAGE_API_KEY GitHub secret is required")

BASE="https://www.alphavantage.co/query"

def api(function, **kwargs):
    q={"function":function,"apikey":KEY,**kwargs}
    url=BASE+"?"+urllib.parse.urlencode(q)
    with urllib.request.urlopen(url,timeout=45) as r:
        obj=json.loads(r.read().decode("utf-8"))
    if "Information" in obj or "Note" in obj or "Error Message" in obj:
        raise RuntimeError(str(obj))
    return obj

def canon(s):
    return CFG.get("canonical_symbols",{}).get(s,s)

def num(x):
    try:
        value=float(x)
        return value if math.isfinite(value) else None
    except (TypeError,ValueError): return None

def pick_fy(estimates):
    today=date.today()
    cutoff=today+timedelta(days=int(CFG["minimum_days_to_fiscal_end"]))
    rows=[]
    for x in estimates:
        if x.get("horizon")!="fiscal year": continue
        try: d=date.fromisoformat(x["date"])
        except Exception: continue
        if d>=cutoff: rows.append((d,x))
    return min(rows,key=lambda z:z[0])[1] if rows else None

etf=api("ETF_PROFILE",symbol=CFG["etf"])
holdings=sorted((h for h in etf.get("holdings",[]) if num(h.get("weight")) is not None and num(h["weight"])>0),
                key=lambda h:num(h["weight"]),reverse=True)[:int(CFG["max_holdings"]) ]

# De-duplicate dual share classes after preserving combined SPY weight.
issuer={}
for h in holdings:
    s=canon(h["symbol"])
    w=num(h.get("weight")) or 0.0
    issuer[s]=issuer.get(s,0.0)+w

rows=[]
for i,(symbol,weight) in enumerate(issuer.items()):
    try:
        obj=api("EARNINGS_ESTIMATES",symbol=symbol)
        fy=pick_fy(obj.get("estimates",[]))
        if not fy: continue
        cur=num(fy.get("eps_estimate_average"))
        d30=num(fy.get("eps_estimate_average_30_days_ago"))
        d60=num(fy.get("eps_estimate_average_60_days_ago"))
        d90=num(fy.get("eps_estimate_average_90_days_ago"))
        if cur is None or d60 in (None,0): continue
        up=num(fy.get("eps_estimate_revision_up_trailing_30_days")) or 0
        down=num(fy.get("eps_estimate_revision_down_trailing_30_days")) or 0
        rows.append({
          "symbol":symbol,"spy_weight":weight,"fiscal_year_end":fy["date"],
          "analyst_count":num(fy.get("eps_estimate_analyst_count")),
          "revision_30d_pct":None if d30 in (None,0) else 100*(cur-d30)/abs(d30),
          "revision_60d_pct":100*(cur-d60)/abs(d60),
          "revision_90d_pct":None if d90 in (None,0) else 100*(cur-d90)/abs(d90),
          "up_30d":up,"down_30d":down
        })
    except Exception as ex:
        print("skip",symbol,ex)
    # Avoid burst-rate failures; weekly job is not latency sensitive.
    time.sleep(1.1)

covered=sum(r["spy_weight"] for r in rows)
if covered<=0: raise RuntimeError("No usable earnings-estimate rows")

def wavg(field):
    xs=[r for r in rows if r[field] is not None]
    den=sum(r["spy_weight"] for r in xs)
    return sum(r["spy_weight"]*r[field] for r in xs)/den if den else None

up=sum(r["up_30d"] for r in rows)
down=sum(r["down_30d"] for r in rows)
analyst_breadth=(up-down)/(up+down) if (up+down)>0 else None
company_positive=sum(r["spy_weight"] for r in rows if r["revision_60d_pct"]>0)/covered
rev60=wavg("revision_60d_pct")

hist=json.loads(HIST.read_text(encoding="utf-8")) if HIST.exists() else []
# Retain one observation per date, and never let today's reruns enter their own baseline.
hist=list({x["as_of"]:x for x in hist if x.get("as_of") and x["as_of"]<date.today().isoformat()}.values())
# Once we have ~1 year of weekly observations, use same-week-of-year historical
# proxy observations as an empirical seasonal baseline. Until then use the
# explicitly labeled provisional benchmark in config.
baseline=float(CFG["seasonal_benchmark_60d"])
baseline_mode="PROVISIONAL_CONFIG"
if CFG.get("enable_empirical_baseline",False) and len(hist)>=int(CFG["history_min_observations_for_empirical_baseline"]):
    month=date.today().month
    seasonal=[x["revision_60d_pct"] for x in hist
              if x.get("as_of","")[5:7]==f"{month:02d}" and x.get("revision_60d_pct") is not None]
    if len(seasonal)>=3:
        seasonal=sorted(seasonal)
        baseline=seasonal[len(seasonal)//2]
        baseline_mode="EMPIRICAL_SAME_MONTH_MEDIAN"

out={
 "as_of":datetime.now(timezone.utc).date().isoformat(),
 "method":"SPY top-holdings weighted signed EPS revision: 100 * (current - prior) / abs(prior)",
 "revision_formula":"100 * (current - prior) / abs(prior); zero prior excluded",
 "source":"Alpha Vantage ETF_PROFILE + EARNINGS_ESTIMATES",
 "coverage_weight":round(covered,4),
 "companies_used":len(rows),
 "revision_30d_pct":round(wavg("revision_30d_pct"),3) if wavg("revision_30d_pct") is not None else None,
 "revision_60d_pct":round(rev60,3),
 "revision_90d_pct":round(wavg("revision_90d_pct"),3) if wavg("revision_90d_pct") is not None else None,
 "seasonal_benchmark_60d":round(baseline,3),
 "baseline_mode":baseline_mode,
 "revision_surprise_60d":round(rev60-baseline,3),
 "analyst_revision_breadth_30d":round(analyst_breadth,3) if analyst_breadth is not None else None,
 "positive_company_weight_60d":round(company_positive,3),
 "constituents":rows
}
OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding="utf-8")
hist.append({k:v for k,v in out.items() if k!="constituents"})
hist.sort(key=lambda x:x["as_of"])
HIST.write_text(json.dumps(hist[-260:],ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({k:out[k] for k in ["as_of","coverage_weight","companies_used","revision_60d_pct","revision_surprise_60d","analyst_revision_breadth_30d","baseline_mode"]},indent=2))
