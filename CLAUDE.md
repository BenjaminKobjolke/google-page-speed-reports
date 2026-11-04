# Version
3

# Coding Rules (Pointer)

This project's rules live in two files in the project root:

- `CODING_RULES.md` — code quality and conventions. BINDING for all code work in
  this repository, always.
- `IMPLEMENTATION_FLOW.md` — the end-to-end flow to follow when planning and
  implementing a change (checks, gates, Definition of Done).

MANDATORY: Before writing or editing ANY code, you MUST Read BOTH files in full
**in the current session**. Do not rely on memory of a previous session, a
summary, or partial reads.

If you are about to make a code change and have not read both files in this
session: STOP, read them, then continue.

An external tool may orchestrate the implementation itself. When a skill or run
states that the implementation is orchestrated, ignore `IMPLEMENTATION_FLOW.md`
entirely — the orchestrator runs those steps as its own phases. `CODING_RULES.md`
stays binding either way.

Next to `CODING_RULES.md`, apply also writes `CODING_RULES_PLAN.md`,
`CODING_RULES_REVIEW.md` and `CODING_RULES_CODE.md`. When an orchestrator's run
instructions name one of these step files, that file replaces `CODING_RULES.md`
for that run; without such an instruction, `CODING_RULES.md` stays binding in full.

Do not inline rules back into this file and do not use `@import` for either file —
they are intentionally referenced, not imported.


# Project Notes

- This project's code directory is `src/` (graphify scan root: `src`).
- CLI: `start.bat <domain>` runs `pagespeed-report`; logs go to stderr, the Markdown report to stdout.
- The `/pagespeed-report` skill source is `skill/pagespeed-report/SKILL.md`; after editing it run
  `tools/install_skill.bat` to update the global copy in `%USERPROFILE%\.claude\skills`.

## Post-Implementation Code Analysis

After any feature, completed plan, or bug fix, run the changed-files analyzer and fix every reported issue before considering the work complete:

```powershell
cmd /c ".\tools\analyze_changed_and_new_files.bat"
```

It reports findings only for files changed from Git `HEAD`, including untracked files. Run `tools\analyze_code.bat` for a whole-project audit, exception maintenance, before a release or merge, after a shared-code refactor, or when the working tree has no changes.

Analyzer reports are written as per-rule CSV files under `code_analysis_results\`; a missing CSV means that rule found no issues. Fix applicable findings and rerun the changed-files analyzer until it exits successfully.
