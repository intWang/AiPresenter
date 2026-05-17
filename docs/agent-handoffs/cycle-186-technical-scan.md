# Cycle 186 Technical Scan: Controller Outcome Ordering

Date: 2026-05-17

## Current Source Shape

`PresenterController.submit_question()` already carries `response.answer_source` into every `QuestionSubmitResult`.

`describe_question_result()` is the UI/status formatter used by the controller after question submission.

`controller_view_model._question_label(...)` displays `last_question_outcome` directly, so privacy-safe wording must be produced before the view model receives it.

## Finding

The old `describe_question_result()` order checked non-operable `entrypoint_id` before `answer_source == "qa"`. That meant Q&A guidance tied to an answer-only entrypoint, such as meeting information or notes/transcript privacy guidance, was displayed as:

```text
Answered only: ringcentral.video.top.meeting-info is not safe to operate automatically
```

The desired parity outcome is:

```text
Answered only: matched text guidance; no demo was started
```

## Implementation Surface

- Reorder `describe_question_result()` after queued/started outcomes:
  - `presenter_meta`
  - `qa`
  - `no_match`
  - non-operable `entrypoint`
- Add `describe_question_error(...)` for generic exception status wording.
- Use the generic error helper in the question-submit exception path.

## Test Targets

- `tests/unit/test_controller.py`
- `tests/unit/test_controller_view_model.py`

## Risks

- Keep non-operable entrypoint coverage on a true `answer_source="entrypoint"` prompt such as `invite people`; `leave meeting` currently routes through Q&A.
- Do not leak exception text into status or summary rows.
- Keep raw answer text confined to the chat transcript path.
