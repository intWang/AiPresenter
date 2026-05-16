# Cycle 004 Demand Analysis

Date: 2026-05-16
Role: demand-analysis explorer
Write scope: this file only

## Read Scope

Reviewed local repo evidence only:

- `README.md`
- `docs/agent-handoffs/cycle-000-summary.md`
- `docs/agent-handoffs/cycle-001-implementation.md`
- `docs/agent-handoffs/cycle-001-retro.md`
- `docs/agent-handoffs/cycle-002-summary.md`
- `docs/agent-handoffs/cycle-003-summary.md`
- `src/ai_presenter/runtime/controller.py`
- `src/ai_presenter/runtime/questions.py`
- `src/ai_presenter/runtime/voice.py`
- `src/ai_presenter/runtime/session.py`
- `src/ai_presenter/runtime/sync.py`
- `src/ai_presenter/runtime/package_demo.py`
- `src/ai_presenter/runtime/diagnostics.py`
- `src/ai_presenter/packages/models.py`
- `packages/ringcentral-video.yaml`
- `docs/knowledge/ringcentral-video/*.md`
- focused unit tests around controller, questions, material packages, material runtime, and logging

No implementation files were modified.

## Context After Cycle 004

Cycle 001 delivered the core controller-trust slice: queued safe question interrupts, deterministic Chinese aliases, clearer question results, and regression coverage for resume ordering. Cycle 002 created the RingCentral knowledge package. Cycle 003 recorded the first read-only live observation for RingCentral Video `26.2.20.355`. The current working tree also shows the Cycle 004 direction has been implemented in code/package tests: `ringcentral.video.main.add-coworkers` now has a UIA `clickWindowControl` route and `tests/unit/test_material_packages.py` expects that route.

The best next cycles should therefore avoid redoing interruption basics or the Add coworkers route. The leverage is now in making the controller more operationally trustworthy, making language/tone behavior scalable instead of special-cased, measuring performance before optimizing it, and keeping RingCentral package knowledge synchronized with live evidence.

## Ranked Opportunities

### 1. Controller Operator Cockpit And View-Model Split

Impact: high
Risk: medium
Theme coverage: UI, requirements, reliability

User value:

- The user can run a live demo with confidence: what target is active, what step is running, what is next, whether a question was queued or answer-only, whether a selected running app scan is stale, and why a control is not clickable.
- Button state can prevent common operator mistakes such as starting twice, scanning while running, or submitting a running-app question before scan.
- A pure view-model split makes future UI redesign safer without forcing an immediate Tk replacement.

Evidence from repo/docs:

- `README.md` documents the controller as the live control surface with target selection, running-app scan, language/tone selectors, and text questions.
- `docs/agent-handoffs/cycle-000-demand-analysis.md` and `cycle-001-retro.md` both call out controller operational clarity as a next demand area.
- `src/ai_presenter/runtime/controller.py` still builds the full Tk layout inline inside `run_controller()`, with `StringVar` state and closure-local scan/package variables.
- Existing pure helpers already point the way: `resolve_controller_status()`, `describe_question_result()`, `render_voice_label()`, `_RunningAppScanState`, and chat formatting are unit-tested.
- Tests cover controller service behavior but not a richer controller state model or button enablement.

Likely files:

- `src/ai_presenter/runtime/controller.py`
- possibly a new small module such as `src/ai_presenter/runtime/controller_view_model.py`
- `src/ai_presenter/runtime/session.py`
- `tests/unit/test_controller.py`
- `tests/unit/test_controller_session.py`
- `docs/runbooks/ringcentral-manual-acceptance.md`

Suggested tests:

- Pure view-model tests for idle/running/paused/ending/question-queued states.
- Button-state tests: Start disabled while running, Pause/End disabled while idle, Scan disabled without a real running app, Submit explains scan requirement for running-app mode.
- Step-display tests once runtime exposes current/next step or last step result.
- Manual acceptance update for controller labels, stale scan warning, and question-result status.

Why it fits a future cycle:

