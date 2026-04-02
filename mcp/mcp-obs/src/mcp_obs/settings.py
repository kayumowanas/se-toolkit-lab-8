"""Runtime settings for the observability MCP server."""

from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    victorialogs_url: str = Field(..., alias="NANOBOT_VICTORIALOGS_URL")
    victoriatraces_url: str = Field(..., alias="NANOBOT_VICTORIATRACES_URL")
