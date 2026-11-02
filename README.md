# pagespeed-report

Runs Google PageSpeed Insights (PSI API v5, Lighthouse lab data) for a domain and writes a
Markdown report made for AI coding agents: scores, Core Web Vitals, and a list of failing
audits sorted by estimated savings, each with the affected resource URLs or CSS selectors.

Ships a Claude Code skill, `/pagespeed-report <domain>`, that you can call from any project.
The agent runs the report, maps each finding to files in that project and works through them.

## Requirements

- Windows, [uv](https://docs.astral.sh/uv/), Python 3.12+ (uv installs it)
- Optional: a free PSI API key. Keyless requests share a tiny quota and often fail with HTTP 429.
  Get one at https://developers.google.com/speed/docs/insights/v5/get-started

Dependencies: `pydantic` (response validation). Dev: `pytest`, `ruff`, `mypy`.

## Setup

```bat
install.bat
copy .env.example .env      & rem then set PAGESPEED_API_KEY
tools\install_skill.bat     & rem installs /pagespeed-report into %USERPROFILE%\.claude\skills
```

## Usage

```bat
start.bat appcentrics.de                       & rem mobile + desktop, saved to reports\
start.bat https://appcentrics.de/apps --strategy mobile
start.bat appcentrics.de --out D:\somewhere\pagespeed-reports
```

Reports go to `<out>/<host>/<YYYY-MM-DD_HHMM>_<strategy>.md` and are printed to stdout.
Exit codes: `0` ok, `1` error, `2` PSI quota exceeded (set `PAGESPEED_API_KEY`).

In Claude Code, from any project:

```
/pagespeed-report appcentrics.de
```

PSI tests the public URL, so local changes show only after deploy.

## Configuration (`.env`)

See `.env.example`: `PAGESPEED_API_KEY`, `PAGESPEED_REPORTS_DIR`, `PAGESPEED_TIMEOUT`,
`PAGESPEED_LOG_LEVEL`. Real environment variables override `.env`.

## Development

```bat
tools\run_tests.bat               & rem unit tests
tools\run_integration_tests.bat   & rem CLI end to end (set PAGESPEED_LIVE=1 for a real PSI call)
update.bat                        & rem upgrade deps, lint, type check, test
tools\graphify_update.bat         & rem refresh the code graph of src\
```

Code: `src/pagespeed_report/` — `psi_client.py` (HTTP + validation), `analyzer.py`
(scores, vitals, sorted action items), `markdown_renderer.py`, `cli.py`.
