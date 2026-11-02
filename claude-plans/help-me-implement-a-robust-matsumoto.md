# PageSpeed Report CLI + `/pagespeed-report` skill

## Context
Need: AI coding agent in any project (e.g. `D:\wamp64\www\appcentrics-clickdummy`) runs
`/pagespeed-report appcentrics.de`, gets a Markdown list of concrete optimizations from
Google PageSpeed Insights (PSI API v5), then works on them. The repository is greenfield and
already has git initialised; application source has not been created yet.
Source: ChatGPT chat — PSI v5 endpoint `https://www.googleapis.com/pagespeedonline/v5/runPagespeed`,
params `url`, `strategy`, repeated `category`, optional `key`; keyless calls often get HTTP 429.

Decisions (user): scaffold fresh in this already-initialised git repository, Python + uv,
Codex delegation, optional API key in `.env`, skill installed globally in
`~/.claude/skills`, and the graphify addon enabled with `src/` as its code directory.

## Conventions and reusable project assets
- This is a greenfield repository: there is no application source, test suite, or graph yet.
  Do not invent compatibility layers for pre-existing code.
- Keep the established `src/` Python package layout, `tests/unit/` plus
  `tests/integration/` split, and `tools/` home for project scripts.
- Reuse the existing `tools/coding_rules_delegate.{sh,ps1}` wrapper for Codex workflow steps;
  do not add another delegation mechanism.
- Copy the reusable setup scripts from
  `D:/GIT/BenjaminKobjolke/claude-coding-rules/plugins/coding-rules/rules/python_setup_files/`:
  `install.bat`, `update.bat`, `tools/run_tests.bat`, and
  `tools/run_integration_tests.bat`. Preserve their visible progress and exit-code behavior.
- Copy `implementation_flow_addons/graphify_update.bat` into `tools/`, changing only its
  code-directory setting from the template default to `src`.
- Follow the existing rule intent in the design: keep environment reads in `settings.py`, use
  typed models at module boundaries, and keep stdout reserved for report content while logs go
  to stderr.

