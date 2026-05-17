# Cycle 180 Test Review

Date: 2026-05-17

## Findings

1. **P2 - Panel-word exemption could make roster-disclosure prompts operable.**
   `_match_participant_privacy_qa()` initially returned `None` as soon as a prompt contained a panel/button term. That let prompts such as `show participants panel names` and `show who is in participants panel` fall through to the Participants entrypoint with `can_operate=True` and an interrupt.

2. **P2 - `controls` was documented as a safe location qualifier but not implemented.**
   The implementation only treats panel/button wording as explicit safe navigation. The Cycle 180 docs now align to that policy; controls wording remains future work.

3. **P3 - Some identity variants were under-matched to the intended privacy answer.**
   Variants such as `who joined the meeting?` and `which participants are here?` were non-operable but had inconsistent answer families.

4. **P3 - `.coverage` remains dirty.**
   Keep it unstaged.

## Fixes Applied

- Added identity-priority handling for panel-plus-disclosure prompts.
- Added `who is in`, `which participants`, and `who joined the meeting` to participant privacy matching.
- Added tests for `Show participants panel names`, `Show who is in participants panel`, `Which participants are here?`, `Who joined the meeting?`, and `Please be brief and who joined the meeting?`.
- Updated Cycle 180 docs to remove `controls` from the implemented safe qualifier list.

## Residual Risks

- Localized participant identity prompts remain intentionally sparse; do not broaden aliases before adding localized privacy sentinels.
- Existing host identity prompts can route to Meeting information privacy Q&A with a non-operable entrypoint. Confirm product intent before requiring `entrypoint_id=None` for every host-status phrase.
- No live RingCentral acceptance was run; this review is unit and routing-probe only.

## Verification

Focused participant/controller/session slice after fixes:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -B -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests\unit\test_questions.py::test_ringcentral_participant_identity_requests_stay_answer_only tests\unit\test_questions.py::test_participants_panel_location_requests_stay_operable_with_meta tests\unit\test_controller.py::test_presenter_controller_starts_safe_mixed_meta_question_demo_when_idle tests\unit\test_controller.py::test_presenter_controller_keeps_sensitive_mixed_meta_question_text_only_when_idle tests\unit\test_controller_session.py::test_session_creates_interrupt_for_safe_mixed_presenter_meta_answer tests\unit\test_controller_session.py::test_session_does_not_create_interrupt_for_sensitive_mixed_presenter_meta_answer
```

Result: `38 passed`.

Broader participant slice:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -B -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests\unit\test_questions.py tests\unit\test_controller_session.py tests\unit\test_controller.py -k "participant or participants or host_controls or safe_mixed_meta or sensitive_mixed_meta"
```

Result after review fixes: `59 passed, 451 deselected`.
