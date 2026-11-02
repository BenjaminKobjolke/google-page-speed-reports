@echo off
rem Install the /pagespeed-report skill globally for Claude Code (%USERPROFILE%\.claude\skills).
rem {{PROJECT_DIR}} in SKILL.md is replaced with this repository's path. Re-run after editing the skill.
setlocal
set "REPO=%~dp0.."
for %%I in ("%REPO%") do set "REPO=%%~fI"
set "TARGET=%USERPROFILE%\.claude\skills\pagespeed-report"

if not exist "%TARGET%" mkdir "%TARGET%"
uv run --quiet --project "%REPO%" python -c "import sys, pathlib; src, dst, repo = sys.argv[1:]; pathlib.Path(dst).write_text(pathlib.Path(src).read_text(encoding='utf-8').replace('{{PROJECT_DIR}}', repo), encoding='utf-8')" "%REPO%\skill\pagespeed-report\SKILL.md" "%TARGET%\SKILL.md" "%REPO%"
if %ERRORLEVEL% neq 0 (
    echo ERROR: Failed to install the skill
    exit /b 1
)
echo Installed: %TARGET%\SKILL.md
exit /b 0
