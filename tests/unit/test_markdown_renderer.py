from pagespeed_report.analyzer import analyze
from pagespeed_report.constants import Strategy
from pagespeed_report.markdown_renderer import format_bytes, format_measures, format_ms, render
from pagespeed_report.models import LighthouseResult


def test_render_contains_agent_relevant_sections(lighthouse_result: LighthouseResult) -> None:
    markdown = render(analyze(lighthouse_result, Strategy.MOBILE))
    assert markdown.startswith("# PageSpeed report: https://appcentrics.de/ (mobile)\n")
    assert "| Performance | 62 | 1 |" in markdown
    assert "| Largest Contentful Paint | 5.1 s | poor |" in markdown
    assert "## Action items (5)" in markdown
    assert "### 1. [performance] Reduce unused JavaScript: est. savings 1.2 s / 340 KiB" in markdown
    assert "- Audit id: `unused-javascript`" in markdown
    assert "  - https://appcentrics.de/js/app.js (210 KiB wasted)" in markdown
    assert "  - https://appcentrics.de/css/main.css (450 ms wasted)" in markdown
    assert '  - selector `div.hero > img`: `<img src="/img/hero.webp">`' in markdown
    assert "### 5. [seo] Document does not have a meta description\n" in markdown


def test_render_without_actions(lighthouse_result: LighthouseResult) -> None:
    report = analyze(lighthouse_result, Strategy.DESKTOP)
    report.actions.clear()
    markdown = render(report)
    assert "(desktop)" in markdown
    assert "No failing audits." in markdown


def test_formatters() -> None:
    assert format_ms(450) == "450 ms"
    assert format_ms(1250) == "1.2 s"
    assert format_bytes(348160) == "340 KiB"
    assert format_measures(450, 348160) == "450 ms / 340 KiB"
    assert format_measures(None, 0) == ""
