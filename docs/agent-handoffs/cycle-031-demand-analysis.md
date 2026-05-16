# Cycle 031 Demand Analysis: Next AiPresenter Slice

Date: 2026-05-16
Role: demand discovery
Scope: review-only demand analysis. No production code was edited in this pass.

## Inputs Reviewed

- Long-running user priorities: continuously improve AiPresenter requirements fit, UI, performance, language/tone coverage, presenter skills, and RingCentralVideo knowledge.
- Cycle 027 summary: package-only CLI import hygiene now keeps `ai_presenter.cli` from loading diagnostics, voice assets, and provider modules at import time.
- Cycle 028 summary: `localization-report --require-complete` now acts as an optional package-only localization quality gate; aliases remain informational.
- Cycle 029 summary: RingCentral validation checklist rows now have stable explicit `rcv-*` target IDs.
- Cycle 030 summary and review: mixed flow-plus-entrypoint validation targets now produce complete offline acceptance draft commands; residual risks are shell quoting for future odd labels and a missing synthetic multi-flow fixture.
- Current controller surface: `ControllerOperatorViewModel` is pure and tested, but `render_controller_operator_summary()` still compresses source, target, flow, voice, scan, question, and action blockers into one long label.
- Current presenter skills: only `app-director.md` and `live-explainer.md` are loaded by RingCentral profiles; RingCentral-specific privacy/destructive-action guidance is present in package/knowledge docs but not in a dedicated presenter skill.
- Current Q&A matcher: localized RingCentral Q&A and package-owned aliases are covered, longest package alias wins, and timing is logged, but candidate data is rebuilt on each question.

## Ranking

| Rank | Candidate | User/Operator Value | Risk | Testability | RingCentralVideo Alignment | Recommendation |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Controller operator summary rows/UI scanability | High. This improves the live control surface operators actually watch while running demos, asking questions, or recovering from scan/voice blockers. It also directly addresses the user's UI optimization priority after several CLI-heavy cycles. | Medium. Tk layout changes are always more delicate than pure package helpers, but the existing pure view model gives a narrow entry point. | Medium-high. Most behavior can be locked in pure row-renderer tests, with a small controller wiring assertion; no live RingCentral run is needed. | Medium. It improves RingCentral operations by making target, flow, scan, voice, question, and blocked actions easier to read during RingCentral demos. | Do next. |
| 2 | RingCentral safety presenter skill | Medium-high. It turns scattered safety lessons into reusable presenter context for OpenAI/Codex narration, improving skill quality and safety language. | Low-medium. Mostly markdown/profile wiring, but behavior is prompt-quality rather than deterministic runtime behavior. | Medium. Tests can prove loading and prompt inclusion, but cannot fully prove narration quality. | High. It directly codifies RingCentral privacy, recording, leave/end, invite, chat, participant, transcript, and evidence boundaries. | Strong next skill/knowledge slice after UI rows. |
| 3 | Q&A matcher performance index | Medium. It is useful as package Q&A grows and repeated live questions become heavier, but current package size is still small and timing logs already provide visibility. | Medium. The precedence rules are subtle: package Q&A, localized Q&A, package aliases, legacy aliases, then token scoring. | Medium-high. Correctness can be tested well; performance checks should avoid brittle wall-clock assertions. | Medium. It supports RingCentral Q&A responsiveness, but does not add new RingCentral knowledge. | Defer until timing evidence or package size justifies it. |
| 4 | Acceptance draft command hardening | Low-medium. Shell-safe quoting and a synthetic multi-flow fixture would reduce residual risk from Cycle 030, but current labels and real group fallback are already safe enough. | Low. Small implementation surface. | High. Pure tests can cover it. | Medium. It hardens RingCentral acceptance tooling, but user-visible value is smaller than the above options. | Keep as opportunistic follow-up, not the main slice. |

## Recommended Slice

Implement **controller operator summary rows/UI scanability**.

The controller is now carrying more operator-facing state than the original single-line summary can comfortably hold:

- source mode,
- selected package or running app,
- flow,
- language/tone,
- voice asset readiness,
- running/stopping status,
- scan state,
- queued question outcome,
- disabled Start/Submit reasons.

The current single label is deterministic and tested, but it is hard to scan when voice assets are missing, a running app needs scan, or a question has just been queued. A row-based summary keeps the same state model and button behavior while making the live operator surface easier to read. This is the best next slice because it balances immediate operator value, UI progress, testability, and low RingCentral live-risk.

