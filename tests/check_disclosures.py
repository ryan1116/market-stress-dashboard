import json
import sys
from copy import deepcopy
from datetime import date
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from update_disclosures import build,six_months_before
assert six_months_before(date(2026,8,31))==date(2026,2,28)
row={'corp_code':'00269922','rcept_no':'20261002000146','rcept_dt':'20261002','report_nm':'보고서','flr_nm':'인바디','rm':''}
p={'status':'000','page_no':1,'total_count':1,'total_page':1,'list':[row]}
assert build([p],date(2026,10,19))['total']==1
assert build([{'status':'013'}],date(2026,10,19))['items']==[]
for mutate in [lambda x:x.update(total_page=2),lambda x:x.update(total_count=2),lambda x:x['list'][0].update(corp_code='other'),lambda x:x['list'][0].update(rcept_dt='20260101')]:
 bad=deepcopy(p);mutate(bad)
 try:build([bad],date(2026,10,19))
 except ValueError:pass
 else:raise AssertionError('Invalid page accepted')
d=json.loads((Path(__file__).resolve().parents[1]/'data/investments/disclosures.json').read_text())
assert len(d['items'])==d['total'] and len({r['receipt'] for r in d['items']})==d['total']
print('PASS: six-month boundaries, complete pagination, issuer, date window, empty result and unique receipts')
