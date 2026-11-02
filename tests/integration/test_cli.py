"""CLI end to end with a fake PSI client; one optional live test against the real API."""

import os
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from pagespeed_report.cli import main
from pagespeed_report.constants import EXIT_ERROR, EXIT_OK, EXIT_QUOTA, Strategy
from pagespeed_report.models import LighthouseResult
from pagespeed_report.psi_client import PsiClient, QuotaExceededError


def _fake_client(result: LighthouseResult) -> MagicMock:
    client = MagicMock(spec=PsiClient)
    client.run.return_value = result
    return client


def test_both_strategies_write_reports_and_print_them(
    tmp_path: Path, lighthouse_result: LighthouseResult, capsys: pytest.CaptureFixture[str]
) -> None:
    client = _fake_client(lighthouse_result)
    exit_code = main(["appcentrics.de", "--out", str(tmp_path)], client=client)

    assert exit_code == EXIT_OK
    assert [c.args for c in client.run.call_args_list] == [
        ("https://appcentrics.de/", Strategy.MOBILE),
        ("https://appcentrics.de/", Strategy.DESKTOP),
    ]
    files = sorted((tmp_path / "appcentrics.de").glob("*.md"))
    assert [f.name.split("_")[-1] for f in files] == ["desktop.md", "mobile.md"]
    assert "## Action items (5)" in files[1].read_text(encoding="utf-8")
    assert capsys.readouterr().out.count("# PageSpeed report:") == 2


def test_quota_error_exits_with_quota_code(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    client = MagicMock(spec=PsiClient)
    client.run.side_effect = QuotaExceededError("Quota exceeded")
    exit_code = main(["appcentrics.de", "--strategy", "mobile", "--out", str(tmp_path)], client)
    assert exit_code == EXIT_QUOTA
    assert "PAGESPEED_API_KEY" in caplog.text
    assert not any(tmp_path.iterdir())


def test_invalid_target_exits_with_error(tmp_path: Path) -> None:
    assert main(["ftp://example.com", "--out", str(tmp_path)]) == EXIT_ERROR


@pytest.mark.skipif(os.environ.get("PAGESPEED_LIVE") != "1", reason="set PAGESPEED_LIVE=1")
def test_live_psi_call(tmp_path: Path) -> None:
    assert main(["example.com", "--strategy", "desktop", "--out", str(tmp_path)]) == EXIT_OK
