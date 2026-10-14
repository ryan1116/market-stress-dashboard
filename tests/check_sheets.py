"""Run: python3 tests/check_sheets.py. No credentials or network required."""
import csv
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('sync_sheets', ROOT/'scripts/sync_sheets.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
tables = m.payload()
requests = m.batch(tables, {}, {})
assert len([r for r in requests if 'addSheet' in r]) == 4
assert all(len(r) == 1 for r in requests)
assert m.cell_value('=IMPORTXML("private")') == {'stringValue': '=IMPORTXML("private")'}
existing = {'MSD_Latest': {'sheetId': 123, 'gridProperties': {'rowCount': 1000, 'columnCount': 5}}}
try:
    m.batch(tables, existing, {'MSD_Latest': 'User notes'})
    raise AssertionError('Unmanaged tab overwritten')
except ValueError:
    pass
updates = m.batch(tables, existing, {'MSD_Latest': m.MARKER})
update = next(r['updateCells'] for r in updates if r.get('updateCells', {}).get('range', {}).get('sheetId') == 123)
assert update['range']['endRowIndex'] == 1000  # clears remnants when input shrinks
assert update['fields'] == 'userEnteredValue'  # preserves unrelated formatting
with tempfile.TemporaryDirectory() as td:
    fixture = Path(td)/'latest.csv'
    with fixture.open('w', newline='') as file:
        csv.writer(file).writerows(tables['MSD_Latest'])
    js = r'''
const fs=require('fs'),assert=require('assert');
const {parseCSV,sheetPayload}=require(process.argv[1]);
const raw=fs.readFileSync(process.argv[2],'utf8');
const expected=JSON.parse(fs.readFileSync(process.argv[3],'utf8'));
const now=Date.parse(expected.generated_at);
assert.deepEqual(JSON.parse(JSON.stringify(sheetPayload(raw,now)[0])),expected);
assert.deepEqual(parseCSV('a,b,c\r\n"a,b","x""y","line\nbreak"\r\n'),[['a','b','c'],['a,b','x"y','line\nbreak']]);
for(const bad of [raw+'dashboard.__proto__.x,string,bad\r\n',raw+'dashboard.regime,string,RED\r\n',raw.replace('msd_path_v1','bad'),raw.replace('dashboard.regime,string,'+expected.regime,'dashboard.regime,string,<script>')])assert.throws(()=>sheetPayload(bad,now));
assert.throws(()=>sheetPayload(raw,now+5*86400000));
assert.throws(()=>sheetPayload(raw.replace('dashboard.pillars.valuation.forward_pe,number,'+expected.pillars.valuation.forward_pe,'dashboard.pillars.valuation.forward_pe,number,null'),now));
console.log('PASS: CSV round trip, quotes/newlines, duplicate/prototype rejection, stale and malformed data');
'''
    subprocess.run(['node','-e',js,str(ROOT/'data-backend.js'),str(fixture),str(ROOT/'data/latest.json')],check=True)
print('PASS: atomic write plan, unmanaged-tab preservation, safe cell values, shrinking ranges')
