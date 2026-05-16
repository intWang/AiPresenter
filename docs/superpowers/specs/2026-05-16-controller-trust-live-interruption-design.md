# Controller Trust And Live Interruption Design

Date: 2026-05-16

## Context

Cycle 000 found one P0 product gap in the controller: safe question handling is framed as a temporary branch, but `PresenterController.submit_question()` currently stops the running demo and starts a single-step `question-answer-demo`. That demonstrates the answer, yet it does not preserve the original flow position as a true interruption.

The runtime already has a better primitive. `DemoControl` can queue `DemoStep` interrupts, and `MaterialDemoRuntime` checks `interrupt_source` before the next flow step. Because queued interrupts do not increment the main flow index, the original demo can continue naturally after the interrupt step.

Cycle 000 also found two adjacent trust gaps:

- Chinese output exists, but Chinese question input such as `聊天在哪里` does not match because the matcher only extracts Latin/digit tokens.
- The controller UI has useful controls, but its status model does not expose enough operational context for a live presenter to know whether an answer was text-only, safely queued, started while idle, blocked as risky, or waiting on a scan.

## Goals

- Use the existing interrupt queue for safe questions during an active demo so the main flow resumes afterward.
- Keep idle question behavior: if no demo is running, a safe question can still start a one-step answer demo.
- Preserve current safety posture: risky, destructive, privacy-sensitive, and non-executable controls remain text-only.
- Add deterministic Chinese question matching for high-frequency RingCentral Video controls without introducing model-based ambiguity.
- Add pure controller status/view helpers that make question result, safety disposition, target, voice, and scan freshness easier to display and test.
- Keep UI changes modest: no large Tk redesign in this cycle.
- Leave RingCentral package schema expansion and performance telemetry for later cycles.

## Non-Goals

- No voice-input feature.
- No broad RingCentral package expansion.
- No new confirmation workflow for risky controls.
- No full Tk visual redesign or browser/web controller.
- No LLM-based semantic matcher.
- No guarantee that localized RingCentral UI labels are supported; this cycle targets Chinese user questions against the current English-labeled package.

## Approaches Considered

### Recommended: Queue Safe Interrupts In The Current Demo

For running demos, `PresenterController.submit_question()` should call `DemoControl.enqueue_interrupt()` with the generated interrupt step. The active `MaterialDemoRuntime` will pick it up before the next main flow step, run it, and continue from the preserved `_next_index`.

Trade-off: the interrupt is serviced at a step boundary rather than stopping audio/action mid-step. That is a good first trust slice because it avoids partial action cleanup complexity.

### Alternative: Persist And Resume A Controller Flow Cursor

The controller could track the active flow id and step index, stop the current thread, run the question flow, then start a new thread from the saved cursor.

Trade-off: this duplicates runtime cursor logic and increases race risk around stop, cleanup, pending question targets, and voice changes. It is unnecessary because the runtime already supports queued interrupts.

### Alternative: Rebuild The Controller Around A View Model First

The cycle could start by extracting a full controller view model and then rewire interruptions through that.

Trade-off: this is valuable later, but it delays the P0 behavior fix. This cycle should add small pure helpers only where they support tested status and safety display.

## Design

### 1. Running Safe Questions

`PresenterController.submit_question()` already resolves a `QuestionResponse` and creates an interrupt step with `create_question_interrupt_step()`.

New behavior:

- If no interrupt step exists, return a text-only result.
- If a demo thread is running, enqueue the interrupt step on the current `DemoControl`.
- Do not call `request_stop()` for normal safe question interrupts.
- Do not set `_pending_target` for normal safe question interrupts.
- Return status `queued` with a message such as `I queued that for the next safe step.`
- Keep the current voice snapshot on the generated interrupt step by rendering its narration before enqueueing, through existing factory voice application or by constructing the step from the current voice. The simplest first pass keeps using the package/voice result already produced by `answer_question()`.

`MaterialDemoRuntime` remains responsible for preserving the flow cursor. Existing tests already show `DemoControl.enqueue_interrupt()` runs before the next flow step and does not advance the main flow.

### 2. Idle Safe Questions

If no demo is running, current behavior remains useful:

- Create a one-step `question-answer-demo`.
- Start it with `_start_target()`.
- Return status `started`.

This lets the controller answer and demonstrate a safe control even before the main tour starts.

### 3. End And Cancellation

