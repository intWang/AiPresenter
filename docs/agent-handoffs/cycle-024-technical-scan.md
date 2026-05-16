# Cycle 024 Technical Scan: Adaptive Invite Localized Narration

Date: 2026-05-16
Scope: Review only; no production code changes.

## Finding

Confirmed bug risk. `adjust_ringcentral_demo_step()` updates active-meeting invite steps by changing
`narration.text`, but it leaves `narration.localized_text` untouched. `_apply_voice_to_adjusted_step()`
then calls `render_narration_text()`, and that function prefers `localized_text[settings.language]`
over `text`. For Chinese voice settings, a stale package `localizedText.zh` can therefore override
the adaptive English text.

Concrete path:

- `src/ai_presenter/runtime/adaptive_demo.py:14` rewrites `main.add-coworkers` to
  `toolbar.invite` when `participant_count >= 2`.
- `src/ai_presenter/runtime/adaptive_demo.py:20` and `:29` update only `narration.text`.
- `src/ai_presenter/runtime/factory.py:307` applies voice after the state adjuster.
- `src/ai_presenter/runtime/voice.py:159` returns nonblank `narration.localized_text[language]`
  before falling back to `narration.text`.
- `packages/ringcentral-video.yaml:870` has `control-map-add-coworkers` with `localizedText.zh`
  describing the empty-room Add coworkers path.

## Smallest Correct Fix

Prefer providing localized adaptive narration, not merely clearing `localized_text`.

Clearing `localized_text` would stop the stale Chinese sentence, but Chinese rendering would fall
back to `_render_chinese()` over the English adaptive string, which only performs small keyword
replacement and would mostly speak English. The current product supports `PresenterLanguage =
Literal["en", "zh"]`, so the smallest user-correct fix is to add a Chinese active-meeting invite
constant and update both fields together:

```python
_ACTIVE_MEETING_INVITE_LOCALIZED_NARRATION = {
    "zh": "因为已经有人在会议中，Invite 用来继续添加参会人，或复制会议详情，而不会改变当前对话。"
}
```

Then, in both adaptive branches, copy narration with:

```python
update={
    "text": _ACTIVE_MEETING_INVITE_NARRATION,
    "localized_text": dict(_ACTIVE_MEETING_INVITE_LOCALIZED_NARRATION),
}
```

Use the Pydantic field name `localized_text` in `model_copy(update=...)`, not the alias
`localizedText`. This matches existing code using `entrypoint_id` and avoids alias/update ambiguity.
Use a fresh `dict(...)` so adjusted steps do not share a mutable localized-text mapping.

## TDD Tests To Add

Add RED tests before the fix:

1. `tests/unit/test_adaptive_demo.py`
   - Create an Add coworkers step with `localizedText={"zh": "stale empty-room Chinese..."}`,
     `placement="during"`, and `actionOffsetMs=350`.
   - Adjust with `MeetingState(participant_count=2)`.
   - Assert action becomes `ringcentral.video.toolbar.invite`.
   - Assert `adjusted.narration.localized_text["zh"]` is active-meeting Invite narration and does
     not equal/contain the stale empty-room text.
   - Assert `placement == "during"` and `action_offset_ms == 350` are preserved.

2. `tests/unit/test_adaptive_demo.py` or `tests/unit/test_runtime_factory.py`
   - Render the adjusted step through `render_narration_text(adjusted.narration,
     PresenterVoiceSettings(language="zh"))`.
   - Assert the rendered text is the active-meeting Chinese Invite narration, proving the spoken
     output no longer prefers stale package localization.

3. `tests/unit/test_adaptive_demo.py`
   - Repeat for an original `ringcentral.video.toolbar.invite` step with stale
     `localizedText.zh`; assert the active-meeting localized narration is applied while placement
     and `actionOffsetMs` remain unchanged.

Optional integration-level regression:

- Extend `tests/unit/test_runtime_factory.py::test_run_material_demo_captures_state_before_steps_and_rewrites_empty_room_invite`
  so the fixture narration has `localizedText.zh`, runs with
  `PresenterVoiceSettings(language="zh")`, and the fake timeline captures the final spoken text.

## Risks And Notes

- `DemoStepNarration.localized_text` uses alias `localizedText`, with `populate_by_name=True`.
  Runtime `model_copy(update=...)` should use internal field names, because updates are not YAML
  input parsing.
- `localized_text` is mutable, so do not attach a module-level dict object directly to many copied
  step models.
- Preserve `placement` and `action_offset_ms`; existing tests already check this for one branch,
  but the localized regression should keep checking it.
- Do not change `render_narration_text()` precedence. Package-authored localized text should still
  win for normal non-adaptive narration.
- Avoid broad YAML changes. The bug is runtime state adaptation, not package copy quality.
- Current language support is `en`/`zh`; if more languages are added later, preserving old localized
  strings for a semantically rewritten step could reintroduce the same class of bug.

## Verification

Current focused baseline passes, but it does not cover the localized adaptive path:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q `
  tests\unit\test_adaptive_demo.py `
  tests\unit\test_voice.py `
  tests\unit\test_runtime_factory.py
```

Result observed during scan: `44 passed in 7.39s`.

Also run after the fix:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_adaptive_demo.py tests\unit\test_voice.py tests\unit\test_runtime_factory.py
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q
```
