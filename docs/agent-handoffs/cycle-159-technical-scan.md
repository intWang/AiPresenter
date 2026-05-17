# Cycle 159 Technical Scan: Screen Share and Shared Content Prompts

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`

## Recommendation

Keep the six English screen-share prompts as exact Q&A prompts on the existing screen sharing safety Q&A item:

- `Share my screen`
- `Start sharing`
- `Stop sharing`
- `Read the shared screen`
- `Can you describe what's on screen?`
- `Show my screen`

These are action/content-shaped meeting prompts, not neutral control-location aliases. Q&A is the right home because the answer must explain the privacy and meeting-state boundary, remain `can_operate=False`, and avoid queuing a question interrupt. Do not add these as `questionAliases` on `ringcentral.video.toolbar.share`; aliases should stay for control discovery such as Share button location or screen-share selector wording.

## Current Routing

`src/ai_presenter/runtime/questions.py` has the desired precedence:

- `answer_question()` normalizes the prompt.
- `_match_qa()` checks exact Q&A prompts through `package.qa_questions_by_normalized` before entrypoint aliases or scored entrypoint matching.
- The matched Q&A returns `related_entrypoint_ids[0]`, so these prompts still identify `ringcentral.video.toolbar.share`.
- `_can_operate()` returns false because the share entrypoint text contains risky terms such as `share` and `start`.
- `create_question_interrupt_step()` returns `None` when `response.can_operate` is false.

Observed current-tree routing:

```text
'Share my screen' -> ringcentral.video.toolbar.share, can_operate=False, interrupt=False, Q&A safety answer
'Start sharing' -> ringcentral.video.toolbar.share, can_operate=False, interrupt=False, Q&A safety answer
'Stop sharing' -> ringcentral.video.toolbar.share, can_operate=False, interrupt=False, Q&A safety answer
'Read the shared screen' -> ringcentral.video.toolbar.share, can_operate=False, interrupt=False, Q&A safety answer
"Can you describe what's on screen?" -> ringcentral.video.toolbar.share, can_operate=False, interrupt=False, Q&A safety answer
'Show my screen' -> ringcentral.video.toolbar.share, can_operate=False, interrupt=False, Q&A safety answer
```

The important regression this prevents is `Start sharing` falling through to `ringcentral.develop.video.start` and producing `Start meeting:` entrypoint text. The current exact Q&A index prevents that.

## Current Package State

`packages/ringcentral-video.yaml` already has the right content shape:

- `How should AiPresenter handle screen sharing safely?`
  - Related entrypoint: `ringcentral.video.toolbar.share`
  - English localized prompts: the six exact prompts above
  - Answer starts with `Screen sharing can expose private content...`
- `Can the presenter describe shared-screen content?`
  - Still covers broader shared-content safety in localized prompts.

Current loaded package counts:

```text
operation entrypoints: 27
Q&A items: 14
Q&A question prompts/index entries: 119
package-owned aliases: 157
aliases by language: en=5, es=69, ja=34, zh=49
entrypoints with aliases by language: en=2, es=26, ja=13, zh=15
```

The package-level alias count should not change for this work.

## Files To Update

No runtime source change appears necessary for this screen-share slice.

Already aligned:

- `packages/ringcentral-video.yaml`
  - Contains the screen-share safety Q&A item and six exact English prompts.
- `tests/unit/test_questions.py`
  - `test_ringcentral_english_screen_sharing_questions_stay_qa_first` covers all six prompts and verifies:
    - entrypoint is `ringcentral.video.toolbar.share`
    - `can_operate is False`
    - answer contains `Screen sharing can expose private content`
    - answer does not contain `Screen sharing:` or `Start meeting:`
    - no question interrupt is created

Still stale and should be updated in the implementation cycle:

- `tests/unit/test_diagnostics.py`
  - Change `109 Q&A question prompts...` expectations to `119 Q&A question prompts...`.
- `tests/unit/test_cli.py`
  - Change doctor output expectations from `109 Q&A question prompts...` to `119 Q&A question prompts...`.
- `docs/knowledge/ringcentral-video/runtime-safety-routing.md`
  - Its inventory still says `Q&A items: 12` and `Q&A question prompts: 84`; refresh to the current inventory if this doc is part of the cycle scope.

## Test Evidence

Passing:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py::test_ringcentral_english_screen_sharing_questions_stay_qa_first
```

Observed:

```text
6 passed
```

Failing because count assertions are stale:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_questions_ok_for_ringcentral_package tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_alias_overlap_ok_for_ringcentral_package tests\unit\test_cli.py::test_doctor_loads_profile_package_and_flow
```

Observed:

```text
3 failed
expected 109 Q&A question prompts; actual 119 Q&A question prompts
```

Doctor confirms the current runtime counts:

```powershell
.\.venv\Scripts\ai-presenter doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo
```

Key observed lines:

```text
[OK] question aliases: 157 package-owned aliases have no cross-entrypoint duplicates
[OK] qa questions: 119 Q&A question prompts have no cross-item duplicates
[OK] qa alias overlap: 119 Q&A question prompts have no unsafe package-owned alias overlaps
[INFO] qa alias substring risk: 11 Q&A question prompts contain package-owned alias substrings outside related entrypoints
Doctor completed: 11 ok, 1 info, 0 warnings, 0 failed.
```

## Focused Commands

Use these after updating only the stale count assertions and any scoped inventory doc:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py::test_ringcentral_english_screen_sharing_questions_stay_qa_first
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_questions_ok_for_ringcentral_package tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_alias_overlap_ok_for_ringcentral_package
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_cli.py::test_doctor_loads_profile_package_and_flow
.\.venv\Scripts\ai-presenter doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo
git diff --check -- packages\ringcentral-video.yaml tests\unit\test_questions.py tests\unit\test_diagnostics.py tests\unit\test_cli.py docs\knowledge\ringcentral-video\runtime-safety-routing.md docs\agent-handoffs\cycle-159-technical-scan.md
```

## No-Go Scope

- Do not add these six prompts as English `questionAliases` on `ringcentral.video.toolbar.share`.
- Do not make screen sharing operable from Q&A.
- Do not add or change `openSteps`.
- Do not click the final Share button or queue the Share route from these prompts.
- Do not describe, read, infer, or summarize shared-screen content unless an approved observation source has captured it and the user allows it.
- Do not combine this with recording, leave/end, reactions, notes/transcript, chat, participants, microphone, background, or live acceptance work.
