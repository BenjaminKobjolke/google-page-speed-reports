"""Pydantic models for the subset of the PSI v5 / Lighthouse response this tool reads."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from pydantic.alias_generators import to_camel


class PsiModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, extra="ignore")


class NodeRef(PsiModel):
    selector: str | None = None
    snippet: str | None = None
    node_label: str | None = None


def _list_or_empty(value: Any) -> Any:
    """Checklist details send `items` as a dict of named checks; those name no resource."""
    return value if isinstance(value, list) else []


class DetailItem(PsiModel):
    url: str | None = None
    wasted_bytes: float | None = None
    wasted_ms: float | None = None
    node: NodeRef | None = None
    # "list" details nest whole tables as items.
    items: list[DetailItem] = Field(default_factory=list)

    _items_list = field_validator("items", mode="before")(_list_or_empty)

    @model_validator(mode="before")
    @classmethod
    def _url_from_source(cls, data: Any) -> Any:
        """Use `source.url` (source-location items, e.g. deprecations) when there is no url."""
        if not isinstance(data, dict):
            return data
        url = data.get("url")
        if not isinstance(url, str):
            source = data.get("source")
            source_url = source.get("url") if isinstance(source, dict) else None
            data = {**data, "url": source_url if isinstance(source_url, str) else None}
        return data


class AuditDetails(PsiModel):
    type: str | None = None
    overall_savings_ms: float | None = None
    overall_savings_bytes: float | None = None
    items: list[DetailItem] = Field(default_factory=list)

    _items_list = field_validator("items", mode="before")(_list_or_empty)


class Audit(PsiModel):
    id: str
    title: str
    description: str = ""
    score: float | None = None
    score_display_mode: str = ""
    display_value: str | None = None
    details: AuditDetails | None = None
    metric_savings: dict[str, float] = Field(default_factory=dict)


class AuditRef(PsiModel):
    id: str
    group: str | None = None


class Category(PsiModel):
    id: str
    title: str
    score: float | None = None
    audit_refs: list[AuditRef] = Field(default_factory=list)


class RuntimeErrorInfo(PsiModel):
    code: str
    message: str


class LighthouseResult(PsiModel):
    requested_url: str
    final_displayed_url: str | None = None
    fetch_time: str
    runtime_error: RuntimeErrorInfo | None = None
    categories: dict[str, Category]
    audits: dict[str, Audit]


class PsiResponse(PsiModel):
    lighthouse_result: LighthouseResult