- It is the natural sequel to Cycle 001. Interrupts now work; the operator needs to see and trust them.
- It can be implemented mostly with pure helpers before touching Tk layout, keeping risk bounded.
- It creates a better foundation for language/tone and provider-readiness work because voice status becomes a visible first-class state.

### 2. Timing Telemetry, Scan Responsiveness, And Question Indexing

Impact: high
Risk: medium
Theme coverage: performance, reliability, requirements

User value:

- The user can tell whether lag comes from RingCentral binding, UIA scan, narration, TTS, playback, action execution, or cleanup.
- Controller refresh/scan should feel less likely to freeze during live use.
- Repeated questions against a package or temporary running-app package should avoid needless retokenization as package size grows.

Evidence from repo/docs:

- `docs/agent-handoffs/cycle-000-tech-scan.md` identifies missing timing spans for launch/bind, scan, capture, narration, TTS, audio playback, action execution, cleanup, and controller refresh.
- `src/ai_presenter/runtime/logging.py` only has basic logging configuration and secret-prefix redaction; there is no timed-operation helper.
- `src/ai_presenter/runtime/questions.py` recomputes Q&A and entrypoint tokens on every question.
- `MaterialPackage.entrypoint_by_id()` in `src/ai_presenter/packages/models.py` is linear.
- `run_controller()` calls visible-window refresh and visible-control scan synchronously from Tk callbacks.
- `tests/unit/test_runtime_logging.py` only verifies logger level and secret-like value redaction.

Likely files:

- `src/ai_presenter/runtime/logging.py`
- `src/ai_presenter/runtime/controller.py`
- `src/ai_presenter/runtime/questions.py`
- `src/ai_presenter/runtime/session.py`
- `src/ai_presenter/runtime/sync.py`
- `src/ai_presenter/runtime/package_demo.py`
- `src/ai_presenter/media/output.py`
- `tests/unit/test_runtime_logging.py`
- `tests/unit/test_questions.py`
- `tests/unit/test_controller.py`
- `tests/unit/test_material_runtime.py`

Suggested tests:

- Timed helper test with injected clock and redaction-safe structured fields.
- Focused `caplog` tests for a representative scan or timeline/action span without real desktop automation.
- Behavior-identical question matching tests before and after introducing a reusable package question index.
- Controller tests that scan status can enter "scanning" and recover from exceptions without changing selected target incorrectly.

Why it fits a future cycle:

- Performance concerns are plausible but still unmeasured. Instrumentation is the lowest-risk way to replace intuition with evidence.
- It also supports UI trust: the controller can display "Scanning..." or "Last scan took N ms" once timings exist.
- The question index is a small reliability/performance improvement that helps both material packages and running-app temporary packages.

### 3. Language/Tone Content Model And Skill-Aware Response Rendering

Impact: high
Risk: medium
Theme coverage: language/tone expansion, skills, requirements

User value:

- Chinese and future languages can be authored and tested as real content, not only produced by word replacement.
- Tone differences become consistent across scripted narration, Q&A, idle question answers, and provider prompts.
- Presenter skills and memory can shape live answers without weakening deterministic safety rules.

Evidence from repo/docs:

- `src/ai_presenter/runtime/voice.py` supports only `en` and `zh`, with deterministic tone rendering and a small `_CHINESE_REPLACEMENTS` dictionary.
- `DemoStepNarration.localized_text` already supports localized demo-step text, and `tests/unit/test_material_packages.py` requires `meeting-control-map-demo` to have real `zh` localized text.
- Package Q&A in `packages/ringcentral-video.yaml` has only `question`, `answer`, and related entrypoints. There is no localized Q&A schema.
- `src/ai_presenter/runtime/questions.py` stores Chinese aliases in code, not package content, and the test suite includes a mojibake negative regression.
- `docs/agent-handoffs/cycle-001-retro.md` warns that alias expansion must preserve real UTF-8 and keep safety separate from matching.
- `README.md` describes presenter soul, memory, and skills, but deterministic package Q&A mostly bypasses those skills except through pre-authored text.

Likely files:

