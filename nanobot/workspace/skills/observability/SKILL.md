---
name: observability
description: Investigate recent backend errors with logs and traces
always: true
---

# Observability Skill

Use observability tools for questions about errors, failures, incidents, slow
requests, and traces. Prefer recent, scoped evidence from VictoriaLogs and
VictoriaTraces over guesses.

When the user asks "What went wrong?" or "Check system health", treat that as a
request for a one-shot investigation rather than a generic status summary.

## Available tools

- `logs_search`: search recent logs by keyword, severity, service, and time window
- `logs_error_count`: count recent error logs per service
- `traces_list`: list recent traces for a service
- `traces_get`: inspect a trace by trace ID

## Strategy

- If the user asks about recent errors, call `logs_error_count` first.
- If errors exist, call `logs_search` with a narrow window and the LMS backend
  service name to find specific failures.
- If a relevant log record contains a `trace_id`, call `traces_get` for that
  trace and use it to explain where the failure happened.
- Keep the scope narrow by default, such as the last 10 minutes, unless the
  user asks for a different time range.
- Prefer the LMS backend when the user asks about "the backend" or "LMS backend".
- For "What went wrong?" and "Check system health", use this sequence:
  1. `logs_error_count` on a fresh recent window
  2. `logs_search` for the most likely failing service with `severity="ERROR"`
  3. `traces_get` for the most relevant recent `trace_id`, if available
  4. one short explanation that cites both log evidence and trace evidence
- Do not stop after only log evidence if a recent `trace_id` is present. Follow
  the trace and mention at least one failing span or operation in the final
  answer.
- If `logs_search` returns multiple records, prefer the newest error record that
  includes a `trace_id`.
- For the LMS failure path in this lab, be alert for a mismatch between the
  backend's user-facing HTTP response and the deeper database failure shown by
  the trace.
- When PostgreSQL-related failures appear, explicitly distinguish the real
  backend/database failure from any misleading user-facing HTTP status.
- If there are no recent errors, say the system looks healthy.
- For recurring health-check requests in chat, use the built-in `cron` tool to
  create a scheduled job for the current chat session.

## Response style

- Summarize findings briefly.
- Mention both the service and the failure type when you can.
- Do not dump raw JSON unless the user explicitly asks for it.
- For investigations, mention:
  - the affected service
  - the key recent error log
  - the relevant trace ID
  - the failing span or operation from the trace
  - the likely root failing operation
- If the backend response appears misleading, say so explicitly.
