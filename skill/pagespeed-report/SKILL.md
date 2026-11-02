---
name: pagespeed-report
description: Run a Google PageSpeed Insights (Lighthouse) report for a domain or URL and turn it into a prioritised optimisation todo list for the current project. Use for "/pagespeed-report <domain>", "page speed", "pagespeed", "lighthouse report", "why is my site slow", "core web vitals".
---

# PageSpeed report

Arguments: a domain or URL (e.g. `appcentrics.de`), optionally `--strategy mobile|desktop|both`
(default `both`). No argument: ask the user which domain to test.

## 1. Run the report

Run from the current project's root so the reports land in this project:

```
"{{PROJECT_DIR}}\start.bat" <domain> --out "pagespeed-reports"
```

- One Markdown report per strategy is written to `pagespeed-reports/<host>/<date>_<strategy>.md`.
  The report text is also printed to stdout; the saved paths are logged on stderr.
- A run takes 20-60 s per strategy (Google runs Lighthouse remotely).
- Exit code 2 = PSI quota exceeded (HTTP 429). Keyless requests share a tiny quota. Tell the user
  to put a free key in `{{PROJECT_DIR}}\.env` as `PAGESPEED_API_KEY=...`
  (https://developers.google.com/speed/docs/insights/v5/get-started) and stop.
- Exit code 1 = other error (bad URL, Lighthouse could not load the page). Relay the message.
- Suggest adding `pagespeed-reports/` to this project's `.gitignore` if it is not ignored yet.

## 2. Map the findings to this project

Read the generated report(s). Each action item has an audit id, estimated savings and the affected
resource URLs or CSS selectors. For each item:

- Search this project for the affected file names (`/js/app.js` -> grep `app.js`), selectors
  (`div.hero > img`) and snippets to find the responsible source files.
- Note `file:line` where found. Mark items that are outside this project's control
  (third-party scripts such as Google Tag Manager, server/CDN config such as compression or
  caching headers) as **external**.

## 3. Present the todo list

Output one prioritised list, highest estimated savings first, mobile and desktop merged
(dedupe by audit id, keep the larger saving):

```
1. [performance] Reduce unused JavaScript (1.2 s / 340 KiB) — src/js/app.js: split vendor bundle
2. [accessibility] Images without alt — templates/home.twig:42, templates/footer.twig:8
3. [external] Third-party gtag.js — consider delayed loading
```

Then ask the user which items to implement. Work through the chosen items following the
project's own rules (CLAUDE.md, CODING_RULES.md).

## 4. Verify

PageSpeed Insights tests the **public** URL. Local changes show up only after they are deployed.
After deploy, re-run step 1 and compare the scores with the previous report.
