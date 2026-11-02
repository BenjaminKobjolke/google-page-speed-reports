@echo off
rem Run the PageSpeed report CLI from any working directory, e.g. start.bat appcentrics.de
uv run --quiet --project "%~dp0." pagespeed-report %*
exit /b %ERRORLEVEL%
