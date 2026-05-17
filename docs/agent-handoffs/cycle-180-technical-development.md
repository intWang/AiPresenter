# Cycle 180 Technical Development: Participants Privacy Boundary

Date: 2026-05-17

## Files Changed

- `src/ai_presenter/runtime/questions.py`
  - Added a participant privacy runtime matcher.
  - Reuses the existing privacy Q&A: `Can the presenter read meeting messages or participant names?`
- `tests/unit/test_questions.py`
  - Expanded participant disclosure prompts to stay answer-only.
  - Added explicit Participants panel location prompts that remain operable.
- `tests/unit/test_controller.py`
  - Added controller coverage for safe Participants panel meta prompts and unsafe broad participant prompts.
- `tests/unit/test_controller_session.py`
  - Added session interrupt coverage for the same safe/unsafe boundary.
- `docs/agent-handoffs/cycle-180-demand-analysis.md`
- `docs/agent-handoffs/cycle-180-risk-scan.md`
- `docs/agent-handoffs/cycle-180-technical-scan.md`

`.coverage` is a local generated test artifact; do not stage it.

No package YAML changes were made.

## Behavior Added

Broad participant disclosure phrasing now resolves to answer-only privacy guidance instead of an operable Participants panel route.

Answer-only prompts include:

- `Show participants`
- `Please be brief and show participants`
- `List participants`
- `Read participant names`
- `Show participant roles`
- `Who is host or moderator?`
- `Who is in the meeting?`

These return the existing chat/participants privacy answer, with:

- `entrypoint_id is None`
- `can_operate is False`
- no question interrupt step
- answer text covering participant names, roles, private tabs, explicit user request, and verified visible context

Combined panel-plus-disclosure prompts such as `Show participants panel names` and `Show who is in participants panel` also remain answer-only. The panel/button exemption only applies when identity terms such as names, roles, who-is, or who-joined are absent.

Explicit panel-location prompts remain operable:

- `Please be brief and show participants panel`
- `Please be brief and open participants panel`
- `Please be brief and where is participants panel`
- Chinese location sentinel `请简洁一点，参会者在哪里`

These still route to `ringcentral.video.toolbar.participants`, keep `can_operate is True`, produce `Participants panel:` answer text, and can create/start/queue a question interrupt.

## Implementation Notes

`_match_qa()` now calls `_match_participant_privacy_qa()` after chat-content privacy matching and before contained Q&A / entrypoint fallback.

The new matcher is intentionally term-based and narrow:

- It returns no match when the normalized question contains explicit panel/button location terms and no identity intent.
- It returns the existing participant privacy Q&A when the question contains disclosure-adjacent terms such as `show participants`, `list participants`, `participant names`, `participant roles`, `who is host`, `host or moderator`, or `who is in the meeting`.

This keeps the runtime boundary outside YAML, avoiding broad package aliases that could make identity/role/host prompts operable.

## Tests To Run

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -B -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests\unit\test_questions.py tests\unit\test_controller_session.py tests\unit\test_controller.py -k "participant or participants or host_controls or safe_mixed_meta or sensitive_mixed_meta"
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -B -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests\unit\test_questions.py tests\unit\test_controller_session.py tests\unit\test_controller.py
```

## Risks

- The runtime matcher is English-focused. Localized participant identity prompts should get a separate privacy pass before broadening localized aliases.
- The location exemption currently covers panel/button terms only. Future `participants controls` wording may need an explicit safe-path decision and tests.
- Adding `show participants` as a YAML alias later would bypass this safety intent and could make disclosure prompts operable.
- Adding `relatedEntrypointIds` to the privacy Q&A could reintroduce interrupt risk unless `can_operate` remains false.
- `.coverage` is modified local output and should be left out of the cycle commit.
