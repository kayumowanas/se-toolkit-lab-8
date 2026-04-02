"""Async clients and helpers for VictoriaLogs and VictoriaTraces."""

from __future__ import annotations

import json
from collections import Counter
from typing import Any

import httpx

from mcp_obs.models import ErrorCount, LogRecord, TraceDetails, TraceSpan, TraceSummary


class ObservabilityClient:
    def __init__(
        self,
        victorialogs_url: str,
        victoriatraces_url: str,
        *,
        http_client: httpx.AsyncClient | None = None,
        timeout: float = 10.0,
    ) -> None:
        self.victorialogs_url = victorialogs_url.rstrip("/")
        self.victoriatraces_url = victoriatraces_url.rstrip("/")
        self._owns_client = http_client is None
        self._http_client = http_client or httpx.AsyncClient(timeout=timeout)

    async def __aenter__(self) -> ObservabilityClient:
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        if self._owns_client:
            await self._http_client.aclose()

    async def logs_search(
        self,
        *,
        keyword: str,
        minutes: int,
        service_name: str,
        severity: str,
        limit: int,
    ) -> list[LogRecord]:
        query = self._build_logs_query(
            keyword=keyword,
            minutes=minutes,
            service_name=service_name,
            severity=severity,
        )
        response = await self._http_client.get(
            f"{self.victorialogs_url}/select/logsql/query",
            params={"query": query, "limit": limit},
        )
        response.raise_for_status()
        payload = self._parse_logs_payload(response)
        return [self._log_record(item) for item in payload]

    async def logs_error_count(
        self,
        *,
        minutes: int,
        service_name: str,
    ) -> list[ErrorCount]:
        records = await self.logs_search(
            keyword="",
            minutes=minutes,
            service_name=service_name,
            severity="ERROR",
            limit=200,
        )
        counts = Counter(
            record.service_name or service_name or "unknown"
            for record in records
        )
        return [
            ErrorCount(service_name=name, error_count=count)
            for name, count in counts.items()
        ]

    async def traces_list(self, *, service: str, limit: int) -> list[TraceSummary]:
        response = await self._http_client.get(
            f"{self.victoriatraces_url}/select/jaeger/api/traces",
            params={"service": service, "limit": limit},
        )
        response.raise_for_status()
        data = response.json().get("data", [])
        return [self._trace_summary(item) for item in data]

    async def traces_get(self, *, trace_id: str) -> TraceDetails:
        response = await self._http_client.get(
            f"{self.victoriatraces_url}/select/jaeger/api/traces/{trace_id}"
        )
        response.raise_for_status()
        payload = response.json().get("data", [])
        if not payload:
            return TraceDetails(trace_id=trace_id, span_count=0, services=[], spans=[])
        return self._trace_details(payload[0])

    def _build_logs_query(
        self,
        *,
        keyword: str,
        minutes: int,
        service_name: str,
        severity: str,
    ) -> str:
        parts = [f"_time:{minutes}m"]
        if service_name:
            parts.append(f'service.name:"{service_name}"')
        if severity:
            parts.append(f"severity:{severity}")
        if keyword:
            parts.append(json.dumps(keyword))
        return " ".join(parts)

    def _parse_logs_payload(self, response: httpx.Response) -> list[dict[str, Any]]:
        text = response.text.strip()
        if not text:
            return []
        try:
            parsed = response.json()
        except json.JSONDecodeError:
            parsed = None
        if isinstance(parsed, list):
            return [item for item in parsed if isinstance(item, dict)]
        if isinstance(parsed, dict):
            data = parsed.get("data")
            if isinstance(data, list):
                return [item for item in data if isinstance(item, dict)]
            return [parsed]
        records: list[dict[str, Any]] = []
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                parsed_line = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(parsed_line, dict):
                records.append(parsed_line)
        return records

    def _log_record(self, item: dict[str, Any]) -> LogRecord:
        return LogRecord(
            timestamp=str(item.get("_time", "")),
            service_name=str(item.get("service.name", item.get("service_name", ""))),
            severity=str(item.get("severity", "")),
            event=str(item.get("event", "")),
            trace_id=str(item.get("trace_id", "")),
            message=str(
                item.get("_msg", item.get("body", item.get("message", "")))
            ),
            raw=item,
        )

    def _trace_summary(self, item: dict[str, Any]) -> TraceSummary:
        processes = item.get("processes", {})
        spans = item.get("spans", [])
        services = sorted(
            {
                str(processes.get(span.get("processID", ""), {}).get("serviceName", ""))
                for span in spans
                if isinstance(span, dict)
            }
            - {""}
        )
        operations = sorted(
            {
                str(span.get("operationName", ""))
                for span in spans
                if isinstance(span, dict) and span.get("operationName")
            }
        )
        return TraceSummary(
            trace_id=str(item.get("traceID", "")),
            span_count=len(spans),
            services=services,
            operations=operations,
        )

    def _trace_details(self, item: dict[str, Any]) -> TraceDetails:
        processes = item.get("processes", {})
        spans_payload = item.get("spans", [])
        spans: list[TraceSpan] = []
        services: set[str] = set()
        for span in spans_payload:
            if not isinstance(span, dict):
                continue
            process = processes.get(span.get("processID", ""), {})
            service_name = str(process.get("serviceName", ""))
            if service_name:
                services.add(service_name)
            tags = {
                str(tag.get("key", "")): tag.get("value")
                for tag in span.get("tags", [])
                if isinstance(tag, dict)
            }
            spans.append(
                TraceSpan(
                    span_id=str(span.get("spanID", "")),
                    operation_name=str(span.get("operationName", "")),
                    service_name=service_name,
                    start_time=span.get("startTime", ""),
                    duration_ms=float(span.get("duration", 0)) / 1000.0,
                    tags=tags,
                )
            )
        return TraceDetails(
            trace_id=str(item.get("traceID", "")),
            span_count=len(spans),
            services=sorted(services),
            spans=spans,
        )
