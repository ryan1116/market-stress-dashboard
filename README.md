# Current methodology — v0.2.4 (2026-10-19)

Seasonal adjustment is disabled. The earnings card shows raw 60-day revisions, upward-revised company weight and 30-day analyst breadth. Valid earnings data are UNRATED; the combined regime remains UNDETERMINED pending validated earnings thresholds. Null legacy baseline/surprise fields are retained for compatibility. Earlier history and the original whitepaper are historical records, not the active model.

# Market Stress Dashboard Web v0.2.3

Repository: https://github.com/ryan1116/market-stress-dashboard

## v0.2.3 changes

- Term premium now uses FRED THREEFYTP10 (Kim–Wright), instead of parsing the blocked Fed HTML table.
- The observed value, its own observation date, and quality are displayed. Its 30-day change is anchored to that observation date. Under the existing 7-day freshness policy, stale term premium remains visible but does not contribute to shock classification.
- Live retrieval on 2026-09-28: 2026-09-18 value 0.9595%, 30-day change +12.2 bp, quality STALE. Rates remain current and the earnings fallback remains stale, producing UNDETERMINED.
- Seasonal definition is a separate research backlog, not a blocker for data collection or deployment preparation. Seasonal adjustment is disabled; no earnings rating is inferred.
- 29 offline regression checks passed. EPS live API access, GitHub scheduled execution and visual browser rendering remain unverified.

## Forward P/E refresh (2026-10-14)

The daily dashboard workflow now checks recent Friday FactSet Earnings Insight PDFs and saves the full-index forward 12-month P/E to `data/forward_pe.json`. The original Reuters/LSEG manual input remains unchanged as fallback. FactSet and LSEG estimates can differ; this is an explicit source change, not a historical restatement.

The saved date is the **report publication date**, not the collection date or an independently verified underlying price date. The existing 14-day validity rule is retained. A missing report, changed format or failed download leaves the saved value and its date unchanged; expired inputs still block classification. The page links the actual report. Standard Friday editions are supported; other publication patterns require a collector update.

Run `python3 scripts/update_forward_pe.py` (requires Poppler `pdftotext`), then `python3 scripts/update_dashboard.py`. GitHub Actions installs Poppler. Offline checks: `python3 tests/run_checks.py` and `python3 tests/check_forward_pe.py`.

## API key setup

Open https://github.com/ryan1116/market-stress-dashboard/settings/secrets/actions
Choose New repository secret, Name: ALPHAVANTAGE_API_KEY, Secret: your key, then Add secret.
The EPS workflow already maps that repository secret to the process environment. Do not put the key in config, HTML, or committed files.

Project files and .github/workflows belong at repository root. After configuring the secret, use Actions → Update EPS Revision Proxy → Run workflow for a manual first run. Repository upload does not itself enable GitHub Pages.

## v0.2.2 data-quality corrections

The v0.2.1 source and ZIP remain preserved in the parent project directory.

- Rates levels and 30/90-day changes use the same latest shared observation date.
- Proxy JSON errors, invalid numbers, non-object data, missing required fields and future dates fall back safely.
- Proxy age is limited to 10 days; fallback age to 14 days. Expired earnings have no active surprise/state, and the regime becomes UNDETERMINED.
- Proxy use requires SPY weight coverage >= 30% and at least 10 companies. These are provisional operating guards, not statistically calibrated trading thresholds. Aggregated low-coverage observations can still be saved for diagnostics, but the dashboard rejects them as active signals.
- EPS revision is now `100 * (current - prior) / abs(prior)`. A loss reduction from -2 to -1 yields +50%, not -50%. A zero prior EPS is excluded. This is a signed relative revision measure; changes involving losses or near-zero EPS still need economic interpretation.
- Holdings are sorted by weight before selecting the top basket and combining share classes.
- EPS history retains one snapshot per date. Today's earlier snapshot cannot enter today's baseline.
- The inconsistent packaged rate sample was replaced by an actual FRED refresh, with rate source URLs and a generation timestamp. The old sample history remains in v0.2.1; v0.2.2 history starts with this fresh observation.
- The UI shows earnings and P/E dates, stale quality, indeterminate regime and fetch errors.

Policy settings are in `config/data_policy.json`. P/E has a 14-day validity limit; rates have a 7-day validity limit. The independent FactSet-versus-fiscal-year seasonal benchmark concern has NOT been resolved by these software corrections.

## Validation on 2026-09-28

All 27 offline checks passed, including the nine previously unmet conditions. Python and embedded JavaScript syntax checks passed. An actual rates refresh completed: common market date 2026-09-24, nominal 5.18%, real 2.85%, breakeven 2.33%. Term premium access returned HTTP 403 and is UNAVAILABLE. The 2026-08-31 fallback is STALE, so the packaged regime is UNDETERMINED.

Live EPS API access and visual browser rendering remain unverified. No deployment or scheduled GitHub execution is claimed. Run regression checks with `python3 tests/run_checks.py` after installing pandas. Results are written to the ignored `tests/results.json` file.

## Original EPS automation design
The Earnings Confirmation pillar can now update automatically from a structured analyst-estimate feed.

