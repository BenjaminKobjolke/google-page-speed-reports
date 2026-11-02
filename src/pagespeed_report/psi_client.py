"""HTTP client for the PageSpeed Insights v5 API."""

import json
import urllib.error
import urllib.parse
import urllib.request

from pydantic import ValidationError

from pagespeed_report.app_logger import AppLogger
from pagespeed_report.constants import CATEGORIES, PSI_ENDPOINT, QUOTA_HTTP_STATUS, Strategy
from pagespeed_report.models import LighthouseResult, PsiResponse
from pagespeed_report.settings import Settings

_log = AppLogger(__name__)


class PsiError(Exception):
    """The PSI request failed or returned an unusable result."""


class QuotaExceededError(PsiError):
    """PSI answered HTTP 429; keyless requests share a small anonymous quota."""


def normalize_target(target: str) -> str:
    """`appcentrics.de` -> `https://appcentrics.de/`. Rejects non-http(s) schemes."""
    target = target.strip()
    if "://" not in target:
        target = f"https://{target}"
    parsed = urllib.parse.urlsplit(target)
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        raise ValueError(f"Not an http(s) URL or domain: {target!r}")
    return urllib.parse.urlunsplit(parsed._replace(path=parsed.path or "/"))


class PsiClient:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def run(self, url: str, strategy: Strategy) -> LighthouseResult:
        params: list[tuple[str, str]] = [("url", url), ("strategy", strategy.value)]
        params += [("category", category) for category in CATEGORIES]
        if self._settings.api_key:
            params.append(("key", self._settings.api_key))
        request_url = f"{PSI_ENDPOINT}?{urllib.parse.urlencode(params)}"
        _log.info(f"Running PageSpeed Insights ({strategy.value}) for {url} ...")
        try:
            with urllib.request.urlopen(
                request_url, timeout=self._settings.timeout_seconds
            ) as response:
                body = response.read()
        except urllib.error.HTTPError as error:
            message = _error_message(error)
            if error.code == QUOTA_HTTP_STATUS:
                raise QuotaExceededError(message) from error
            raise PsiError(f"HTTP {error.code}: {message}") from error
        except (urllib.error.URLError, TimeoutError) as error:
            raise PsiError(f"Request failed: {error}") from error
        return parse_response(body)


def parse_response(body: bytes | str) -> LighthouseResult:
    try:
        result = PsiResponse.model_validate(json.loads(body)).lighthouse_result
    except (json.JSONDecodeError, ValidationError) as error:
        raise PsiError(f"Unexpected PSI response: {error}") from error
    if result.runtime_error and result.runtime_error.code != "NO_ERROR":
        raise PsiError(
            f"Lighthouse could not test the page: {result.runtime_error.code}: "
            f"{result.runtime_error.message}"
        )
    return result


def _error_message(error: urllib.error.HTTPError) -> str:
    try:
        return str(json.loads(error.read())["error"]["message"])
    except (ValueError, KeyError, TypeError):
        return str(error.reason)
