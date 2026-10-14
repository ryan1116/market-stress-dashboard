"""Offline collector checks: python3 tests/check_forward_pe.py."""
import contextlib
import importlib.util
import io
import json
from datetime import date, timedelta
from pathlib import Path
import tempfile
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('forward_pe', Path(__file__).resolve().parents[1] / 'scripts/update_forward_pe.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
day = date(2026, 10, 9)
text = 'EARNINGS INSIGHT\nOctober 9, 2026\nThe forward 12-month P/E ratio for the S&P 500 is 19.1.'
assert m.parse_report(text, day, day) == 19.1
assert m.parse_report(text, day, day + timedelta(days=14)) == 19.1
for bad_text, expected, today in [
    (text, day, day + timedelta(days=15)),
    (text, day, day - timedelta(days=1)),
    (text, day - timedelta(days=7), day),
    (text.replace('19.1', '0'), day, day),
    (text.replace('forward 12-month', 'trailing 12-month'), day, day),
    (text + text, day, day),
    ('Login required', day, day),
]:
    try:
        m.parse_report(bad_text, expected, today)
        raise AssertionError('Invalid report accepted')
    except ValueError:
        pass
with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    (root/'data').mkdir()
    (root/'config').mkdir()
    (root/'config/data_policy.json').write_text('{"forward_pe_max_age_days":14}')
    target = root/'data/forward_pe.json'
    original = '{"value":18.9,"as_of":"2026-09-21"}'
    target.write_text(original)
    with patch.object(m, 'ROOT', root), patch.object(m.urllib.request, 'urlopen', side_effect=OSError('offline')), contextlib.redirect_stdout(io.StringIO()):
        m.refresh(day)
    assert target.read_text() == original
    with patch.object(m, 'ROOT', root), patch.object(m.urllib.request, 'urlopen', return_value=io.BytesIO(b'%PDF-fixture')), patch.object(m.subprocess, 'run') as run, contextlib.redirect_stdout(io.StringIO()):
        run.return_value.stdout = text.encode()
        m.refresh(day)
    saved = json.loads(target.read_text())
    assert saved['value'] == 19.1 and saved['as_of'] == '2026-10-09'
    assert saved['date_type'] == 'REPORT_DATE' and saved['source_url'].endswith('100926.pdf')
print('PASS: report parsing, date limits, invalid reports, outage preservation, saved provenance')