## Recommended Acceptance Criteria

- Add a pure row renderer in `src/ai_presenter/runtime/controller_view_model.py`, for example:
  - `render_controller_operator_summary_rows(view_model) -> tuple[str, ...]`
  - rows should be deterministic, compact, and stable enough for tests.
- The rows separate the current dense summary into scan-friendly lines, such as:
  - source/target/flow,
  - voice/language/tone/asset readiness,
  - run/scan state,
  - question state,
  - blocked action reasons when present.
- Preserve the existing `render_controller_operator_summary()` behavior or implement it as a join of the new rows so downstream callers are not forced to migrate at once.
- Update the Tk controller status area to render the row list as multiple compact labels or an equivalent multi-line label, without changing button callbacks or enablement rules.
- Add focused pure tests covering at least:
  - ready material package target,
  - missing local voice assets,
  - running desktop app selected but not scanned,
  - scanned running app with queued safe question,
  - running demo,
  - stopping controller.
- Add or update one controller wiring test to prove the UI consumes the row renderer rather than the old dense single-line summary.
- Keep the controller usable with both material package targets and scanned running-app targets.
- No live RingCentralVideo automation, clicks, screenshots, or acceptance evidence writes are required for this slice.

## Suggested Technical Shape

- Keep the state source as `ControllerOperatorViewModel`; do not add runtime polling or new controller state unless a row cannot be derived from existing fields.
- Prefer a small immutable row data shape only if plain strings become ambiguous. A minimal dataclass such as `ControllerSummaryRow(label: str, value: str, severity: str = "info")` can be considered, but plain strings are likely enough for the first slice.
- In `run_controller()`, replace the single `operator_summary` string with either:
  - a single `StringVar` containing newline-joined rows, or
  - a small list of labels refreshed from row strings.
- Keep layout churn low: the goal is scanability, not a controller redesign.
- Reuse existing tests in `tests/unit/test_controller_view_model.py` and `tests/unit/test_controller.py` as the main verification surface.

## Out Of Scope

- Do not replace Tk or redesign the full controller.
- Do not change Start, Pause, End, Refresh, Scan, Submit, or question submission semantics.
- Do not alter voice selection, voice readiness checks, profile loading, or provider behavior.
- Do not change RingCentral package routes, validation targets, acceptance draft behavior, or evidence docs.
- Do not introduce screenshots or live RingCentral validation as required verification.
- Do not add new Q&A matching logic, localization fields, language choices, or tone choices in this slice.

## Other Candidate Acceptance Criteria

### RingCentral Safety Presenter Skill

If chosen instead, acceptance should include:

- Add a focused `ringcentral-safety.md` presenter skill under both repo and packaged presenter skill locations if packaging requires both.
- Add the skill path to RingCentral profiles that currently load `app-director.md` and `live-explainer.md`.
- Cover privacy boundaries, destructive controls, recording, leave/end meeting, invite/chat/participants, notes/transcript, shared-screen content, cleanup, and evidence language.
- Update presenter context tests to prove the skill loads in profile order.
- Update OpenAI and/or Codex CLI provider prompt tests to prove the skill content reaches narration instructions.
- Do not change route execution policy or live automation behavior.

### Q&A Matcher Performance Index

If chosen instead, acceptance should include:

- Introduce a small immutable matcher/index boundary for package Q&A questions, localized questions, package aliases, legacy aliases, and token sets.
- Preserve current precedence and answer behavior exactly.
- Add tests for localized Q&A, package-owned alias precedence, longest alias wins, risky non-operable answers, and no-match fallback.
- Add a deterministic reuse test that proves repeated questions do not rebuild all candidate token sets.
- Do not add embeddings, semantic search, LLM routing, or wall-clock performance assertions.

### Acceptance Draft Command Hardening

If chosen instead, acceptance should include:

- Add shell-safe quoting for `--checklist-target` command rendering.
- Add a synthetic multi-flow target fixture proving ambiguous multi-flow targets stay checklist-only.
- Preserve current `rcv-controller-chat-question` mixed command behavior.
- Do not change acceptance draft semantics or write evidence.

## Recommended Next Step

Run a Cycle 031 technical scan for controller operator summary rows. It should inspect the current Tk controller layout, existing view-model tests, and the lowest-risk way to render multiple rows without disturbing controller behavior. The implementation should be UI-focused but still mostly pure-test driven.
