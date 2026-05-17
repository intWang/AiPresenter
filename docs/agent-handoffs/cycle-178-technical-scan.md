# Cycle 178 Technical Scan

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`

## Current Behavior

`src/ai_presenter/runtime/questions.py` routes in this order: Q&A match first, then presenter-meta detection, then entrypoint routing. Pure presenter meta prompts return `Presenter settings:` with `entrypoint_id=None` and `can_operate=False`.

Mixed meta prompts use `_match_explicit_entrypoint()`, which is intentionally narrower than normal fuzzy entrypoint matching: package aliases, meeting-info location lookup, and title/localized title containment. That keeps pure meta prompts from accidentally opening RingCentral controls.

`create_question_interrupt_step()` in `src/ai_presenter/runtime/session.py` is the operational gate: no `entrypoint_id` or `can_operate=False` means no interrupt step. `PresenterController.submit_question()` only queues or starts `question-answer-demo` when that helper returns a step.

Current working tree behavior after the alias/test changes:

- `Please be brief and open chat` routes to `ringcentral.video.toolbar.chat`, `can_operate=True`, and queues/starts `question-answer-demo`.
- `Please be brief and read meeting information aloud` routes to `ringcentral.video.top.meeting-info`, `can_operate=False`, and stays text-only.
- Chinese mixed meta plus Chat routes safely to Chat.
- Chinese mixed meta plus meeting-link copy stays text-only.

## Gaps Worth Testing

Add broader mixed-meta coverage beyond Chat so this does not become alias-specific:

- English safe intent: `Please be brief and show network quality` or `Please be brief and show participants`.
- English answer-only intent: `Please be brief and show Notes and Transcript`.
- Japanese/Spanish mixed-meta examples, especially meeting-info privacy/action prompts.

Keep a package/material test asserting English `open chat`, `show chat`, `where is chat`, and `chat button` belong to `ringcentral.video.toolbar.chat`, since mixed-meta routing depends on explicit aliases and should not fall back to fuzzy scoring.

## Reuse These Patterns

Question-layer pattern:

- `load_material_package(Path("packages/ringcentral-video.yaml"))`
- `answer_question(...)`
- `create_question_interrupt_step(package, response)`
- Assert `entrypoint_id`, `can_operate`, interrupt presence, and `not response.answer_text.startswith("Presenter settings:")`.

Controller fixtures:

- Reuse `_controller_inputs()` from `tests/unit/test_controller.py`.
- Running-demo queue pattern: `DemoControl()`, `threading.Event()`, `calls: list[str]`, runner waits on `release`.
- Idle pattern: runner appends `captured_flow_id`, then assert `calls == ["question-answer-demo"]` only for safe operable mixed intents.

Session fixtures:

- `ControllerSession()`
- `MaterialPackageTarget(profile=load_desktop_profile(), package=package, flow_id="meeting-control-map-demo")`
- Parametrize `(question, voice, expected_entrypoint_id, expected_answer)`.

## Production Code Necessity

No production runtime code looks necessary right now. The existing conservative routing guard is the right shape. For future misses, prefer adding package-owned `questionAliases` or localized titles for explicit RingCentralVideo intents rather than broadening `_match_explicit_entrypoint()` with fuzzy scoring.

Post-review update: after English Chat aliases were added, broad substring matching exposed a chat-content privacy bypass. The final implementation therefore added a narrow runtime safety helper for Chat content requests while keeping the general presenter-meta matcher conservative.

## Verification Notes

Focused no-coverage slices should include question routing, controller idle/running behavior, session interrupt gating, diagnostics alias count, and material package alias ownership. Full suite still needs to pass before commit.
