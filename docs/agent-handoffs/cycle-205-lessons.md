# Cycle 205 Lessons: Source Metadata Without Evidence Leakage

## Reusable Lesson

When surfacing guard context in CLI output, render only source metadata and state. For evidence-sensitive docs, showing the path and whether it was explicit, auto-discovered, or absent is useful; rendering body text is a privacy and evidence-boundary risk.

## Prompt Pattern

Ask reviewers: "Does this output help users understand which guard source was loaded without printing any acceptance-run content or implying live validation?" If not, tighten output to path plus source state only.

## Test Lesson

Visibility tests should include both positive metadata assertions and negative leakage assertions. For acceptance-runs output, assert that body-only field names such as `Steps executed`, `Promotion rationale`, and `Privacy notes` do not appear in `validation-targets` stdout.

## Follow-Up Candidates

- Add CLI help or docs examples showing `--acceptance-runs`.
- Consider showing acceptance-runs source in JSON output if a structured output mode is added later.
- Reuse the explicit/auto-discovered/absent source pattern for future sidecar knowledge files.
