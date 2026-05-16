# Cycle 024 Demand Analysis: Adaptive Invite Localized Narration

Date: 2026-05-16
Scope: Review only; no code changes.

## Product Risk

Chinese RingCentral demos can say the wrong thing after the runtime correctly changes the action.
For an active multi-person meeting, `adjust_ringcentral_demo_step()` rewrites the empty-room
`Add coworkers` action to the toolbar `Invite` action and replaces English `narration.text`.
However, it preserves `narration.localized_text`. `render_narration_text()` prefers
`localized_text["zh"]` over `text`, so the Chinese presenter can still describe the original
empty-room Add coworkers callout while the product is clicking toolbar Invite.

User-facing impact: in a live localized demo, the presenter may tell Chinese users they are seeing
the fastest empty-room path for bringing people in, even though the UI is in an active meeting and
the correct control is Invite. This weakens trust in synchronized narration, especially because the
flow is about participant controls and meeting state.

## Evidence

- `src/ai_presenter/runtime/adaptive_demo.py` rewrites `ringcentral.video.main.add-coworkers` to
  `ringcentral.video.toolbar.invite` when `participant_count >= 2`, and rewrites only
  `narration.text`.
- `src/ai_presenter/runtime/voice.py` returns nonblank `narration.localized_text[language]` before
  falling back to `narration.text`.
- `tests/unit/test_adaptive_demo.py` currently asserts only the rewritten English text and action;
  it does not cover localized narration.
- `packages/ringcentral-video.yaml` documents `main.add-coworkers` as empty-room-only and
  `toolbar.invite` as the active-room invite path.
- `meeting-control-map-demo` step `control-map-add-coworkers` has `localizedText.zh` that describes
  the empty-room Add coworkers path, making it stale after the adaptive rewrite.

## Recommended Cycle 024 Slice

Fix only the adaptive narration/localization mismatch for the RingCentral Invite rewrite.

Acceptance criteria:

- For active meetings with `participant_count >= 2`, an Add coworkers step with existing
  `localizedText.zh` must not render the stale empty-room Chinese narration after being rewritten
  to toolbar Invite.
- Toolbar Invite steps in active meetings should use the same active-meeting Invite narration in
  English and Chinese behavior.
- Existing inactive/empty-room behavior remains unchanged when `state is None`,
  `participant_count is None`, or `participant_count < 2`.
- The implementation should stay localized to adaptive narration behavior; no package schema,
  route, controller, CLI, or YAML copy expansion is needed.

Suggested tests:

- Add a unit test in `tests/unit/test_adaptive_demo.py` where an Add coworkers step includes
  stale `localized_text={"zh": ...empty-room...}` and `MeetingState(participant_count=2)`.
  Assert the adjusted step no longer contains that stale `zh` text, or contains an explicit
  active-meeting Chinese Invite override if the implementation chooses to provide one.
- Add a rendering-level assertion using `render_narration_text()` with
  `PresenterVoiceSettings(language="zh")` so the test proves the spoken Chinese output is not the
  stale package text.
- Keep the existing English rewrite assertions for Add coworkers and toolbar Invite.

Out of scope:

- Do not localize the remaining long `meeting-controls-tour` flow.
- Do not rewrite RingCentral YAML narration for this issue unless the chosen fix needs a single
  constant copied into tests.
- Do not change general voice fallback semantics; package-authored localized text should continue
  to win for normal, non-adaptive steps.
- Do not broaden adaptive behavior beyond the Add coworkers / Invite meeting-state path.

## Verification Recommendation

Focused verification should be enough:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q `
  tests\unit\test_adaptive_demo.py `
  tests\unit\test_voice.py
```
