---
name: observability
description: Investigate recent backend errors with logs and traces
always: true
---

# Observability Skill

Use observability tools for questions about errors, failures, incidents, slow
requests, and traces. Prefer recent, scoped evidence from VictoriaLogs and
VictoriaTraces over guesses.

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

## Response style

- Summarize findings briefly.
- Mention both the service and the failure type when you can.
- Do not dump raw JSON unless the user explicitly asks for it.
- If there are no recent backend errors, say so clearly.
