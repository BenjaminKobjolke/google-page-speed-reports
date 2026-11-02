from pagespeed_report.analyzer import analyze, rating_for
from pagespeed_report.constants import Rating, Strategy
from pagespeed_report.models import LighthouseResult


def test_scores_and_passed_counts(lighthouse_result: LighthouseResult) -> None:
    report = analyze(lighthouse_result, Strategy.MOBILE)
    assert [(s.category_id, s.score, s.passed_audits) for s in report.scores] == [
        ("performance", 62, 1),
        ("accessibility", 88, 1),
        ("best-practices", 96, 1),
        ("seo", 91, 1),
    ]


def test_vitals_in_display_order_with_ratings(lighthouse_result: LighthouseResult) -> None:
    vitals = analyze(lighthouse_result, Strategy.MOBILE).vitals
    assert [(v.title, v.display_value, v.rating) for v in vitals] == [
        ("Largest Contentful Paint", "5.1 s", Rating.POOR),
        ("Cumulative Layout Shift", "0.002", Rating.GOOD),
        ("Total Blocking Time", "120 ms", Rating.GOOD),
        ("First Contentful Paint", "2.9 s", Rating.NEEDS_IMPROVEMENT),
        ("Speed Index", "6.0 s", Rating.POOR),
    ]


def test_actions_sorted_by_savings_then_category(lighthouse_result: LighthouseResult) -> None:
    actions = analyze(lighthouse_result, Strategy.MOBILE).actions
    # Hidden-group duplicate, metrics, passing, informative and n/a audits are all excluded.
    assert [a.audit_id for a in actions] == [
        "unused-javascript",
        "render-blocking-insight",
        "image-alt",
        "errors-in-console",
        "meta-description",
    ]


def test_insight_savings_from_metric_savings_and_nested_items(
    lighthouse_result: LighthouseResult,
) -> None:
    action = analyze(lighthouse_result, Strategy.MOBILE).actions[1]
    assert action.savings_ms == 450
    assert [item.url for item in action.affected] == [
        "https://appcentrics.de/css/main.css",
        "https://fonts.googleapis.com/css2?family=Inter",
    ]


def test_affected_items_are_capped(lighthouse_result: LighthouseResult) -> None:
    details = lighthouse_result.audits["unused-javascript"].details
    assert details is not None
    details.items = details.items * 7  # 14 items
    action = analyze(lighthouse_result, Strategy.MOBILE).actions[0]
    assert len(action.affected) == 10
    assert action.more_affected == 4


def test_rating_boundaries() -> None:
    assert rating_for(0.9) is Rating.GOOD
    assert rating_for(0.5) is Rating.NEEDS_IMPROVEMENT
    assert rating_for(0.49) is Rating.POOR
