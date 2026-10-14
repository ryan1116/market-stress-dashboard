"""Collect FactSet's weekly index forward P/E; retain the last verified report on failure."""
import json
import re
import subprocess
import urllib.error
import urllib.request
from datetime import date, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE_URL = 'https://advantage.factset.com/hubfs/Website/Resources%20Section/Research%20Desk/Earnings%20Insight/'


def parse_report(text, expected, today, max_age=14):
    first_page = ' '.join(text.split('\f')[0].split())
    dates = re.findall(r'\b([A-Z][a-z]+ \d{1,2}, \d{4})\b', first_page)
    if not dates or datetime.strptime(dates[0], '%B %d, %Y').date() != expected:
        raise ValueError('Report date does not match requested edition')
    if not 0 <= (today - expected).days <= max_age:
        raise ValueError('Report is expired or future-dated')
    matches = re.findall(r'The forward 12-month P/E ratio for the S&P 500 is (\d+(?:\.\d+)?)\.', first_page)
    if len(matches) != 1 or not 0 < float(matches[0]) < 100:
        raise ValueError('Missing, ambiguous, or invalid index forward P/E')
    return float(matches[0])


def refresh(today=None):
    today = today or date.today()
    target = ROOT / 'data/forward_pe.json'
    policy = json.loads((ROOT / 'config/data_policy.json').read_text())
    # ponytail: standard Friday editions only; fail closed if FactSet changes its publication pattern or layout.
    friday = today - timedelta(days=(today.weekday() - 4) % 7)
    for offset in range(0, policy['forward_pe_max_age_days'] + 1, 7):
        edition = friday - timedelta(days=offset)
        if (today - edition).days > policy['forward_pe_max_age_days']:
            continue
        url = BASE_URL + 'EarningsInsight_' + edition.strftime('%m%d%y') + '.pdf'
        try:
            with urllib.request.urlopen(url, timeout=30) as response:
                pdf = response.read(20_000_001)
            if len(pdf) > 20_000_000 or not pdf.startswith(b'%PDF-'):
                raise ValueError('Invalid PDF response')
            text = subprocess.run(['pdftotext', '-f', '1', '-l', '1', '-', '-'], input=pdf,
                                  capture_output=True, check=True, timeout=30).stdout.decode('utf-8')
            value = parse_report(text, edition, today, policy['forward_pe_max_age_days'])
            record = dict(value=value, as_of=edition.isoformat(), date_type='REPORT_DATE',
                          source='FactSet Earnings Insight', source_url=url, source_mode='AUTO')
            if target.exists():
                previous = json.loads(target.read_text())
                if previous.get('as_of', '') > record['as_of']:
                    print('Retained newer saved report')
                    return
                if previous == record:
                    print('Forward P/E report unchanged')
                    return
            temp = target.with_suffix('.tmp')
            temp.write_text(json.dumps(record, indent=2) + '\n')
            temp.replace(target)
            print(f'Forward P/E: {value}x; report date {edition}; {url}')
            return
        except (OSError, ValueError, subprocess.SubprocessError) as exc:
            print(f'::warning::Forward P/E {edition}: {type(exc).__name__}: {exc}')
    print('::warning::No valid new FactSet report; existing input retains its original date and expiry.')


if __name__ == '__main__':
    refresh()
