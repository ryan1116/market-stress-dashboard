"""Check quote/date/source integrity against a private captured Sheets snapshot."""
import copy
import json
import sys
from pathlib import Path
from datetime import date, timedelta

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from update_investment import export, number

data = json.loads(Path(sys.argv[1]).read_text())
previous = json.loads((Path(__file__).resolve().parents[1] / 'data/investments/inbody.json').read_text())
day = (date(1899, 12, 30) + timedelta(days=number(data, '자동데이터', 10, 2))).isoformat()
result = export(data, previous, day)
assert result['price']['value'] == number(data, '자동데이터', 9, 2)
assert result['price']['source']
assert abs(sum(s['value'] * s['weight'] for s in result['scenarios']) - result['weighted_value']) < .01
try:
    export(data, previous, '2000-01-01')
except ValueError:
    pass
else:
    raise AssertionError('Mismatched price date was accepted')
broken = copy.deepcopy(data)
broken['sheets'] = [s for s in broken['sheets'] if s['properties']['title'] != '자동데이터']
try:
    export(broken, previous, day)
except ValueError:
    pass
else:
    raise AssertionError('Missing price metadata was accepted')
print('PASS: automatic quote, source, date, weights, missing metadata')