- `src/ai_presenter/runtime/voice.py`
- `src/ai_presenter/runtime/questions.py`
- `src/ai_presenter/packages/models.py`
- `src/ai_presenter/runtime/controller.py`
- `src/ai_presenter/providers/openai_provider.py`
- `src/ai_presenter/providers/codex_cli.py`
- `packages/ringcentral-video.yaml`
- `src/ai_presenter/presenter/soul.md`
- `src/ai_presenter/presenter/memory.md`
- `src/ai_presenter/presenter/skills/*.md`
- `tests/unit/test_voice.py`
- `tests/unit/test_questions.py`
- `tests/unit/test_material_packages.py`
- `tests/unit/test_openai_provider.py`
- `tests/unit/test_codex_cli_provider.py`

Suggested tests:

- Package-model tests for localized Q&A fields, preserving backward compatibility.
- Question tests for localized answer selection and alias priority, including risky-control non-operability.
- Golden voice-rendering tests for professional, conversational, and concise in both `en` and `zh`.
- Provider prompt tests that voice instruction and skill context are included for generated narration without changing package facts.
- Encoding regression tests that mojibake strings do not become supported aliases.

Why it fits a future cycle:

- Cycle 001 made Chinese questions possible; the next step is moving multilingual content from hardcoded aliases and word replacement into package-owned knowledge.
- It directly advances the user's language/tone expansion goal while keeping English as the default polished path.
- It can stay deterministic at the safety boundary: matching may improve, but operation permission remains separate.

### 4. RingCentral Evidence Synchronization And Coverage Expansion

Impact: high
Risk: medium
Theme coverage: RingCentralVideo knowledge/package, requirements, reliability

User value:

- The RingCentral package remains believable as the product UI changes because docs, tests, and package routes agree.
- Future demos can cover more of RingCentral Video: captions/transcription, whiteboard, host/security, waiting room, scheduling/joining, recordings, summaries, and post-meeting artifacts.
- Locators become safer because each executable route has evidence, confidence, cleanup notes, and known layout variants.

Evidence from repo/docs:

- `docs/knowledge/ringcentral-video/source-index.md` lists official coverage gaps beyond the current in-meeting attendee controls.
- `docs/knowledge/ringcentral-video/state-matrix.md` lists weak or missing states: audio join prompt, camera preview, host not started, active sharing, recording consent/active, captions, transcription, whiteboard, breakout rooms, waiting room/security, CPU detail, and post-meeting artifacts.
- `docs/knowledge/ringcentral-video/privacy-matrix.md` already defines privacy and confirmation boundaries for these surfaces.
- `docs/knowledge/ringcentral-video/locator-matrix.md` now records `Add coworkers` as UIA, but several entries still have low confidence due to coordinates, `More` occurrence matching, side-panel cleanup, settings cleanup, and English-only UI labels.
- `packages/ringcentral-video.yaml` has strong in-meeting coverage but only 3 Q&A items.
- `tests/unit/test_material_packages.py` now protects the Add coworkers UIA route and complete meeting-control-map coverage.

Likely files:

- `packages/ringcentral-video.yaml`
- `docs/knowledge/ringcentral-video/source-index.md`
- `docs/knowledge/ringcentral-video/observation-log.md`
- `docs/knowledge/ringcentral-video/locator-matrix.md`
- `docs/knowledge/ringcentral-video/state-matrix.md`
- `docs/knowledge/ringcentral-video/privacy-matrix.md`
- `docs/knowledge/ringcentral-video/acceptance-runs.md`
- `src/ai_presenter/adapters/ringcentral.py`
- `src/ai_presenter/runtime/diagnostics.py`
- `tests/unit/test_material_packages.py`
- `tests/unit/test_ringcentral_profile.py`
- `tests/integration/test_ringcentral_profile.py`

Suggested tests:

- Package coverage tests for new entrypoints, explainers, privacy notes, and localized narration where applicable.
- Snapshot-style sanitized UIA fixtures for known RingCentral states, especially `More` variants, participants/chat panels, settings tabs, and Notes direct-vs-nested variants.
- Adapter tests for missing/weak states once fixtures exist.
- Doctor or coverage-report tests that flag executable entrypoints without locator confidence/evidence metadata.

Why it fits a future cycle:

