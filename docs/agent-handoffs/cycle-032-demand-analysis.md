# Cycle 032 Demand Analysis: RingCentral Safety Presenter Skill

Date: 2026-05-16
Role: demand discovery
Scope: review-only demand analysis. No production code was edited in this pass.

## Recommendation

Add a dedicated `ringcentral-safety.md` presenter skill and load it through RingCentral profiles.

This is the best next slice because RingCentralVideo privacy, evidence, and validation knowledge already exists, but it is scattered across knowledge docs and package notes. Current presenter skills are generic: they tell the presenter to avoid private or destructive actions, but they do not encode RingCentral-specific boundaries.

No executable RingCentral Video route is fully `Accepted` for live operation yet. Presenter language needs to distinguish observed, repo-tested, blocked, and accepted routes without implying unattended live safety.

## User And Operator Pain

- Operators need the presenter to explain RingCentral Video confidently without reading private meeting content.
- Risky surfaces such as meeting info, invite links, participants, chat, shared content, notes, transcripts, recording, settings, and leave/end are easy to over-explain or accidentally frame as executable.
- The current safety knowledge lives in `privacy-matrix.md`, `validation-checklist-index.md`, `evidence-index.md`, and `packages/ringcentral-video.yaml`, so model-backed narration does not get one compact RingCentral-specific behavior guide.
- A presenter should be able to answer "where is it", "can you read it", and "can you do it" questions with the right privacy and evidence boundary.

## Minimum Scope

- Add `presenter/skills/ringcentral-safety.md`.
- Add the packaged copy under `src/ai_presenter/presenter/skills/`.
- Add the skill path to every RingCentral profile that currently loads `app-director.md` and `live-explainer.md`.
- Update presenter context tests for stable skill order.
- Update provider prompt tests proving the skill reaches narration context.
- Do not change package routes, runtime action policy, live validation docs, controller behavior, or acceptance evidence.

## Skill Content

Include:

- Default to explain-only for private, destructive, role-gated, or state-changing controls.
- Cover meeting info, network diagnostics, invite/add coworkers, participants, chat, screen share, mic/camera, background, reactions, raise hand, notes/transcript, recording, settings/security, leave/end, and post-meeting artifacts.
- Include evidence-language discipline: `Accepted` vs `Observed` vs `Repo-tested` vs `Blocked`.
- Explain that question intent can match risky requests, but operation permission still comes from runtime/package safety gates.
- Include safe recovery language: if the UI is uncertain, stop at explanation and avoid acting.

Exclude:

- Full privacy matrix duplication.
- Locator coordinates, UIA occurrence order, DPI/window bounds, or build-specific evidence.
- Acceptance run records.
- New confirmation workflow or deterministic runtime safety gate.
- Any promise that a prompt skill alone enforces safety.

## Acceptance Criteria

- RingCentral profiles load three presenter skills in this order: `app-director`, `live-explainer`, `ringcentral-safety`.
- Formatted presenter context includes `Presenter skill - ringcentral-safety:`.
- OpenAI and Codex CLI provider prompt tests include a unique safety skill marker.
- The new skill states that recording and leave/end remain explain-only by default.
- The new skill states that chat and participant names are not read by default.
- Focused tests pass without requiring live RingCentral.

## Risks

- Prompt context improves model behavior but does not replace deterministic `can_operate` gates.
- Root and packaged skill copies can drift.
- Profile copies can drift between development profiles and packaged profile.
- Overly long skill content can dilute high-signal provider instructions.
- Safety docs can drift over time; future changes to `privacy-matrix.md` should review this skill.

## Suggested Verification

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_config_loader.py tests\unit\test_presenter_context.py tests\unit\test_openai_provider.py::test_narration_instructions_include_presenter_soul_and_memory tests\unit\test_codex_cli_provider.py::test_codex_cli_prompt_includes_presenter_soul_and_memory
.\.venv\Scripts\ruff check --no-cache tests\unit\test_config_loader.py tests\unit\test_presenter_context.py tests\unit\test_openai_provider.py tests\unit\test_codex_cli_provider.py
.\.venv\Scripts\mypy --no-incremental src\ai_presenter\runtime\presenter_context.py src\ai_presenter\config tests\unit\test_config_loader.py tests\unit\test_presenter_context.py tests\unit\test_openai_provider.py tests\unit\test_codex_cli_provider.py
```

## Inputs Reviewed

- `docs/knowledge/ringcentral-video/privacy-matrix.md`
- `docs/knowledge/ringcentral-video/validation-checklist-index.md`
- `docs/knowledge/ringcentral-video/evidence-index.md`
- `packages/ringcentral-video.yaml`
- `presenter/skills/app-director.md`
- `presenter/skills/live-explainer.md`
- `docs/agent-handoffs/cycle-031-summary.md`
