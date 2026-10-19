"""Publish a validated Sheets CellData snapshot, without changing financial assumptions.

Read private Sheets through the authorized connector and save its structuredContent
outside this repository. This script exports only the explicit public allowlist.
"""
import argparse
import json
import math
import subprocess
import tempfile
from datetime import date
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
RANGES=["'Valuation summary'!A1:B49", "'매출성장률'!A4:M34", "'Assumptions'!A1:B16", "'DCF (Normal)'!B4:M29", "'INPUT'!B15:B20", "'최신자료'!A52:B69", "'Net debt'!B22"]


def number(data, sheet, row, col):
    for s in data['sheets']:
        if s['properties']['title']!=sheet: continue
        for block in s.get('data',[]):
            r=row-1-block.get('startRow',0);c=col-1-block.get('startColumn',0)
            rows=block.get('rowData',[])
            if 0<=r<len(rows):
                cells=rows[r].get('values',[])
                if 0<=c<len(cells):
                    value=cells[c].get('effectiveValue',{}).get('numberValue')
                    if isinstance(value,(float,int)) and not isinstance(value,bool) and math.isfinite(value): return value
    raise ValueError(f'Missing numeric value: {sheet}!row{row} col{col}')


def export(data, previous, price_date):
    d=json.loads(json.dumps(previous))
    n=lambda s,r,c=2:number(data,s,r,c)
    summary=lambda r:n('Valuation summary',r)
    # Excel serial uses 1899-12-30. Model date is read, never advanced by collection.
    from datetime import timedelta
    d['model_as_of']=(date(1899,12,30)+timedelta(days=summary(38))).isoformat()
    date.fromisoformat(price_date);d['price']['as_of']=price_date;d['price']['value']=summary(23)
    d['weighted_value']=summary(33)
    for i,s in enumerate(d['scenarios']):
        s.update(value=summary(18+i),weight=summary(29+i),terminal_growth=n('매출성장률',5+i,13),growth=[n('매출성장률',5+i,c) for c in range(3,13)],margins=[n('매출성장률',14+i,c) for c in range(3,13)])
    d['years']=[int(n('DCF (Normal)',4,c)) for c in range(3,13)]
    d['normal_revenue']=[n('DCF (Normal)',5,c) for c in range(3,13)]
    d['normal_fcf']=[n('DCF (Normal)',14,c) for c in range(3,13)]
    d['assumptions'].update(wacc=summary(43),tax=n('Assumptions',7),opening_wc=n('최신자료',67),wc_ratio=n('최신자료',69),operating_cash=n('Net debt',22),beta=n('INPUT',17),kd=n('INPUT',18),erp=n('INPUT',19),net_debt_adjustment=summary(9),shares=summary(16))
    return d


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--cells',type=Path,required=True);p.add_argument('--price-date',required=True,help='Actual observed price date, not collection date');p.add_argument('--review',type=Path,required=True,help='JSON: date, note, review (status, decision, triggers), limitations, sources');p.add_argument('--dry-run',action='store_true');a=p.parse_args()
    target=ROOT/'data/investments/inbody.json';previous=json.loads(target.read_text());raw=json.loads(a.cells.read_text());data=export(raw.get('structuredContent',raw),previous,a.price_date)
    review=json.loads(a.review.read_text());date.fromisoformat(review['date'])
    for key in ('review','limitations','sources'):data[key]=review[key]
    data['reviewed_at']=review['date']
    if not review.get('note'):raise ValueError('Change/review note is required')
    encoded=json.dumps(data,ensure_ascii=False,indent=2,allow_nan=False)+'\n'
    subprocess.run(['node','-e',"const {validateSnapshot}=require('./investments.js');validateSnapshot(JSON.parse(require('fs').readFileSync(0,'utf8')));"],input=encoded,text=True,cwd=ROOT,check=True)
    history_path=target.with_name('history.json');history=json.loads(history_path.read_text());entry={'date':review['date'],'weighted_value':data['weighted_value'],'normal_value':data['scenarios'][1]['value'],'note':review['note']}
    # Preserve prior decisions, including multiple decisions on the same day.
    if not history or history[-1]!=entry:history.append(entry)
    if a.dry_run:print('Validated; no files changed');return
    for path,value in [(target,data),(history_path,history)]:
        with tempfile.NamedTemporaryFile('w',dir=path.parent,delete=False,encoding='utf-8') as f:json.dump(value,f,ensure_ascii=False,indent=2,allow_nan=False);tmp=Path(f.name)
        tmp.replace(path)
    print('Published local snapshot; commit/deploy separately')

if __name__=='__main__':main()
