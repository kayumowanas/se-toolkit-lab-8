---
name: lms
description: Use LMS MCP tools for live course data
always: true
---

# LMS Skill

Use the LMS MCP tools for questions about labs, scores, pass rates, completion,
groups, learners, timelines, or LMS health. Prefer live LMS data over local
repository files whenever LMS tools are available.

## Available tools

- `lms_health`: check whether the LMS backend is healthy and report item count
- `lms_labs`: list labs available in the LMS
- `lms_learners`: list learners registered in the LMS
- `lms_pass_rates`: task-level pass-rate and average-score data for a lab
- `lms_timeline`: submission timeline for a lab
- `lms_groups`: group performance for a lab
- `lms_top_learners`: top learners for a lab
- `lms_completion_rate`: passed/total completion summary for a lab
- `lms_sync_pipeline`: trigger LMS sync if the backend has no data yet

## Strategy

- If the user asks what labs are available, call `lms_labs`.
- If the user asks whether the LMS is healthy, call `lms_health`.
- If the user asks for scores, pass rates, completion, groups, timeline, or top
  learners and does not specify a lab, call `lms_labs` first.
- If multiple labs are available and a lab is required, ask the user to choose
  one. Use the lab title as the default user-facing label and the lab id such as
  `lab-04` as the value when possible.
- If the backend returns no labs or no learner data, explain that clearly and
  mention that the sync pipeline may need to run.
- Use `lms_pass_rates` for pass-rate questions. Use `lms_completion_rate` only
  for completion questions, or when clarifying that no submissions exist yet.
- When the user asks "what can you do?", explain the current LMS tools and
  their limits briefly.

## Response style

- Keep answers concise.
- Format percentages clearly.
- Distinguish between "no submissions yet" and a true low score or low pass
  rate.
- When tool results and repository docs disagree, trust live LMS tool results.
