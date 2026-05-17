# Cycle 204 Demand Analysis: Wire Accepted Evidence Guard Into Validation Targets

## Value

Cycle 203 added the core traceability guard in `validate_entrypoint_evidence_index(..., acceptance_text=...)`, but normal validation-target discovery still called it without `acceptance_text`. That left the most common RingCentral validation tooling path able to list targets from an invalid `Accepted` evidence row if `acceptance-runs.md` existed but was not loaded.

Cycle 204 makes the guard part of the default RingCentral validation-target workflow so future users and agents catch invalid `Accepted` promotions while using `ai-presenter validation-targets`, not only when calling the lower-level evidence validator directly.

## Acceptance Criteria

- Extend `discover_validation_targets` in `src/ai_presenter/acceptance/validation_targets.py` to accept optional `acceptance_text`.
- When `evidence_text` is present, pass `acceptance_text` through to `validate_entrypoint_evidence_index`.
- Preserve current behavior when no acceptance text is supplied, so non-RingCentral or synthetic callers are not forced to provide an acceptance-runs file.
- Update `ai-presenter validation-targets` to read a sibling `acceptance-runs.md` when present and pass its text into `discover_validation_targets`.
- Expose `--acceptance-runs` so custom evidence indexes can be checked against a matching acceptance-runs file.
- Add unit coverage proving `discover_validation_targets(..., acceptance_text=...)` rejects an `Accepted` evidence row without a qualifying manual pass.
- Add CLI coverage proving `validation-targets` rejects an `Accepted` evidence row when the acceptance-runs text lacks a matching eligible manual pass.
- Keep the existing current-catalog success case passing: today no entrypoint is `Accepted`, so normal `validation-targets --package ringcentral-video` should still succeed.

## Non-Goals

- Do not mark any current RingCentral route as `Accepted`.
- Do not edit or fabricate `docs/knowledge/ringcentral-video/acceptance-runs.md`.
- Do not perform live RingCentral validation.
- Do not change the definition of `Accepted`, `Observed`, `Repo-tested`, `Backlog`, or `Blocked`.
- Do not make generated acceptance drafts count as acceptance evidence.
- Do not require acceptance-runs files for unrelated packages or callers that intentionally omit acceptance text.

## Privacy Constraints

- Preserve the metadata-first manual evidence policy.
- Do not require screenshots for guard satisfaction.
- Promotion evidence must remain sanitized and must not include chat text, participant names or roles, invite links, meeting IDs, dial-in details, emails, device lists, account/profile content, notes/transcripts, recordings, shared content, or room imagery.
- The guard should check that privacy notes exist, not inspect or encourage private content capture.

## Suggested Verification

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests\unit\test_validation_targets.py
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests\unit\test_cli.py
.\.venv\Scripts\python.exe -m pytest -q
```

Useful RED case: synthesize an evidence index where `ringcentral.video.toolbar.chat` is `Accepted` while `acceptance-runs.md` contains only current automated/read-only/ineligible records. `validation-targets` should fail before rendering target lines.
