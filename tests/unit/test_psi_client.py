import io
import json
import urllib.error
from pathlib import Path

import pytest

from pagespeed_report.constants import Strategy
from pagespeed_report.psi_client import (
    PsiClient,
    PsiError,
    QuotaExceededError,
    normalize_target,
    parse_response,
)
from pagespeed_report.settings import Settings

SETTINGS = Settings(
    api_key="secret", reports_dir=Path("reports"), timeout_seconds=5, log_level="INFO"
)


@pytest.mark.parametrize(
    ("target", "expected"),
    [
        ("appcentrics.de", "https://appcentrics.de/"),
        (" https://appcentrics.de/apps?x=1 ", "https://appcentrics.de/apps?x=1"),
        ("http://example.com", "http://example.com/"),
    ],
)
def test_normalize_target(target: str, expected: str) -> None:
    assert normalize_target(target) == expected


@pytest.mark.parametrize("target", ["ftp://example.com", "https://", ""])
def test_normalize_target_rejects_invalid(target: str) -> None:
    with pytest.raises(ValueError):
        normalize_target(target)


def test_parse_response_rejects_runtime_error(psi_body: str) -> None:
    data = json.loads(psi_body)
    data["lighthouseResult"]["runtimeError"] = {"code": "NO_FCP", "message": "No content"}
    with pytest.raises(PsiError, match="NO_FCP"):
        parse_response(json.dumps(data))


def test_parse_response_rejects_unexpected_shape() -> None:
    with pytest.raises(PsiError):
        parse_response('{"kind": "something else"}')


def _http_error(code: int, message: str) -> urllib.error.HTTPError:
    body = io.BytesIO(json.dumps({"error": {"message": message}}).encode())
    return urllib.error.HTTPError("https://x", code, "err", {}, body)  # type: ignore[arg-type]


def test_run_maps_429_to_quota_error(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_urlopen(url: str, timeout: int) -> None:
        raise _http_error(429, "Quota exceeded")

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    with pytest.raises(QuotaExceededError, match="Quota exceeded"):
        PsiClient(SETTINGS).run("https://appcentrics.de/", Strategy.MOBILE)


def test_run_sends_all_categories_and_key(monkeypatch: pytest.MonkeyPatch, psi_body: str) -> None:
    requested: list[str] = []

    def fake_urlopen(url: str, timeout: int) -> io.BytesIO:
        requested.append(url)
        return io.BytesIO(psi_body.encode())

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    result = PsiClient(SETTINGS).run("https://appcentrics.de/", Strategy.DESKTOP)
    assert result.requested_url == "https://appcentrics.de/"
    for part in ("strategy=desktop", "category=best-practices", "category=seo", "key=secret"):
        assert part in requested[0]
