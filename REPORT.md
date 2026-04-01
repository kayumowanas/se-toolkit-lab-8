# Lab 8 — Report

Paste your checkpoint evidence below. Add screenshots as image files in the repo and reference them with `![description](path)`.

## Task 1A — Bare agent

### Prompt: What is the agentic loop?

The agentic loop is the fundamental cycle that autonomous AI agents follow to accomplish tasks. It typically consists of these core stages:

1. Perceive — gather information about the current state.
2. Think/Reason — analyze the situation and plan next steps.
3. Act — execute actions using available tools.
4. Observe — check the results of the action.
5. Repeat — continue until the goal is achieved.

The response also explained that this loop is what distinguishes agentic systems from simple chatbots: agents can take multi-step actions, recover from errors, and work toward complex goals independently.

### Prompt: What labs are available in our LMS?

The bare agent did not use live LMS backend data. Instead, it explored the local workspace with built-in file tools such as `list_dir` and `read_file`, then answered from repository documentation.

It reported information based on local files about:

- Lab 8 — The Agent is the Interface
- Required tasks 1–4
- Optional Telegram client task

This confirms the expected Part A behavior: without MCP tools, the agent can inspect local files and produce plausible answers, but it is not yet connected to the real LMS backend.

## Task 1B — Agent with LMS tools

<!-- Paste the agent's response to "What labs are available?" and "Describe the architecture of the LMS system" -->

## Task 1C — Skill prompt

<!-- Paste the agent's response to "Show me the scores" (without specifying a lab) -->

## Task 2A — Deployed agent

<!-- Paste a short nanobot startup log excerpt showing the gateway started inside Docker -->

## Task 2B — Web client

<!-- Screenshot of a conversation with the agent in the Flutter web app -->

## Task 3A — Structured logging

<!-- Paste happy-path and error-path log excerpts, VictoriaLogs query screenshot -->

## Task 3B — Traces

<!-- Screenshots: healthy trace span hierarchy, error trace -->

## Task 3C — Observability MCP tools

<!-- Paste agent responses to "any errors in the last hour?" under normal and failure conditions -->

## Task 4A — Multi-step investigation

<!-- Paste the agent's response to "What went wrong?" showing chained log + trace investigation -->

## Task 4B — Proactive health check

<!-- Screenshot or transcript of the proactive health report that appears in the Flutter chat -->

## Task 4C — Bug fix and recovery

<!-- 1. Root cause identified
     2. Code fix (diff or description)
     3. Post-fix response to "What went wrong?" showing the real underlying failure
     4. Healthy follow-up report or transcript after recovery -->