- Cycle 002 and Cycle 003 built the evidence discipline; Cycle 004 changed a locator. The next leverage is keeping evidence synchronized and expanding coverage in that same disciplined style.
- It can be split into a doc/package-only cycle or a fixture-backed automation cycle depending on live RingCentral access.
- It improves both prepared demos and live Q&A because the package becomes a broader product knowledge base.

### 5. Explicit Safety Metadata And Confirmation Policy

Impact: medium-high
Risk: medium-high
Theme coverage: requirements, RingCentralVideo knowledge/package, skills, UI

User value:

- The user gets predictable, explainable behavior for risky actions: AiPresenter can understand intent without accidentally operating controls that affect a real meeting.
- Future confirmation workflows become possible for actions such as recording, leave/end, mute/unmute, camera toggle, invite, share, reactions, and settings changes.
- Controller UI can display safety disposition from data instead of from inferred keywords.

Evidence from repo/docs:

- `src/ai_presenter/runtime/questions.py` uses `_RISKY_ENTRYPOINT_WORDS` over id/title/purpose text to decide `can_operate`.
- `src/ai_presenter/runtime/temporary_package.py` was not deeply reviewed in this pass, but Cycle 000 notes describe conservative safe/risky classification for scanned running-app controls.
- `src/ai_presenter/packages/models.py` has no safety metadata on `OperationEntrypoint`.
- `docs/knowledge/ringcentral-video/privacy-matrix.md` defines operation modes and notes that scripted-demo safety does not automatically imply real-meeting safety.
- `packages/ringcentral-video.yaml` encodes safety in presenter notes and by omitting `openSteps` for some explain-only entrypoints, but this is not a queryable policy model.
- Controller result text can say a matched entrypoint is "not safe to operate automatically", but it cannot cite a structured reason.

Likely files:

- `src/ai_presenter/packages/models.py`
- `src/ai_presenter/runtime/questions.py`
- `src/ai_presenter/runtime/session.py`
- `src/ai_presenter/runtime/controller.py`
- `src/ai_presenter/runtime/temporary_package.py`
- `packages/ringcentral-video.yaml`
- `docs/knowledge/ringcentral-video/privacy-matrix.md`
- `tests/unit/test_questions.py`
- `tests/unit/test_material_packages.py`
- `tests/unit/test_temporary_package.py`
- `tests/unit/test_controller.py`

Suggested tests:

- Schema tests for optional safety metadata such as `operationMode`, `requiresConfirmation`, `privacySensitive`, `permissionDependent`, and `riskReason`.
- Question tests proving metadata overrides lexical fallback and risky matched controls remain non-operable.
- Controller tests for user-visible safety messages derived from metadata.
- Package tests that every RingCentral entrypoint has either explicit safety metadata or a documented fallback classification.

Why it fits a future cycle:

- It is the cleanest way to scale beyond hardcoded risky words as package coverage grows.
- It gives UI, skills, and Q&A one shared safety source of truth.
- It should come before any attempt to make currently explain-only RingCentral actions operable after confirmation.

## Recommended Next Cycle

Recommended next: **Controller Operator Cockpit And View-Model Split**, with a small telemetry hook if scope allows.

Reasoning:

- It has the highest direct user value after Cycle 004: the package route is being hardened, and the next pain is operating the demo with confidence.
- It builds on existing tested helpers instead of touching fragile desktop automation first.
- It creates display surfaces for later work: scan timing, provider readiness, language/tone, safety disposition, locator confidence, and RingCentral evidence freshness.

Suggested cycle shape:

1. Add pure controller view-model helpers for target, flow, voice, running state, scan freshness, question result, safety disposition, and button enabled states.
2. Wire the Tk controller to those helpers with minimal layout change.
3. Add one user-visible "current/next/last" status row if current runtime data is already available; otherwise start with target/voice/scan/question safety.
4. Add focused tests around pure helpers and keep manual acceptance small.

Second choice: **Timing Telemetry, Scan Responsiveness, And Question Indexing** if the user is feeling runtime lag during demos.

Third choice: **RingCentral Evidence Synchronization And Coverage Expansion** if live RingCentral access is available and the user wants deeper product coverage before more controller work.
