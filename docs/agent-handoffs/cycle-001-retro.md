# Cycle 001 Retro

Date: 2026-05-16

## What Went Well

Cycle 001 picked a narrow, high-trust product slice and kept it coherent: running safe questions now queue into the active demo, Chinese typed questions can hit curated RingCentral controls, and the controller exposes clearer question outcome text. This was the right scale for a cycle because it addressed the P0 live-demo interruption gap without expanding the RingCentral package or redesigning the whole UI.

Subagent coordination worked well. Cycle 000 produced separate demand, technical, test, and RingCentral knowledge handoffs; Cycle 001 then converted those into a focused coordination log, design spec, implementation plan, and implementation handoff. The single-implementation-agent decision was especially useful because `controller.py` and `tests/unit/test_controller.py` were central shared files.

TDD was effective rather than ceremonial. The implementation handoff records meaningful RED/GREEN checkpoints for controller queue behavior, Chinese alias matching, status helpers, and the later mojibake cleanup. The best example was the added regression test that corrupted Chinese input such as `èŠå¤©` must not be treated as a supported alias. That turned an environment encoding hazard into an executable contract.

The design reused the existing runtime primitive, `DemoControl.enqueue_interrupt()`, instead of inventing a second resume cursor in the controller. That kept the behavior smaller and safer: the active `MaterialDemoRuntime` remains responsible for consuming interrupts at step boundaries and preserving main-flow progress.

The implementation also preserved safety boundaries. Risky or non-operable controls such as Invite, Share, and Leave can be matched from Chinese input, but still return answer-only results.

## Pitfalls Found

PowerShell Chinese display can lie. Earlier design/plan text showed mojibake versions of Chinese examples, while later implementation and tests contain real UTF-8 Chinese strings. Agents should not judge Chinese source correctness from terminal rendering alone; inspect file bytes/editor rendering when in doubt.

Do not encode mojibake as aliases. A corrupted string can accidentally become a "supported" phrase if copied from terminal output or an already-corrupted document. Alias lists should contain real UTF-8 phrases only, plus explicit negative tests for common mojibake samples when the area is encoding-sensitive.

Alias priority matters. Short generic aliases like `共享`, `背景`, or `设置` can shadow more specific phrases if matching returns on first hit. Cycle 001 fixed this by preferring the longest matching phrase. Future alias expansion should keep deterministic ordering or scoring explicit.

Alias safety is separate from alias matching. Matching `怎么离开会议` to Leave is desirable for understanding the user, but it must not imply the action is safe to click. Every matcher improvement should keep passing through the existing `can_operate` gate.

Running interrupt semantics are step-boundary semantics. A queued question does not interrupt audio or action mid-step; it runs before the next flow step. This is a good trust slice, but future UX text and manual acceptance should avoid promising immediate cancellation.

The old `interrupting` status can be semantically ambiguous. Cycle 001 introduced `queued` and clearer status helpers, but the type still includes legacy `interrupting`. Future controller view-model work should decide whether that status still has a real product meaning.

Thread tests need careful release events. The queue behavior was tested with fake runners and events. This is appropriate, but future tests should keep timeouts small, release background threads reliably, and assert no stop request was sent.

## Habits To Keep

Start each cycle with one explicit theme, one coordination document, and a small set of write scopes. The "not multiple implementation agents on shared controller files" rule should become a default when a cycle centers on a hot module.

Use spec -> plan -> implementation handoff -> review/retro as the standard loop. The plan should include expected RED failures, expected GREEN commands, and exact files. The handoff should record what actually happened, including unexpected cleanup tests.

Prefer existing runtime primitives before adding orchestration state. Cycle 001 succeeded because the design found `DemoControl` and `MaterialDemoRuntime` already had most of the needed behavior.

For multilingual features, require real-language positive tests and encoding-corruption negative tests. Treat terminal mojibake as a process smell, not as product input.

Keep safety as a post-match invariant. Search, alias, and future semantic matchers should identify intent; a separate safety layer decides whether automation is allowed.

Make manual acceptance follow the exact live-demo path. The runbook additions for queued Chat, Chinese Chat, and Chinese Leave are small but valuable because they match the user-visible trust questions.

## Cycle 002 Candidates

1. RingCentral knowledge package hardening.

   Recommended next. Cycle 001 improved how existing package knowledge is consumed, but Cycle 000 still found the package itself needs source index, observation log, locator matrix, state matrix, privacy matrix, acceptance-run history, evidence/version metadata, and locator confidence. This should come before broad feature expansion so new RingCentral observations do not become one-off YAML guesses.

2. Performance telemetry.

   Add timing spans around launch/bind, scan, capture, narration, TTS, audio playback, action execution, cleanup, controller refresh, and queued-interrupt latency. Start with injected clocks and low-noise debug output. This gives later optimization cycles evidence instead of intuition.

3. Controller UI view-model.

   Extract a pure view-model for current target, flow, voice, provider readiness, scan freshness, question outcome, safety disposition, and recovery hints. This should precede any large Tk redesign and should also clarify whether legacy statuses such as `interrupting` remain useful.

## Next Subagent Prompt Reminders

- State that agents are sharing a dirty worktree and must not revert or overwrite others' changes.
- Give each subagent an explicit read scope and write scope; for shared files, assign a single implementation owner.
- Ask implementers to record RED/GREEN TDD evidence, exact verification commands, and any unexpected regression tests they added.
- For Chinese or other non-ASCII work, remind agents to preserve UTF-8, avoid copying mojibake from terminal output, and add negative tests for corrupted input if relevant.
- For matcher work, require alias priority rules and separate safety assertions for every risky matched control.
- For live-interruption work, clarify that current semantics are queued at the next safe step, not mid-action cancellation.
- For RingCentral package work, require evidence fields or companion docs for observed app version, locale, DPI/display scale, scenario, locator confidence, cleanup behavior, and privacy/safety classification.
- For performance work, require injected clocks or deterministic timing seams before wall-clock assertions.
- For controller UI work, prefer pure helper/view-model tests before widget-level changes.

