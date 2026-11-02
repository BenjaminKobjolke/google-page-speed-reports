"""Regression: a real (trimmed) Lighthouse 13.6 response for appcentrics.de must parse and render.

Real responses carry shapes the hand-made fixture lacks: checklist `items` as a dict,
`source.url` instead of `url`, nested sub-items.
"""

from pathlib import Path

from pagespeed_report.analyzer import analyze
from pagespeed_report.constants import Strategy
from pagespeed_report.markdown_renderer import render
from pagespeed_report.psi_client import parse_response

REAL_FIXTURE = Path(__file__).parents[1] / "fixtures" / "psi_appcentrics_mobile_real.json"


def test_real_response_parses_and_renders() -> None:
    result = parse_response(REAL_FIXTURE.read_text(encoding="utf-8"))
    report = analyze(result, Strategy.MOBILE)
    by_id = {action.audit_id: action for action in report.actions}

    assert report.actions[0].audit_id == "cache-insight"  # largest saving: 1.4 s
    assert {"unused-javascript", "render-blocking-insight", "deprecations"} <= set(by_id)
    assert any(item.url for item in by_id["deprecations"].affected)  # taken from source.url
    assert by_id["image-delivery-insight"].savings_bytes > 1_000_000  # summed from items
    assert "appcentrics-logo.png at selector `" in render(report)