`PresenterController.end()` should keep clearing pending queued work:

- Clear `_pending_target` and `_pending_voice`.
- Request stop on the active `DemoControl`.
- Resetting control for the next run should clear queued interrupts, as `DemoControl.reset()` already does.

There should be a regression test proving End after queueing a question does not run that question in a later session.

### 4. Chinese Question Matching

Keep matching deterministic and package-driven.

Add a small alias layer in `runtime.questions`:

- Curated aliases map common Chinese phrases to entrypoint ids or matching tokens.
- Initial RingCentral aliases should cover chat, participants, invite, share, microphone, camera, settings, background, recording, notes/transcript, reactions, raise hand, network quality, meeting info, and leave.
- Alias matches should prefer exact phrase containment before fuzzy token scoring.
- Alias matches must still pass `_can_operate()`. For example, `怎么离开会议` may match Leave, but it remains text-only.

The matcher should still support all existing English behavior. This cycle should not add broad NLP. The alias list should be deliberately small, auditable, and easy to extend.

### 5. Controller Status Helpers

Add pure helper types/functions in `runtime.controller` or a small adjacent module if the file becomes too crowded.

First-pass helpers:

- `QuestionDemonstrationStatus` gains `queued`.
- `QuestionSubmitResult` carries `entrypoint_id`, `can_operate`, and an answer/demo status message.
- A pure formatter can render question outcome text:
  - text-only fallback
  - risky matched control
  - safe queued interrupt
  - safe demo started while idle
- A pure voice-label helper can render `English / Professional`, `Chinese / Conversational`, etc.
- Scan freshness stays in `_RunningAppScanState`, but a helper can render `Ready`, `Needs scan`, or `No running app selected`.

Tk wiring can then show better status strings without requiring widget-level tests.

### 6. Error Handling

- If enqueueing a question fails because the controller is stopping, return text-only answer plus a clear status instead of starting a competing thread.
- If the running demo has already finished between the `is_running` check and enqueue, fall back to the idle start path.
- If a matched entrypoint is risky or non-executable, do not enqueue it.
- If Chinese input has no match, return the existing no-match message rendered in the selected language/tone.

## Testing Strategy

Use TDD for every behavior change.

Unit tests:

- Running safe question enqueues on `DemoControl` and does not stop the active demo.
- Queued interrupt is consumed by `MaterialDemoRuntime` and the next main flow step still runs afterward.
- Idle safe question still starts `question-answer-demo`.
- End clears queued question interrupts before a later run.
- Chinese questions match expected entrypoints:
  - `聊天在哪里` -> Chat, operable
  - `怎么邀请别人` -> Invite, non-operable
  - `怎么共享屏幕` -> Share, non-operable
  - `怎么离开会议` -> Leave, non-operable
  - `怎么设置背景` -> Background settings
- Existing English question tests remain unchanged.
- Status helper tests cover text-only, queued, started, risky, and no-match outcomes.

Integration-style tests with fakes:

- A fake long-running controller demo receives a safe question, the control queue contains the interrupt, no stop is requested, and the runner remains on the original flow.
- A fake `MaterialDemoRuntime` run order proves `main step -> queued interrupt -> next main step` when the question arrives after a step boundary.

Manual acceptance:

- Start controller with `ringcentral-video` and `meeting-control-map-demo`.
- Ask `chat` during the flow; verify answer is queued/demonstrated and the original flow continues afterward.
- Switch language to Chinese and ask `聊天在哪里`; verify it maps to Chat.
- Ask `怎么离开会议`; verify AiPresenter explains without clicking.

## Rollout

1. Write failing tests for queue-based controller interrupts.
2. Implement the minimal controller change to enqueue interrupts while running.
3. Write failing tests for Chinese alias matching and risky Chinese controls.
4. Implement alias matching without changing existing English scoring.
5. Write failing tests for question outcome/status helpers.
6. Add helper implementation and modest Tk status wiring.
7. Run focused tests, then full no-coverage test suite, ruff, and mypy.
8. Update `docs/agent-handoffs/` with Cycle 001 implementation and review notes.

## Self-Review

- No placeholder requirements remain.
- Scope is one implementation slice: live controller trust, not broad UI redesign or package expansion.
- The design uses existing runtime primitives instead of duplicating flow cursor state.
- Safety behavior remains conservative.
- Chinese support is explicitly limited to deterministic question aliases for current package knowledge.
