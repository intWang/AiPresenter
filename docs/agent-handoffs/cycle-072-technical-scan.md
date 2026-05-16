# Cycle 072 Technical Scan: meeting-controls-tour / explain-raise-hand JA narration

Date: 2026-05-16

## Scope

Add Japanese `localizedText.ja` for:

- Package: `packages/ringcentral-video.yaml`
- Flow: `meeting-controls-tour`
- Step: `explain-raise-hand`
- Entrypoint: `ringcentral.video.toolbar.raise-hand`
- Operation: `toggle`

This is a narrow localization slice. Do not edit runtime behavior, locators, aliases, Q&A, diagnostics implementation, CLI implementation, flow order, or adjacent narration. Preserve the existing toggle semantics and cleanup expectations.

Current repository state already has `explain-reactions` localized and expects the next missing Japanese controls-tour step to be `explain-raise-hand`:

```text
- meeting-controls-tour: 15/22 narration localized
  missing: explain-raise-hand, explain-more, explain-recording, explain-notes, explain-background-settings, explain-settings, explain-leave
Localization report: 22/51 demo steps, 12/12 Q&A questions, 12/12 Q&A answers localized for ja.
```

## Exact Source Step

From `packages/ringcentral-video.yaml`, `meeting-controls-tour` currently has English and Chinese narration only for `explain-raise-hand`:

```yaml
  - id: explain-raise-hand
    title: Raise hand
    action:
      entrypointId: ringcentral.video.toolbar.raise-hand
      operation: toggle
    narration:
      text: Raise hand signals that you want attention without speaking over someone. It is a toggle, so I lower
        the hand again after showing it.
      localizedText:
        zh: Raise hand 表示你想获得发言机会，而不用打断别人。它是开关，所以展示后会再把手放下。
      placement: during
      actionOffsetMs: 350
```

Related entrypoint details:

```yaml
- id: ringcentral.video.toolbar.raise-hand
  title: Raise hand
  area: Meeting toolbar
  purpose: Raise or lower hand to request attention.
  openSteps:
  - action: clickWindowControl
    target: Raise hand
    match:
      alternateTargets: onconf.reactions.REMOVE_RAISE_HAND
      controlType: button
      cleanup: toggle
  presenterNotes:
  - Use this in moderated meeting demos.
  - The button toggles state; when active, a hand indicator appears and the toolbar button changes emphasis.
  - Click again to lower the hand after demonstrating it.
```

Related source-index wording:

```yaml
  raiseHand:
    shortScript: Raise hand signals that the participant wants attention without speaking over the meeting.
    details:
    - Explain both raise and lower states because the same control toggles.
    - Use it as the safer alternative to interrupting with audio.
    relatedEntrypointIds:
    - ringcentral.video.toolbar.raise-hand
```

Important source semantics:

- The step operation is `toggle`, not `open`, `explain`, or a reaction send.
- The route clicks `Raise hand`, can match `onconf.reactions.REMOVE_RAISE_HAND` when already active, and uses `cleanup: toggle`.
- The narration must explain both raised and lowered states because the same control toggles.
- Raise hand is a persistent meeting-visible attention signal, not an emoji reaction, private note, or local-only marker.
- Any confirmed demonstration must end with the hand lowered; do not imply AiPresenter may raise, lower, or leave a hand raised without explicit user confirmation.

## Recommended Japanese Text

```yaml
        ja: Raise hand は、ほかの人の発話を遮らずに注目してほしいことや発言機会を求めていることを知らせるトグル操作です。押すと手を上げた状態になり、もう一度押すと手を下げます。会議中に見えるシグナルなので、ユーザーの明確な指示なしに手を上げたり、上げたままにしたりしません。実演した場合は、説明後に手を下げます。
```

Rationale:

- Preserves `Raise hand`, attention/speaking-turn intent, and the "without speaking over someone" meaning.
- Explicitly says the control is a toggle with raise and lower states.
- Treats the raised hand as a meeting-visible signal, not a private or local-only state.
- Keeps user control explicit: no raise, lower, or left-raised state without clear user instruction.
- Carries the source cleanup obligation: after a demonstration, lower the hand again.
- Keeps this separate from Reactions; no emoji, quick feedback, reaction strip, `Escape`, or send-reaction language.

## Expected Count Changes

After adding only the Japanese narration for `explain-raise-hand`:

- Japanese demo narration: `22/51` -> `23/51`
- `meeting-controls-tour.localized_steps`: `15/22` -> `16/22`
- First missing `meeting-controls-tour` step: `explain-raise-hand` -> `explain-more`
- Remaining missing `meeting-controls-tour` steps: `explain-more`, `explain-recording`, `explain-notes`, `explain-background-settings`, `explain-settings`, `explain-leave`
- Japanese Q&A remains `12/12` questions and `12/12` answers.
- Japanese aliases remain `3/27` entrypoints and `9` aliases.
- Japanese `--require-complete` remains intentionally incomplete and should still exit `1`.
- `meeting-control-map-demo` remains `0/22`; do not use this slice to localize control-map narration.

