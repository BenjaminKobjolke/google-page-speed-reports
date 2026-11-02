"""Shared fixtures: a recorded-shape PSI response, no network."""

from pathlib import Path

import pytest

from pagespeed_report.models import LighthouseResult
from pagespeed_report.psi_client import parse_response

FIXTURE = Path(__file__).parent / "fixtures" / "psi_appcentrics_mobile.json"


@pytest.fixture
def psi_body() -> str:
    return FIXTURE.read_text(encoding="utf-8")


@pytest.fixture
def lighthouse_result(psi_body: str) -> LighthouseResult:
    return parse_response(psi_body)
