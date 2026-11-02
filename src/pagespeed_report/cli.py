"""Command line entry point: run PSI for a URL and write Markdown reports."""

import argparse
import io
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import urlsplit

from pagespeed_report.analyzer import analyze
from pagespeed_report.app_logger import AppLogger
from pagespeed_report.constants import (
    ENV_API_KEY,
    ENV_FILE_NAME,
    EXIT_ERROR,
    EXIT_OK,
    EXIT_QUOTA,
    Strategy,
)
from pagespeed_report.markdown_renderer import render
from pagespeed_report.psi_client import PsiClient, PsiError, QuotaExceededError, normalize_target
from pagespeed_report.settings import PROJECT_ROOT, Settings

BOTH = "both"
_log = AppLogger(__name__)


def parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="pagespeed-report",
        description="Google PageSpeed Insights report as Markdown for AI coding agents.",
    )
    parser.add_argument("target", help="Domain or URL, e.g. appcentrics.de")
    parser.add_argument(
        "--strategy",
        choices=[*(s.value for s in Strategy), BOTH],
        default=BOTH,
        help="Device to emulate (default: both)",
    )
    parser.add_argument("--out", type=Path, help="Output folder (default: PAGESPEED_REPORTS_DIR)")
    return parser.parse_args(argv)


def report_path(out_dir: Path, url: str, strategy: Strategy, now: datetime) -> Path:
    host = urlsplit(url).hostname or "unknown-host"
    return out_dir / host / f"{now:%Y-%m-%d_%H%M}_{strategy.value}.md"


def main(argv: list[str] | None = None, client: PsiClient | None = None) -> int:
    args = parse_args(argv)
    if isinstance(sys.stdout, io.TextIOWrapper):
        # Windows consoles default to cp1252; reports contain arbitrary page snippets.
        sys.stdout.reconfigure(encoding="utf-8")
    try:
        settings = Settings.load()
        url = normalize_target(args.target)
    except ValueError as error:
        AppLogger.configure("INFO")
        _log.error(str(error))
        return EXIT_ERROR
    AppLogger.configure(settings.log_level)
    client = client or PsiClient(settings)
    out_dir: Path = args.out or settings.reports_dir
    strategies = list(Strategy) if args.strategy == BOTH else [Strategy(args.strategy)]
    now = datetime.now()

    for strategy in strategies:
        try:
            report = analyze(client.run(url, strategy), strategy)
        except QuotaExceededError as error:
            _log.error(
                f"PSI quota exceeded: {error}\nSet {ENV_API_KEY} in {PROJECT_ROOT / ENV_FILE_NAME} "
                "(free key: https://developers.google.com/speed/docs/insights/v5/get-started)."
            )
            return EXIT_QUOTA
        except PsiError as error:
            _log.error(str(error))
            return EXIT_ERROR
        markdown = render(report)
        path = report_path(out_dir, url, strategy, now)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(markdown, encoding="utf-8")
        sys.stdout.write(markdown + "\n")
        _log.info(f"Report saved: {path}")
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
