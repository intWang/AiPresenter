# Cycle 188 Risk Scan

Date: 2026-05-17

## Findings

- P1 wording risk: examples could be mistaken for live acceptance or new permissions unless the docs explicitly say they are policy/routing guidance only.
- P2 scope risk: adding examples should not change YAML, aliases, route permissions, locator confidence, localization counts, or acceptance runs.
- P2 staging risk: `.coverage` remains modified by test runs and must stay out of the commit.

## Guardrails

- Do not edit `packages/ringcentral-video.yaml`.
- Do not edit `acceptance-runs.md` without an actual dated run.
- Do not use words such as accepted, validated, verified live, or works in RingCentral for these examples.
- Recording remains explain-only. Notes/transcript, chat, and meeting information do not permit content reading by default.

## Suggested Checks

```powershell
rg -n "Private Surface Examples|docs-only|accepted|validated|verified live|works in RingCentral" docs\knowledge\ringcentral-video
git diff --name-only -- packages profiles src\ai_presenter\profiles pyproject.toml
git diff --check
```
