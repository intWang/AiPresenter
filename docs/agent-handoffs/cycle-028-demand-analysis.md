# Cycle 028 Demand Analysis: Next Optimization Slices

Date: 2026-05-16
Role: demand discovery
Scope: review-only demand analysis. No production code was edited in this pass.

## Context Reviewed

- Long-running user priorities: continue discovering AiPresenter requirements, improve UI/operator workflow and performance, expand language/tone coverage, improve presenter skills, and deepen the RingCentralVideo knowledge package.
- Recent handoffs from Cycles 018-027.
- RingCentralVideo knowledge docs under `docs/knowledge/ringcentral-video/`.
- Current CLI/package helpers: `acceptance-draft`, `validation-targets`, `localization-report`, `entrypoints`, `flows`, `voices`, and `doctor`.
- Presenter context files under `presenter/` and current `presenter/skills/`.

Recent trajectory:

- Cycles 018 and 021 created offline acceptance draft and validation target tooling.
- Cycles 022-026 closed Chinese RingCentral Q&A/demo localization and surfaced localization coverage.
- Cycle 027 protected the lightweight package-only CLI import boundary.
- The strongest remaining RingCentral gap is not package coverage; it is turning known evidence gaps into repeatable, low-friction acceptance work.

## Recommended Next Slice

### P1 - Stable RingCentral validation target IDs

Add explicit, stable target IDs to the RingCentral validation checklist and teach `validation-targets` to prefer them over label-derived slugs.

This is the best next implementation slice because the project now has useful validation discovery, but the target IDs are generated from human-readable checklist labels. Those labels are likely to change as the knowledge package matures. Stable IDs would make subagent prompts, runbooks, CLI examples, acceptance drafts, and future automation less brittle.

User/operator value:

- Operators can run commands such as `validation-targets --target rcv-add-coworkers-modal` without depending on the exact checklist title.
- Future agents can pass target IDs through handoffs and docs without re-reading the checklist table.
- The evidence workflow becomes more durable before any live RingCentralVideo validation begins.
- This strengthens the RingCentralVideo knowledge package while staying offline and privacy-safe.

Acceptance criteria:

- Add a `Target ID` column to `docs/knowledge/ringcentral-video/validation-checklist-index.md` for Priority Checklist rows and Do Not Execute Yet rows.
- Update validation target parsing so an explicit nonblank target ID is used when present; generated slugs remain a compatibility fallback only when the column is absent.
- Reject duplicate explicit target IDs and target IDs that normalize to blank.
- Preserve existing output shape except the displayed IDs now come from the explicit column.
- `validation-targets --package ringcentral-video --priority P0` lists the explicit P0 IDs.
- `validation-targets --package ringcentral-video --target <explicit-id>` renders the expected target detail and draft command.
- Existing generated-id behavior remains covered by temporary markdown fixture tests.
- No live RingCentral interaction, no evidence promotion, and no writes to `acceptance-runs.md`.

Out of scope:

- Do not append or edit completed acceptance evidence.
- Do not promote any route to `Accepted`.
- Do not change package entrypoint IDs, demo flows, route execution, cleanup behavior, or privacy policy.
- Do not add JSON output in the same slice unless the explicit-ID change is already complete and reviewed.

## Other Good Next Slices

### P1 - Controller operator summary rows

Turn the dense single-line controller summary into stable, compact rows backed by the existing pure view model.

User/operator value:

- The controller becomes easier to scan while a demo is running or blocked.
- Voice readiness, target state, scan freshness, question outcome, and disabled-action reasons stop competing in one long string.
- This continues the UI/operator workflow improvements from Cycles 019-020 without a full Tk redesign.

Acceptance criteria:

- Add a pure formatter, for example `render_controller_operator_summary_lines(view_model)`, that returns deterministic rows for target, voice, scan, question, and actions.
- Keep the existing button enablement and callback behavior unchanged.
- Render the rows in the current Tk controller status area with minimal layout churn.
- Add focused pure view-model tests for normal, voice-blocked, running-app scan-required, and submitted-question states.
- Run focused controller/view-model tests and full verification if production UI code is touched.

Out of scope:

- Do not replace Tk, redesign the controller, or add screenshots as required verification in this slice.
- Do not change Start/Pause/End/Refresh/Scan/Submit semantics.
- Do not add new runtime state telemetry unless needed for the existing labels.

### P2 - Presenter skill package expansion for RingCentral safety

Add a dedicated presenter skill for RingCentralVideo operator safety and evidence discipline, then load it through RingCentral profiles.

User/operator value:

- OpenAI/Codex narration providers get explicit, reusable instructions for RingCentral privacy boundaries, explain-only routes, cleanup expectations, and evidence-safe language.
- The user's priority of improving AiPresenter skills becomes concrete and testable.
- The skill would encode project-specific lessons now scattered across memory, knowledge docs, and handoffs.

Acceptance criteria:

- Add a new markdown skill under `presenter/skills/`, with a focused name such as `ringcentral-safety.md` or `acceptance-guardian.md`.
- The skill covers privacy boundaries, destructive controls, dialog cleanup, accepted-vs-observed evidence language, and how to answer when a route is not live-accepted.
- Add the skill path to all RingCentral profiles that currently load `app-director.md` and `live-explainer.md`.
- Update tests so presenter context loading proves the new skill is resolved and formatted.
- Add one provider prompt/instruction test proving the new skill content is included in OpenAI or Codex CLI narration context.

Out of scope:

- Do not change package routes or live execution policy.
- Do not duplicate all RingCentral knowledge docs inside the skill; keep it behavior-focused.
- Do not change default language or tone behavior.

### P2 - Q&A matcher performance index

Precompute package Q&A questions, localized question strings, alias candidates, and token sets for repeated live question matching.

User/operator value:

- Running controller sessions can answer repeated questions with less per-question recomputation.
- This addresses a known performance follow-up while staying inside the pure runtime question layer.
- The improvement is most useful for live sessions where question matching happens repeatedly against the same package.

Acceptance criteria:

- Introduce a small immutable matcher/index object or cache boundary for `runtime.questions`.
- Preserve current precedence: package Q&A, package-owned aliases, legacy aliases, then token scoring.
- Add tests proving package-owned longest alias precedence and localized Q&A behavior remain unchanged.
- Add a focused test or benchmark-style assertion that repeated calls reuse precomputed candidates rather than rebuilding all candidate token sets.
- Keep logging fields for `question_answered` unchanged.

Out of scope:

- Do not introduce semantic search, embeddings, LLM-based routing, or fuzzy Chinese segmentation.
- Do not remove the legacy alias fallback in this slice.
- Do not change safety/can-operate policy or add package schema fields.

## Suggested Cycle 028 Implementation Choice

Choose **P1 Stable RingCentral validation target IDs** for the next implementation cycle.

It is small, testable, and strongly aligned with the user's long-running operating model: each cycle should leave clearer prompts and documents for the next agent. It also improves RingCentralVideo knowledge packaging without requiring live RingCentral access, screenshots, or risky UI operations.

Suggested focused verification for that slice:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_validation_targets.py tests\unit\test_cli.py
.\.venv\Scripts\python -m ruff check --no-cache src\ai_presenter\acceptance\validation_targets.py src\ai_presenter\cli.py tests\unit\test_validation_targets.py tests\unit\test_cli.py
.\.venv\Scripts\python -m mypy --no-incremental src tests
```

If only docs and validation-target parsing are touched, a full test run is still recommended before closing the cycle because the CLI import boundary and package-only command behavior have become important regression surfaces.
