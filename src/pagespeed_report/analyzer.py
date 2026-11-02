"""Turn a Lighthouse result into the report data: scores, vitals and sorted action items."""

from dataclasses import dataclass

from pagespeed_report.constants import (
    AVERAGE_SCORE,
    CATEGORIES,
    MAX_AFFECTED_ITEMS,
    NON_SCORED_MODES,
    PASS_SCORE,
    SKIPPED_GROUPS,
    VITAL_AUDIT_IDS,
    Rating,
    Strategy,
)
from pagespeed_report.models import Audit, DetailItem, LighthouseResult


@dataclass(frozen=True)
class CategoryScore:
    category_id: str
    title: str
    score: int | None
    passed_audits: int


@dataclass(frozen=True)
class Vital:
    title: str
    display_value: str
    rating: Rating


@dataclass(frozen=True)
class ActionItem:
    category_id: str
    audit_id: str
    title: str
    description: str
    display_value: str | None
    savings_ms: float
    savings_bytes: float
    affected: list[DetailItem]
    more_affected: int


@dataclass(frozen=True)
class ReportData:
    url: str
    strategy: Strategy
    fetch_time: str
    scores: list[CategoryScore]
    vitals: list[Vital]
    actions: list[ActionItem]


def rating_for(score: float) -> Rating:
    if score >= PASS_SCORE:
        return Rating.GOOD
    return Rating.NEEDS_IMPROVEMENT if score >= AVERAGE_SCORE else Rating.POOR


def is_scored(audit: Audit) -> bool:
    return audit.score is not None and audit.score_display_mode not in NON_SCORED_MODES


def is_failing(audit: Audit) -> bool:
    return is_scored(audit) and audit.score is not None and audit.score < PASS_SCORE


def analyze(result: LighthouseResult, strategy: Strategy) -> ReportData:
    scores: list[CategoryScore] = []
    actions: list[ActionItem] = []
    seen: set[str] = set()
    for category_id in CATEGORIES:
        category = result.categories.get(category_id)
        if category is None:
            continue
        passed = 0
        for ref in category.audit_refs:
            audit = result.audits.get(ref.id)
            if audit is None or ref.group in SKIPPED_GROUPS or ref.id in seen:
                continue
            seen.add(ref.id)
            if is_failing(audit):
                actions.append(_action_item(category_id, audit))
            elif is_scored(audit):
                passed += 1
        score = None if category.score is None else round(category.score * 100)
        scores.append(CategoryScore(category_id, category.title, score, passed))

    category_order = {category_id: index for index, category_id in enumerate(CATEGORIES)}
    actions.sort(
        key=lambda a: (-a.savings_ms, -a.savings_bytes, category_order[a.category_id], a.title)
    )
    return ReportData(
        url=result.final_displayed_url or result.requested_url,
        strategy=strategy,
        fetch_time=result.fetch_time,
        scores=scores,
        vitals=_vitals(result),
        actions=actions,
    )


def _vitals(result: LighthouseResult) -> list[Vital]:
    vitals: list[Vital] = []
    for audit_id in VITAL_AUDIT_IDS:
        audit = result.audits.get(audit_id)
        if audit is not None and audit.score is not None and audit.display_value:
            vitals.append(Vital(audit.title, audit.display_value, rating_for(audit.score)))
    return vitals


def _action_item(category_id: str, audit: Audit) -> ActionItem:
    details = audit.details
    savings_ms = details.overall_savings_ms if details else None
    if savings_ms is None:
        # Lighthouse 12 insight audits report savings per metric only; CLS is unitless, not ms.
        savings_ms = max((v for k, v in audit.metric_savings.items() if k != "CLS"), default=0.0)
    affected = _flatten(details.items) if details else []
    savings_bytes = details.overall_savings_bytes if details else None
    if savings_bytes is None:
        # Insight audits omit the total; their items still carry per-resource waste.
        savings_bytes = sum(item.wasted_bytes or 0.0 for item in affected)
    return ActionItem(
        category_id=category_id,
        audit_id=audit.id,
        title=audit.title,
        description=audit.description,
        display_value=audit.display_value,
        savings_ms=savings_ms,
        savings_bytes=savings_bytes,
        affected=affected[:MAX_AFFECTED_ITEMS],
        more_affected=max(0, len(affected) - MAX_AFFECTED_ITEMS),
    )


def _flatten(items: list[DetailItem]) -> list[DetailItem]:
    """Keep items that name a resource or DOM node; unwrap nested tables."""
    flat: list[DetailItem] = []
    for item in items:
        if item.url or item.node:
            flat.append(item)
        flat.extend(_flatten(item.items))
    return flat