## TDD Test Updates

Recommended red-first test work:

- `tests/unit/test_material_packages.py`
  - Update `test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage`:
    - `report.demo_localized_steps`: `22` -> `23`
    - `report.flow_by_id["meeting-controls-tour"].localized_steps`: `15` -> `16`
  - Add `test_meeting_controls_tour_has_japanese_raise_hand_narration`, adjacent to the existing `test_meeting_controls_tour_has_japanese_reactions_narration`.
- `tests/unit/test_cli.py`
  - In both Japanese localization-report tests:
    - `Localization report: 22/51 demo steps` -> `23/51`
    - `- meeting-controls-tour: 15/22 narration localized` -> `16/22`
    - `missing: explain-raise-hand` -> `missing: explain-more`
- `tests/unit/test_diagnostics.py`
  - In `test_diagnostics_require_localization_reports_japanese_qa_complete_but_demo_missing`:
    - diagnostic detail `22/51 demo steps` -> `23/51 demo steps`

Focused material-package test assertions should cover:

- `step.id == "explain-raise-hand"` found from `meeting-controls-tour`
- `step.action.entrypoint_id == "ringcentral.video.toolbar.raise-hand"`
- `step.action.operation == "toggle"`
- `step.narration.placement == "during"`
- `step.narration.action_offset_ms == 350`
- Japanese text exists and `has_cjk(ja_text)` is true
- Includes `Raise hand`, `注目`, `発言機会`, `遮らず`, `トグル`, `手を上げ`, `手を下げ`, `会議中に見える`, `ユーザー`, `明確な指示`, `上げたまま`, `実演`, and `説明後`
- Does not include reaction-specific wording such as `リアクション`, `ハート`, `いいね`, `拍手`, `Be right back`, or `送信しません`

Focused verification command:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage tests\unit\test_material_packages.py::test_meeting_controls_tour_has_japanese_raise_hand_narration tests\unit\test_cli.py::test_localization_report_outputs_japanese_demo_and_qa_coverage tests\unit\test_cli.py::test_localization_report_require_complete_fails_for_japanese_demo_gap tests\unit\test_diagnostics.py::test_diagnostics_require_localization_reports_japanese_qa_complete_but_demo_missing
```

## Expected CLI Output

After implementation, `.\.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language ja` should include:

```text
Demo flows:
- vbg-blur-demo: 4/4 narration localized
- meeting-basics-demo: 3/3 narration localized
- meeting-controls-tour: 16/22 narration localized
  missing: explain-more, explain-recording, explain-notes, explain-background-settings, explain-settings, explain-leave
- meeting-control-map-demo: 0/22 narration localized
  missing: control-map-overview, control-map-meeting-info, control-map-network, control-map-views, control-map-report, control-map-add-coworkers, control-map-participants, control-map-chat, control-map-microphone, control-map-audio-menu, control-map-camera, control-map-camera-menu, control-map-share, control-map-reactions, control-map-raise-hand, control-map-more, control-map-recording, control-map-notes, control-map-background, control-map-settings, control-map-leave, control-map-summary

Q&A:
- localized questions: 12/12
- localized answers: 12/12

Entrypoint aliases:
- questionAliases.ja present on 3/27 entrypoints (9 aliases)

Localization report: 23/51 demo steps, 12/12 Q&A questions, 12/12 Q&A answers localized for ja.
```

`.\.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language ja --require-complete` should still exit `1` and append:

```text
Localization coverage incomplete for ja.
```

The focused diagnostics detail should move to:

```text
[FAIL] localization: required ja localization incomplete: 23/51 demo steps, 12/12 Q&A questions, 12/12 Q&A answers
```

Note: running `doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --language ja --require-localization` in the current profile can also fail the voice check because `ringcentral-video-bind-speaker` uses `windows-sapi-en`; that is separate from the localization-count assertion.

## Guardrails

- Edit only the `localizedText.ja` entry for `meeting-controls-tour` -> `explain-raise-hand` during implementation.
- Preserve `operation: toggle`, `placement: during`, and `actionOffsetMs: 350`.
- Preserve the route's `cleanup: toggle`, alternate target, locators, entrypoint IDs, flow order, aliases, Q&A, runtime behavior, CLI formatting, and diagnostics logic.
- Do not localize `explain-more` or any later controls-tour step in this slice.
- Do not change `explain-reactions`, reaction-strip cleanup, reaction examples, or any send-reaction behavior.
- Do not add live state detection, confirmed-action workflow, acceptance evidence, manual-control changes, or a raise/lower alias.
- Do not leave the wording ambiguous about the hand being lowered after a confirmed demonstration.
