# Cycle 155 Technical Development Handoff

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`

## Objective

Capture the Cycle155 package/test-only RingCentral Video routing increment for
the deferred microphone button location prompt. The implemented slice adds one
exact English package-owned alias so `Where is the microphone button?` routes to
the existing microphone toolbar control instead of the audio-menu entrypoint.

This is deterministic question routing only. It does not change runtime matcher
scoring, media operation policy, live RingCentral behavior, provider output,
speech synthesis, virtual microphone routing, or any source code path.

## Files Changed

- `packages/ringcentral-video.yaml`: added `questionAliases.en` with the exact
  alias `microphone button` under `ringcentral.video.toolbar.audio`.
- `tests/unit/test_questions.py`: added a focused route guard proving
  `Where is the microphone button?` selects
  `ringcentral.video.toolbar.audio`, keeps `can_operate is False`, and creates
  no question interrupt step.
- `tests/unit/test_diagnostics.py`: updated the RingCentral package-owned alias
  diagnostic expectation from 156 to 157.
- `tests/unit/test_cli.py`: updated the doctor output expectation from 156 to
  157 package-owned aliases.
- `docs/agent-handoffs/cycle-155-technical-development.md`: this handoff only.

## TDD Red Evidence

Before the alias addition, the Cycle155 technical scan recorded the current
probe for the covered prompt:

```text
question: Where is the microphone button?
entrypoint: ringcentral.video.toolbar.audio-menu
can_operate: False
interrupt step is None: True
```

The proposed red test expected `ringcentral.video.toolbar.audio`, so the
pre-change failure was:

```text
assert 'ringcentral.video.toolbar.audio-menu' == 'ringcentral.video.toolbar.audio'
```

That red state proves the prompt was being routed to the audio menu instead of
the microphone toolbar button.

## Green Evidence

No-coverage verification passed for the implemented slice:

- Targeted route test: `1 passed`.
- Full question-routing suite: `202 passed`.
- Material package, diagnostics, and doctor count/output selection: `143
  passed`.

The green route assertion now proves:

- `Where is the microphone button?` selects
  `ringcentral.video.toolbar.audio`.
- `can_operate is False` remains preserved.
- `create_question_interrupt_step(package, response) is None`.

## Count Update

RingCentral package-owned alias diagnostics moved from 156 to 157. The increase
is exactly the new English alias `microphone button` under
`ringcentral.video.toolbar.audio`.

Q&A prompt counts did not change; the existing doctor check still expects
`87 Q&A question prompts`.

## Risk Boundaries

- No source, runtime matcher, operation policy, provider, profile, README,
  package schema, or existing handoff behavior is part of this slice.
- No `.coverage` changes are owned by this slice.
- The new alias is location-only. It must not be described as muting,
  unmuting, enabling a microphone, proving audio readiness, choosing a device,
  or changing live meeting state.
- `ringcentral.video.toolbar.audio` remains non-operable from questions because
  media-state controls are stateful and side-effecting.
- Audio-menu device-recovery wording remains separate from toolbar-button
  location wording.
- Unit tests and doctor output are repository-local evidence only; they do not
  prove live RingCentral Video acceptance, current UIA locator reliability,
  device permissions, provider readiness, speech readiness, or virtual
  microphone behavior.

## Recommended Follow-Up

Keep the follow-up narrow: if future cycles add more media-control aliases,
separate toolbar-button location prompts from audio-menu and video-menu
device-selection prompts. Each new media alias should include route,
`can_operate`, and interrupt-step assertions, plus diagnostics/doctor count
updates when package-owned alias inventory changes.

Do not expand this slice into broad aliases such as `microphone`, `mic`,
`audio`, `mute`, `unmute`, `sound`, `camera`, or `video` without a separate
risk scan and neighboring negative-route tests.

## Handoff Verification

Requested hygiene command for this handoff turn:

```powershell
git diff --check -- packages\ringcentral-video.yaml tests\unit\test_questions.py tests\unit\test_diagnostics.py tests\unit\test_cli.py docs\agent-handoffs\cycle-155-technical-development.md
```
