# Adaptive Invite Localized Narration Design

Date: 2026-05-16
Cycle: 024

## Goal

Fix RingCentral adaptive invite narration so Chinese demos do not speak stale empty-room localized text after the runtime rewrites an active-meeting Add coworkers step to toolbar Invite.

## Root Cause

`adjust_ringcentral_demo_step()` rewrites active-meeting invite behavior by changing `narration.text`, but it preserves `narration.localized_text`. Later, `render_narration_text()` prefers `localized_text[settings.language]` over `text`. For Chinese, that means an adjusted step can click or explain toolbar Invite while still speaking package-authored Chinese text about empty-room Add coworkers.

## Scope

In scope:

- Add active-meeting Chinese invite narration to adaptive demo behavior.
- Apply the English and Chinese adaptive narration together for:
  - `ringcentral.video.main.add-coworkers` when `participant_count >= 2`.
  - `ringcentral.video.toolbar.invite` when `participant_count >= 2`.
- Preserve placement and `actionOffsetMs`.
- Add focused tests proving Chinese render output no longer uses stale package localization.

Out of scope:

- Package YAML narration expansion.
- General `render_narration_text()` precedence changes.
- Runtime factory, sync, CLI, controller, route, schema, and provider changes.
- Long-flow `meeting-controls-tour` localization.

## Design

Add a module-level Chinese adaptive narration constant alongside the existing English active-meeting invite narration. When adaptive logic rewrites a step, update both `text` and `localized_text` on the copied narration. Use the model field name `localized_text`, not the YAML alias `localizedText`, inside `model_copy(update=...)`.

The Chinese adaptive sentence should keep the visible `Invite` label and explain the active-meeting behavior:

`因为已经有人在会议中，Invite 用来继续添加参会人，或复制会议详情，而不会改变当前对话。`

Use `dict(_ACTIVE_MEETING_INVITE_LOCALIZED_NARRATION)` when copying into a step so adjusted step models do not share a mutable mapping.

## Acceptance Criteria

- Existing English adaptive tests still pass.
- Add coworkers with stale Chinese `localizedText.zh` adjusts to toolbar Invite and renders the active-meeting Chinese Invite sentence.
- Toolbar Invite with stale Chinese `localizedText.zh` renders the same active-meeting Chinese Invite sentence.
- Stale empty-room Chinese strings are not present in adjusted localized narration or rendered Chinese output.
- `placement` and `actionOffsetMs` remain unchanged.
- Non-active states still return the original step object unchanged.

## Risks

- Clearing `localized_text` would avoid stale text but produce mostly-English Chinese fallback. The fix must provide localized adaptive text.
- Using alias `localizedText` in `model_copy(update=...)` can silently miss the Pydantic field. Use `localized_text`.
- This same class of issue can return when more languages are added; Cycle 024 only covers current supported languages.
