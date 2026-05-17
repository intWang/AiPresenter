# Cycle 180 Technical Scan: Participant Intent Boundaries

Date: 2026-05-17
Mode: read-only; no source/YAML/test patch applied by this scan.

## Current Behavior Probes

| Prompt | Current route | Operable? | Interrupt? | Answer shape |
| --- | --- | --- | --- | --- |
| `Please be brief and show participants` | `None` | false | false | Presenter settings meta-answer before this cycle |
| `Please be brief and show participants panel` | `ringcentral.video.toolbar.participants` | true | true | `Participants panel: Open participant list...` |
| `Please be brief and list participants` | `None` | false | false | Participant identity privacy Q&A |
| `Please be brief and who is host` | `ringcentral.video.top.meeting-info` | false | false | Meeting info privacy Q&A |
| `show participants` | `ringcentral.video.toolbar.participants` before this cycle | true | true | Participants panel entrypoint |
| `list participants` | `None` | false | false | Participant identity privacy Q&A |
| `who is host` | `None` | false | false | Participant identity privacy Q&A |

## Why It Behaves This Way

`runtime/questions.py` is Q&A-first: `_answer_question()` checks `_match_qa()` before entrypoints. That keeps `list participants`, participant names, roles, chat content, meeting info, notes, recording, and host-control actions answer-only when they match Q&A safety entries.

Presenter meta prompts like `Please be brief...` switch entrypoint matching to `_match_explicit_entrypoint()`. That path only accepts aliases, meeting-info location, or explicit titles. So English `show participants` without `panel` becomes ambiguous and used to fall back to the presenter-settings answer, while `show participants panel` matches the title.

`create_question_interrupt_step()` only creates an interrupt when `entrypoint_id` is present and `can_operate` is true. Participants has open steps and is not `answerOnly`, so it can interrupt. Privacy Q&A responses with no entrypoint never interrupt.

## Change Assessment

Runtime change is needed if the intended boundary is to give broad `show participants` a participant privacy answer instead of generic Presenter settings. The change should:

- Add a participant-disclosure privacy matcher before contained-QA and entrypoint matching.
- Reuse the existing Chat/Participants privacy Q&A where possible.
- Exempt explicit panel/button location phrases.
- Avoid YAML aliases for broad `show participants`.

No package YAML change is needed for the safe panel route because explicit `participants panel` phrases already match the entrypoint title.

## Test Patterns

Existing patterns to extend:

- `tests/unit/test_questions.py::test_ringcentral_participant_identity_requests_stay_answer_only`
- `tests/unit/test_questions.py::test_participants_panel_location_requests_stay_operable_with_meta`
- `tests/unit/test_controller_session.py::test_session_does_not_create_interrupt_for_sensitive_mixed_presenter_meta_answer`
- `tests/unit/test_controller.py` mixed safe/sensitive controller matrices

For new cases, assert `entrypoint_id`, `can_operate`, interrupt presence, and an answer-text snippet excluding the wrong family.

## Risks

- If `show participants` becomes an alias, identity prompts may become operable.
- If privacy Q&A gains a related entrypoint, `can_operate` must still remain false or no interrupt.
- Chinese `列出参会者` may need a separate localized privacy pass; do not broaden CJK semantics in this cycle without dedicated tests.
