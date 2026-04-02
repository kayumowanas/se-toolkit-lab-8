"""Typed models for observability tool payloads."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class LogsSearchQuery(BaseModel):
    keyword: str = Field(default="", description="Keyword or phrase to search for.")
    minutes: int = Field(default=10, ge=1, le=1440, description="Lookback window in minutes.")
    service_name: str = Field(
        default="Learning Management Service",
        description="Service name filter, for example 'Learning Management Service'.",
    )
    severity: str = Field(
        default="",
        description="Optional severity filter such as ERROR, INFO, or WARN.",
    )
    limit: int = Field(default=20, ge=1, le=200, description="Max number of log records to return.")


class LogsErrorCountQuery(BaseModel):
    minutes: int = Field(default=10, ge=1, le=1440, description="Lookback window in minutes.")
    service_name: str = Field(
        default="Learning Management Service",
        description="Optional service name filter.",
    )


class TracesListQuery(BaseModel):
    service: str = Field(
        default="Learning Management Service",
        description="Service name to query in VictoriaTraces.",
    )
    limit: int = Field(default=10, ge=1, le=50, description="Max traces to return.")


class TraceGetQuery(BaseModel):
    trace_id: str = Field(description="Trace identifier returned by logs or traces_list.")


class LogRecord(BaseModel):
    timestamp: str = ""
    service_name: str = ""
    severity: str = ""
    event: str = ""
    trace_id: str = ""
    message: str = ""
    raw: dict[str, Any] = Field(default_factory=dict)


class ErrorCount(BaseModel):
    service_name: str
    error_count: int


class TraceSummary(BaseModel):
    trace_id: str
    span_count: int
    services: list[str]
    operations: list[str]


class TraceSpan(BaseModel):
    span_id: str
    operation_name: str
    service_name: str
    start_time: int | str
    duration_ms: float
    tags: dict[str, Any] = Field(default_factory=dict)


class TraceDetails(BaseModel):
    trace_id: str
    span_count: int
    services: list[str]
    spans: list[TraceSpan]
