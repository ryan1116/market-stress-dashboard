"""Validate complete DART list pages and publish a dated six-calendar-month window."""
import argparse
import calendar
import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def six_months_before(end):
    month = end.year * 12 + end.month - 1 - 6
    year, m = divmod(month, 12)
    return date(year, m + 1, min(end.day, calendar.monthrange(year, m + 1)[1]))


def build(pages, end):
    start = six_months_before(end)
    if not pages: raise ValueError('Missing DART response')
    if len(pages) == 1 and pages[0].get('status') == '013':
        rows = []
    else:
        total = int(pages[0]['total_count']); count = int(pages[0]['total_page'])
        if len(pages) != count or {int(p['page_no']) for p in pages} != set(range(1, count+1)):
            raise ValueError('Incomplete DART pagination')
        rows = []
        for p in pages:
            if p.get('status') != '000' or int(p['total_count']) != total or int(p['total_page']) != count:
                raise ValueError('DART error or changing result set; retry full query')
            rows.extend(p['list'])
        if len(rows) != total: raise ValueError('DART count mismatch')
    result = []
    for r in rows:
        if r['corp_code'] != '00269922' or not re.fullmatch(r'\d{14}', r['rcept_no']):
            raise ValueError('Unexpected issuer or receipt number')
        observed = date.fromisoformat(r['rcept_dt'])
        if not start <= observed <= end: raise ValueError('Outside six-month query window')
        result.append({'date':observed.isoformat(),'title':r['report_nm'].strip(),'filer':r['flr_nm'],
                       'receipt':r['rcept_no'],'remarks':r.get('rm',''),
                       'url':'https://dart.fss.or.kr/dsaf001/main.do?rcpNo='+r['rcept_no']})
    if len({r['receipt'] for r in result}) != len(result): raise ValueError('Duplicate receipts')
    return {'source':'DART 공시검색','corp_code':'00269922','as_of':end.isoformat(),'from':start.isoformat(),
            'to':end.isoformat(),'includes_corrections':True,'total':len(result),
            'items':sorted(result,key=lambda r:(r['date'],r['receipt']),reverse=True)}


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--pages',type=Path,required=True);p.add_argument('--as-of',type=date.fromisoformat,required=True);a=p.parse_args()
    data=build(json.loads(a.pages.read_text()),a.as_of)
    target=ROOT/'data/investments/disclosures.json';tmp=target.with_suffix('.tmp')
    tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n');tmp.replace(target)
    print(f"Validated {data['total']} disclosures: {data['from']} through {data['to']}")
