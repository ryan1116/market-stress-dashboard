"""Publish collected data atomically to dedicated tabs; never change sharing."""
import argparse
import json
import math
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHEET_ID = '1KpPI7uOPcqlnxrVzkGpjlyj3hp7i0uvwrf6agqvYMAw'
MARKER = 'msd_path_v1'


def flatten(value, prefix=''):
    if isinstance(value, dict):
        for key, item in value.items():
            yield from flatten(item, f'{prefix}.{key}' if prefix else key)
    else:
        kind = ('null' if value is None else 'boolean' if isinstance(value, bool)
                else 'number' if isinstance(value, (int, float)) else 'array' if isinstance(value, list) else 'string')
        if kind == 'number' and not math.isfinite(value):
            raise ValueError('Non-finite metric')
        yield [prefix, kind, json.dumps(value, ensure_ascii=False, allow_nan=False) if kind != 'string' else value]


def table(records):
    flat = [dict((key, json.loads(value) if kind in ('number', 'boolean') else '' if kind == 'null' else value) for key, kind, value in flatten(record)) for record in records]
    headers = list(dict.fromkeys(key for record in flat for key in record))
    return [['msd_record_v1', *headers], *[[str(i + 1), *[r.get(k, '') for k in headers]] for i, r in enumerate(flat)]]


def cell_value(value):
    if isinstance(value, bool):
        return {'boolValue': value}
    if isinstance(value, (int, float)):
        if not math.isfinite(value):
            raise ValueError('Non-finite cell')
        return {'numberValue': value}
    return {'stringValue': str(value)}


def payload(root=ROOT):
    read = lambda name: json.loads((root / name).read_text())
    latest = read('data/latest.json')
    manual = read('config/manual_metrics.json')
    return {
        'MSD_Latest': [[MARKER, 'type', 'value'], *flatten({'dashboard': latest, 'manual': manual})],
        'MSD_History': table(read('data/history.json')),
        'MSD_EPS_Constituents': table([
            {'as_of': read('data/eps_revision_proxy.json')['as_of'], **row}
            for row in read('data/eps_revision_proxy.json')['constituents']]),
        'MSD_EPS_History': table(read('data/eps_revision_history.json')),
    }


def batch(tables, sheets, markers):
    """All managed-tab content changes land together, including clearing old rows."""
    requests = []
    used = {p['sheetId'] for p in sheets.values()}
    for name, rows in tables.items():
        width = max(map(len, rows))
        existing = sheets.get(name)
        if existing:
            if markers.get(name) != rows[0][0]:
                raise ValueError(f'Refusing to overwrite unrecognized tab: {name}')
            sid = existing['sheetId']
            height = max(existing['gridProperties']['rowCount'], len(rows))
            columns = max(existing['gridProperties']['columnCount'], width)
            requests.append({'updateSheetProperties': {'properties': {'sheetId': sid, 'gridProperties': {
                'rowCount': height, 'columnCount': columns}}, 'fields': 'gridProperties.rowCount,gridProperties.columnCount'}})
        else:
            sid = max(used, default=0) + 1
            used.add(sid)
            height, columns = max(100, len(rows)), max(3, width)
            requests.append({'addSheet': {'properties': {'sheetId': sid, 'title': name,
                'gridProperties': {'rowCount': height, 'columnCount': columns, 'frozenRowCount': 1}}}})
        requests.append({'updateCells': {'range': {'sheetId': sid, 'startRowIndex': 0,
            'endRowIndex': height, 'startColumnIndex': 0, 'endColumnIndex': columns},
            'rows': [{'values': [{'userEnteredValue': cell_value(cell)} for cell in row]} for row in rows],
            'fields': 'userEnteredValue'}})
        if not existing:
            requests.extend([
                {'repeatCell': {'range': {'sheetId': sid, 'startRowIndex': 0, 'endRowIndex': 1,
                    'startColumnIndex': 0, 'endColumnIndex': width},
                    'cell': {'userEnteredFormat': {'backgroundColor': {'red': .92, 'green': .92, 'blue': .92},
                        'textFormat': {'bold': True}}}, 'fields': 'userEnteredFormat'}},
                {'updateDimensionProperties': {'range': {'sheetId': sid, 'dimension': 'COLUMNS',
                    'startIndex': 0, 'endIndex': width}, 'properties': {'pixelSize': 180}, 'fields': 'pixelSize'}},
            ])
    return requests


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    tables = payload()
    if args.dry_run:
        print(json.dumps({name: {'rows': len(rows), 'columns': len(rows[0])} for name, rows in tables.items()}))
        return
    # Use Google's maintained signer; never expose service-account credentials to the browser.
    from google.oauth2 import service_account
    from google.auth.transport.requests import AuthorizedSession
    info = json.loads(os.environ['GOOGLE_SERVICE_ACCOUNT_JSON'])
    credentials = service_account.Credentials.from_service_account_info(info,
        scopes=['https://www.googleapis.com/auth/spreadsheets'])
    session = AuthorizedSession(credentials)
    base = f'https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}'
    def request(method, url, **kwargs):
        response = session.request(method, url, timeout=60, **kwargs)
        if not response.ok:
            raise RuntimeError(f'Sheets API HTTP {response.status_code}; check API enablement and sheet access')
        return response.json()
    metadata = request('GET', base, params={'fields': 'sheets(properties)'})
    sheets = {s['properties']['title']: s['properties'] for s in metadata['sheets']}
    markers = {}
    for name in tables.keys() & sheets.keys():
        result = request('GET', base + f"/values/{name}!A1")
        markers[name] = result.get('values', [['']])[0][0]
    request('POST', base + ':batchUpdate', json={'requests': batch(tables, sheets, markers)})
    for name, rows in tables.items():
        result = request('GET', base + f'/values/{name}!A1:C2', params={'valueRenderOption': 'UNFORMATTED_VALUE'})
        if result.get('values') != [row[:3] for row in rows[:2]]:
            raise RuntimeError(f'Sheet verification failed: {name}')
    print('Verified Google Sheets sync:', ', '.join(tables))


if __name__ == '__main__':
    main()