### Earnings Revision Proxy
The weekly job:
1. pulls current SPY holdings,
2. takes the top 24 holdings,
3. combines duplicate share classes (GOOG/GOOGL),
4. selects each issuer's nearest future fiscal-year EPS estimate at least 90 days from fiscal year-end,
5. calculates 30/60/90-day EPS estimate revisions,
6. weights revisions by SPY holding weight,
7. calculates analyst up/down revision breadth,
8. compares the 60-day revision with a provisional -1.7% first-two-month seasonal benchmark (comparability remains unvalidated),
9. writes `data/eps_revision_proxy.json` and historical snapshots.

This is an **automated proxy**, not FactSet's official S&P 500 bottom-up EPS series.

## API setup
Create a GitHub repository secret:

`ALPHAVANTAGE_API_KEY`

The workflow intentionally limits itself to the SPY ETF-profile request plus a top-holdings basket so it can stay close to low API-call budgets. API entitlements and limits can change; if the endpoint is unavailable, the dashboard retains the explicitly labeled fallback earnings input rather than silently substituting zero.

## Schedules
- Rates / regime: 07:30 KST Tue-Sat
- EPS Revision Proxy: Monday 08:15 KST

## Core pillars
1. **Valuation Vulnerability** — forward earnings yield minus 10Y real yield
2. **Discount-Rate Shock** — 1M/3M real-yield change plus term-premium context
3. **Earnings Confirmation** — weighted 60D EPS revision surprise and revision breadth

## Seasonal benchmark
The initial -1.7% benchmark is the recent five-year average decline in S&P 500 bottom-up EPS estimates during the first two months of a quarter reported by FactSet in September 2026. It is a provisional external benchmark.

The code stores weekly proxy history. Empirical seasonal-baseline switching is disabled pending the research in RESEARCH_BACKLOG.md.

## Important limitations
- SPY top holdings cover only part of the index.
- Market-cap weighting of percentage EPS revisions is an approximation; it is not index bottom-up EPS arithmetic.
- Different issuers have different fiscal year ends.
- The proxy is designed to detect direction and breadth of estimate revisions, not reproduce FactSet index EPS exactly.
- Regime thresholds remain operating hypotheses, not optimized trading rules.

## Google Sheets backend

Target: https://docs.google.com/spreadsheets/d/1KpPI7uOPcqlnxrVzkGpjlyj3hp7i0uvwrf6agqvYMAw/edit

Collectors continue running in GitHub Actions. `scripts/sync_sheets.py` writes one atomic Sheets batch after collection and before committing the backup JSON files. Both scheduled workflows share one concurrency group. Financial calculations remain in the existing collector; the frontend reads the completed snapshot from the sheet.

Managed tabs (existing unrelated tabs remain untouched):
- `MSD_Latest`: typed metric paths and values, including source metadata used by the web page.
- `MSD_History`: stored market snapshots (one per rates observation date, retained under the existing history policy).
- `MSD_EPS_Constituents`: the latest company-level EPS revisions and weights.
- `MSD_EPS_History`: stored weekly earnings proxy snapshots.

These are collector-owned output tabs, not manual input forms. Collection replaces their contents. Edit manual inputs in `config/manual_metrics.json`; only collected public market data enter these tabs. Credentials never enter the sheet, repository or browser. Historical tables contain native numeric cells; the published transport tab uses explicit types so CSV cannot reinterpret dates or missing values.

### One-time connection

1. Enable Google Sheets API in a Google Cloud project. Create a dedicated service account (no project-wide role needed) and share only this spreadsheet with its email as Editor.
2. Store that service account's JSON key in the repository Actions secret `GOOGLE_SERVICE_ACCOUNT_JSON`. Do not paste keys into chat or commit them. Restrict the account to this sheet; rotate the key under your normal credential policy.
3. Set repository Actions variable `SHEETS_SYNC_ENABLED` to `true`. Run `Update Market Stress Dashboard` manually. Verify its Sheets step and sheet values before enabling the frontend.
4. In Sheets, choose File → Share → Publish to web. Publish **only `MSD_Latest`**, in CSV format, with automatic republication. This exposes that tab's market metrics, dates and source metadata to anyone; the other tabs need not be public.
5. Put the resulting `https://docs.google.com/spreadsheets/d/e/.../pub?gid=...&single=true&output=csv` link in `config/data_backend.json` and change `mode` to `google_sheets`. Verify unauthenticated CSV access, browser CORS and the live page before completing the switch. Publishing may lag writes by several minutes.

Connection verified on 2026-10-14: sheet synchronization is enabled and the frontend uses `google_sheets` mode. For a new setup, keep `mode` as `repository` until steps 1–5 are verified. No automatic fallback is used once sheet mode is enabled: inaccessible, malformed or more-than-four-day-old snapshots produce the existing unavailable state instead of silently showing another source. Rollback is explicit: set `mode` back to `repository`.

Checks: `python3 scripts/sync_sheets.py --dry-run`, `python3 tests/check_sheets.py`, `python3 tests/run_checks.py`.
