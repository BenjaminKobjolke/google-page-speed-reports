"""Render ReportData as Markdown written for an AI coding agent to act on."""

from pagespeed_report.analyzer import ActionItem, ReportData
from pagespeed_report.models import DetailItem

BYTES_PER_KIB = 1024
MS_PER_SECOND = 1000


def format_ms(ms: float) -> str:
    return f"{ms / MS_PER_SECOND:.1f} s" if ms >= MS_PER_SECOND else f"{round(ms)} ms"


def format_bytes(size: float) -> str:
    return f"{round(size / BYTES_PER_KIB)} KiB"


def format_measures(ms: float | None, size: float | None) -> str:
    """Join the non-zero time and byte amounts, e.g. `1.2 s / 340 KiB`."""
    parts = [format_ms(ms)] if ms else []
    parts += [format_bytes(size)] if size else []
    return " / ".join(parts)


def render(report: ReportData) -> str:
    lines = [
        f"# PageSpeed report: {report.url} ({report.strategy.value})",
        "",
        f"Tested: {report.fetch_time} via Google PageSpeed Insights (Lighthouse lab data). "
        "PSI tests the public URL, so local changes show only after deploy.",
        "",
        "## Scores",
        "",
        "| Category | Score | Passed audits |",
        "|---|---|---|",
    ]
    for score in report.scores:
        value = "n/a" if score.score is None else str(score.score)
        lines.append(f"| {score.title} | {value} | {score.passed_audits} |")

    lines += ["", "## Core Web Vitals (lab)", "", "| Metric | Value | Rating |", "|---|---|---|"]
    lines += [f"| {v.title} | {v.display_value} | {v.rating.value} |" for v in report.vitals]

    lines += ["", f"## Action items ({len(report.actions)})", ""]
    lines.append(
        "Sorted by estimated time savings, then byte savings, then category."
        if report.actions
        else "No failing audits."
    )
    for index, action in enumerate(report.actions, start=1):
        lines += ["", *_render_action(index, action)]
    return "\n".join(lines) + "\n"


def _render_action(index: int, action: ActionItem) -> list[str]:
    savings = format_measures(action.savings_ms, action.savings_bytes)
    heading = f"### {index}. [{action.category_id}] {action.title}"
    if savings:
        heading += f": est. savings {savings}"
    lines = [heading, "", f"- Audit id: `{action.audit_id}`"]
    if action.display_value:
        lines.append(f"- Lighthouse says: {action.display_value}")
    if action.description:
        lines.append(f"- Why: {action.description}")
    if action.affected:
        lines.append("- Affected:")
        lines += [f"  - {_render_item(item)}" for item in action.affected]
        if action.more_affected:
            lines.append(f"  - +{action.more_affected} more")
    return lines


def _render_item(item: DetailItem) -> str:
    node = item.node
    selector = f"selector `{node.selector}`" if node and node.selector else None
    if item.url:
        label = f"{item.url} at {selector}" if selector else item.url
    else:
        label = selector or "element"
        if node and node.snippet:
            label += f": `{node.snippet}`"
    wasted = format_measures(item.wasted_ms, item.wasted_bytes)
    return f"{label} ({wasted} wasted)" if wasted else label
