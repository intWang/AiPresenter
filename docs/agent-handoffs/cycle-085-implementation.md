# Cycle 085 Implementation: control-map-participants JA

Date: 2026-05-16

## Scope

Added Japanese narration for `meeting-control-map-demo` step `control-map-participants`.

This cycle intentionally kept the slice narrow:

- no locator changes
- no route or cleanup changes
- no adaptive logic changes
- no Q&A changes
- no alias changes
- no neighboring control-map step localization

## TDD Evidence

Red command:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage tests\unit\test_material_packages.py::test_meeting_control_map_has_japanese_participants_narration tests\unit\test_cli.py::test_localization_report_outputs_japanese_demo_and_qa_coverage tests\unit\test_cli.py::test_localization_report_require_complete_fails_for_japanese_demo_gap tests\unit\test_diagnostics.py::test_diagnostics_require_localization_reports_japanese_qa_complete_but_demo_missing
```

Red result: `5 failed`.

Expected failures:

- JA demo coverage remained `35/51` instead of expected `36/51`.
- `meeting-control-map-demo` remained `6/22` instead of expected `7/22`.
- `control-map-participants` had no `localizedText.ja`.
- CLI and diagnostics still reported `35/51`.

Green command:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage tests\unit\test_material_packages.py::test_meeting_control_map_has_japanese_participants_narration tests\unit\test_cli.py::test_localization_report_outputs_japanese_demo_and_qa_coverage tests\unit\test_cli.py::test_localization_report_require_complete_fails_for_japanese_demo_gap tests\unit\test_diagnostics.py::test_diagnostics_require_localization_reports_japanese_qa_complete_but_demo_missing
```

Green result: `5 passed`.

## Behavior Preserved

The focused guard test preserves the Participants route:

- `entrypointId: ringcentral.video.toolbar.participants`
- `operation: open`
- `placement: during`
- `actionOffsetMs: 350`
- `clickWindowControl`
- target `Participants`
- `controlType: button`
- `cleanup: toggle`

It also verifies existing Japanese aliases remain unchanged and presenter notes still warn about attendee count, meeting control, not identifying participants unless verified and allowed, Participant/Chat tabs, search, invite, lock, mute, raise-hand, more controls, and cleanup before Chat.

## Localization Result

Expected Japanese coverage after this slice:

- overall demo coverage: `36/51`
- `meeting-control-map-demo`: `7/22`
- first remaining missing control-map step: `control-map-chat`
- Q&A coverage unchanged: `12/12` questions and `12/12` answers
- alias coverage unchanged: `3/27` entrypoints and `9` aliases
- `--require-complete` for Japanese still fails because later control-map steps remain untranslated

## Copy Boundary

The Japanese text describes `Participants` as the participant-list and people-controls panel. It explains that attendee count, Invite, lock, mute, raise-hand, and more controls live there, but names and roles are not read unless the user explicitly asks and visible content is verified.

The copy avoids saying AiPresenter searches participants, invites people, locks the meeting, mutes others, changes hand state, identifies attendees, reads names by default, or leaves the Participants panel open before Chat.
