"""Stdio MCP server exposing observability tools."""

from __future__ import annotations

import asyncio
import json
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool
from pydantic import BaseModel

from mcp_obs.models import (
    LogsErrorCountQuery,
    LogsSearchQuery,
    TraceGetQuery,
    TracesListQuery,
)
from mcp_obs.observability import ObservabilityClient
from mcp_obs.settings import Settings


class ToolSpec(BaseModel):
    name: str
    description: str
    model: type[BaseModel]


TOOL_SPECS = (
    ToolSpec(
        name="logs_search",
        description="Search VictoriaLogs by keyword, severity, service name, and time window.",
        model=LogsSearchQuery,
    ),
    ToolSpec(
        name="logs_error_count",
        description="Count recent error logs per service over a time window.",
        model=LogsErrorCountQuery,
    ),
    ToolSpec(
        name="traces_list",
        description="List recent traces for a service from VictoriaTraces.",
        model=TracesListQuery,
    ),
    ToolSpec(
        name="traces_get",
        description="Fetch a specific trace by trace ID from VictoriaTraces.",
        model=TraceGetQuery,
    ),
)


def _text(data: Any) -> list[TextContent]:
    if isinstance(data, BaseModel):
        payload: Any = data.model_dump()
    else:
        payload = [item.model_dump() for item in data]
    return [TextContent(type="text", text=json.dumps(payload, ensure_ascii=False))]


def create_server(client: ObservabilityClient) -> Server:
    server = Server("obs")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        result: list[Tool] = []
        for spec in TOOL_SPECS:
            schema = spec.model.model_json_schema()
            schema.pop("$defs", None)
            schema.pop("title", None)
            result.append(
                Tool(name=spec.name, description=spec.description, inputSchema=schema)
            )
        return result

    @server.call_tool()
    async def call_tool(
        name: str, arguments: dict[str, Any] | None
    ) -> list[TextContent]:
        try:
            if name == "logs_search":
                query = LogsSearchQuery.model_validate(arguments or {})
                return _text(
                    await client.logs_search(
                        keyword=query.keyword,
                        minutes=query.minutes,
                        service_name=query.service_name,
                        severity=query.severity,
                        limit=query.limit,
                    )
                )
            if name == "logs_error_count":
                query = LogsErrorCountQuery.model_validate(arguments or {})
                return _text(
                    await client.logs_error_count(
                        minutes=query.minutes,
                        service_name=query.service_name,
                    )
                )
            if name == "traces_list":
                query = TracesListQuery.model_validate(arguments or {})
                return _text(
                    await client.traces_list(service=query.service, limit=query.limit)
                )
            if name == "traces_get":
                query = TraceGetQuery.model_validate(arguments or {})
                return _text(await client.traces_get(trace_id=query.trace_id))
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
        except Exception as exc:
            return [
                TextContent(type="text", text=f"Error: {type(exc).__name__}: {exc}")
            ]

    _ = list_tools, call_tool
    return server


async def main() -> None:
    settings = Settings.model_validate({})
    async with ObservabilityClient(
        victorialogs_url=settings.victorialogs_url,
        victoriatraces_url=settings.victoriatraces_url,
    ) as client:
        server = create_server(client)
        async with stdio_server() as (read_stream, write_stream):
            init_options = server.create_initialization_options()
            await server.run(read_stream, write_stream, init_options)
