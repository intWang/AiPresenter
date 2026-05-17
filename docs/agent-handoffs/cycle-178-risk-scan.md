# Cycle 178 Risk Scan: Mixed Presenter Meta + RingCentralVideo Intents

Date: 2026-05-17
Scope: review-only scan; no code edits by this pass.

## Findings

- Mixed-intent route tests passed after adding English Chat aliases under `ringcentral.video.toolbar.chat`.
- Docs/package contract became stale when the Chat alias addition changed package-owned aliases from `165` to `169`.
- `runtime-safety-routing.md`, `source-index.md`, `observation-log.md`, diagnostics tests, and CLI doctor tests need to move together whenever package alias counts intentionally change.
- Workspace dirt includes `.coverage`; keep it uncommitted.

## Review Checklist

- Confirm lower-level routing before controller/session assertions: safe mixed prompts should resolve to the intended entrypoint and sensitive mixed prompts should remain answer-only.
- Keep controller/session tests representative, not exhaustive; broad phrase taxonomy belongs in `tests/unit/test_questions.py`.
- For safe mixed prompts, assert `entrypoint_id`, `can_operate=True`, interrupt/demo status, and no `Presenter settings:` answer.
- For sensitive mixed prompts, assert `entrypoint_id` may be present, `can_operate=False`, no interrupt, no queued demo, and no stop request.
- Use Unicode escapes or `PYTHONIOENCODING=utf-8` for CJK prompts; do not add mojibake variants as supported aliases.
- If package aliases change, update diagnostics count expectations and docs count claims in the same slice.

## Must-Not-Break Behaviors

- Q&A safety matching runs before Presenter meta matching.
- Pure Presenter meta prompts stay answer-only: no entrypoint, no operation permission, no interrupt, no `question-answer-demo`.
- Mixed prompts preserve explicit RingCentralVideo intent only through authored Q&A, package aliases, meeting-info location lookup, or entrypoint titles.
- Broad token fallback stays skipped while Presenter meta matching is active.
- `questionPolicy: answerOnly` means no interrupt even when an entrypoint is identified.
- Tone/language rendering must not change route, permission, or interrupt behavior.
- Repo tests are not live RingCentral acceptance evidence.

## Verification Performed By Review Agent

Focused mixed routing/controller/session slice passed in the review agent. The diagnostics alias count check failed until expected count and durable docs were updated from `165` to `169`.

## Suggested Final Commands

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -B -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests\unit\test_questions.py tests\unit\test_controller.py tests\unit\test_controller_session.py tests\unit\test_diagnostics.py::test_diagnostics_reports_question_aliases_ok_for_ringcentral_package tests\unit\test_material_packages.py::test_operation_entrypoints_support_package_owned_question_aliases
.\.venv\Scripts\python.exe -B -m ruff check tests\unit\test_questions.py tests\unit\test_controller.py tests\unit\test_controller_session.py tests\unit\test_diagnostics.py tests\unit\test_material_packages.py
git diff --check -- packages\ringcentral-video.yaml tests\unit\test_questions.py tests\unit\test_controller.py tests\unit\test_controller_session.py tests\unit\test_diagnostics.py tests\unit\test_cli.py tests\unit\test_material_packages.py docs\knowledge\ringcentral-video
git status --short
```

## No-Go Conditions

- Adding controller/session mixed-intent tests while lower-level route tests are red.
- Leaving alias-count diagnostics or durable docs stale after package alias changes.
- Treating mojibake or bare CJK safety/status words as supported meta/control prompts.
- Claiming persistent voice-state mutation from natural-language Presenter meta prompts.
- Promoting repo-local routing tests to live RingCentral acceptance.