## Step 0 — coding rules
Run apply.py (python 3.14 + uv 0.9.18 available):
```
python D:/GIT/BenjaminKobjolke/claude-coding-rules/plugins/coding-rules/skills/apply/apply.py \
  --project D:/GIT/BenjaminKobjolke/google-page-speed-reports \
  --plugin-root D:/GIT/BenjaminKobjolke/claude-coding-rules/plugins/coding-rules \
  --rules COMMON_RULES.md,IMPLEMENTATION_FLOW.md,PYTHON_RULES.md \
  --delegation codex --python python --json
```
- No optional python/*.md (no GUI/DB/templates). No DESIGN_RULES (headless CLI).
- Include the opted-in graphify addon and configure its code directory as `src/`.
- Then Read `CODING_RULES.md` + `IMPLEMENTATION_FLOW.md` in full and follow the flow (Codex DRY/convention steps).
- Git is already initialised. Add/update `.gitignore` with `.env`, `.venv/`, and `reports/`.
  Keep `coding-rules.json` consistent with the coding-rules workflow rather than ignoring it.

## Project layout (uv, `src/` layout)
```
pyproject.toml          # deps: pydantic; dev: pytest, ruff, mypy; [tool.ruff] extend-exclude=["*.md"]
.env.example            # PAGESPEED_API_KEY=, PAGESPEED_REPORTS_DIR=reports, PAGESPEED_TIMEOUT=120
install.bat, update.bat, start.bat           # from python_setup_files; start.bat = uv run pagespeed-report %*
tools/run_tests.bat, tools/run_integration_tests.bat  # from python_setup_files/tools
tools/install_skill.bat # copies skill/pagespeed-report/SKILL.md to %USERPROFILE%\.claude\skills\pagespeed-report\, replacing {{PROJECT_DIR}}
skill/pagespeed-report/SKILL.md
README.md
src/pagespeed_report/
  __main__.py / cli.py  # argparse: target, --strategy mobile|desktop|both (default both), --out DIR
  settings.py           # frozen dataclass Settings from env/.env (only place reading os.getenv)
  constants.py          # API URL, CATEGORY ids, CWV audit ids + thresholds, MAX_ITEMS
  app_logger.py         # AppLogger wrapping logging (stderr; stdout reserved for report)
  psi_client.py         # PsiClient.run(url, strategy) -> LighthouseResult; urllib, no extra HTTP dep
  models.py             # pydantic models for the PSI subset we read (validation at boundary)
  analyzer.py           # LighthouseResult -> ReportData (scores, vitals, action items)
  markdown_renderer.py  # ReportData -> Markdown string
tests/unit/             # analyzer + renderer + target normalisation, using trimmed fixture JSON
tests/integration/      # cli end-to-end with fake PsiClient writes file; live PSI test only if PAGESPEED_LIVE=1
tests/fixtures/psi_appcentrics_mobile.json   # captured once from real API, trimmed
```
Pin versions by checking PyPI at implement time (rule "Confirm Dependency Versions").

## Behaviour
- Target normalisation: `appcentrics.de` -> `https://appcentrics.de/`; reject non-http(s) schemes.
- One PSI call per strategy, all 4 categories (performance, accessibility, best-practices, seo).
- 429 / quota: clear error telling user to set `PAGESPEED_API_KEY` in `.env`; exit code 2. Other HTTP/JSON errors: exit 1 with message. `runtimeError` in lighthouseResult -> fail.
- Output: write `reports/<host>/<YYYY-MM-DD_HHMM>_<strategy>.md` (or `--out`), print the Markdown to stdout, print saved path(s) on stderr via AppLogger.

## Report format (AI-agent oriented)
```
# PageSpeed report — https://appcentrics.de/ (mobile) — 2026-11-02 09:10
## Scores            table: category | score 0-100
## Core Web Vitals   LCP, CLS, TBT, FCP, Speed Index: value | rating good/needs-improvement/poor
## Action items      sorted: perf opportunities by savings ms, then bytes, then other failing audits
### 1. [performance] Reduce unused JavaScript — est. savings 1.2 s / 340 KiB (audit id: unused-javascript)
Why: <audit description, markdown links stripped to text>
Affected:
- https://appcentrics.de/js/app.js — 210 KiB wasted
- selector `div.hero > img` — <snippet>        (for a11y/SEO node items)
## Passed audits     count per category only
```
Rules: failing = score not null and < 0.9, excluding `notApplicable`/`informative`/`manual`; details items capped at MAX_ITEMS (10) with "+N more". Both strategies -> one file each.

## Skill `skill/pagespeed-report/SKILL.md`
Frontmatter `name: pagespeed-report`, description triggers on "/pagespeed-report <domain>", page speed, lighthouse.
Steps for the calling agent:
1. Run `"{{PROJECT_DIR}}\start.bat" <domain> --out "<cwd>\pagespeed-reports"` (report lands in the calling project).
2. Read the generated report(s).
3. Map each action item to files in the current project (grep resource URLs / selectors), output a prioritised todo list with file:line where found, mark items outside the project (third-party scripts, server config).
4. Ask the user which items to implement, then work through them; re-run the report to verify.
- 429 error -> tell the user to set `PAGESPEED_API_KEY` in `{{PROJECT_DIR}}\.env`.
Note: PSI tests the public URL, so local clickdummy changes only show after deploy — skill states this.

## Verification
- `tools\run_tests.bat` (unit) and `tools\run_integration_tests.bat` green; `uv run ruff check`, `ruff format --check`, `mypy src`.
- Run `tools\graphify_update.bat` from the repository root after implementation; the first
  graph build is performed by the graphify workflow before this refresh script can smoke-test it.
- Live: `start.bat appcentrics.de` -> check report files in `reports/appcentrics.de/`, readable, items sorted.
- `tools\install_skill.bat`, then in `D:\wamp64\www\appcentrics-clickdummy` run `/pagespeed-report appcentrics.de` and confirm the agent gets the todo list.

Skipped: sitemap/multi-page crawling, history/trend tracking, CrUX field data, HTML output.

## SUMMARY CONVENTION CHECK

Reused the existing `src/`, `tests/unit/`, `tests/integration/`, and `tools/` layout; the
repository's delegation wrapper; the external uv setup/test templates; and the graphify refresh
template. These match the current project scaffolding and avoid introducing parallel tooling or
naming conventions. No application-source conventions exist yet because this is greenfield.

## SUMMARY DRY

Consolidated the setup decisions into one conventions section, removed obsolete prompts to ask
about graphify and git initialization, and made the reusable external templates explicit instead
of restating their behavior in multiple plan sections. Also clarified that the graphify refresh is
verification after the initial graph build, not a second build mechanism.
