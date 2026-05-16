# Cycle 072 Demand Analysis: JA Raise Hand Narration

Date: 2026-05-16

## Recommendation

Proceed with a narrow Japanese narration slice for `meeting-controls-tour` -> `explain-raise-hand`.

This is the next missing Japanese controls-tour step after Cycle 071. Keep it isolated from reactions, More, recording, notes, settings, live validation, locator confidence work, and any broad confirmed-action workflow. The product requirement is to explain Raise hand as a persistent meeting-visible attention signal, distinct from quick reactions, while making the safety boundary explicit: AiPresenter must not raise or lower a hand automatically unless the user has confirmed a demo or action, and any confirmed demonstration must end with the hand lowered.

## Current Gap

- Japanese demo narration: `22/51`.
- `meeting-controls-tour`: `15/22`.
- First missing controls-tour step: `explain-raise-hand`.
- Remaining missing controls-tour steps: `explain-raise-hand`, `explain-more`, `explain-recording`, `explain-notes`, `explain-background-settings`, `explain-settings`, and `explain-leave`.
- Japanese Q&A remains complete at `12/12` questions and `12/12` answers.
- Japanese aliases remain unchanged at `3/27` entrypoints and `9` aliases.
- The source `explain-raise-hand` step currently has English narration and Chinese `localizedText.zh`, but no `localizedText.ja`.
- The existing step uses `entrypointId: ringcentral.video.toolbar.raise-hand`, `operation: toggle`, `placement: during`, and `actionOffsetMs: 350`.
- The existing raise-hand entrypoint is a toggle route with cleanup expectations: the hand indicator can remain visible if not lowered, and the route notes say to click again to lower the hand after demonstrating it.
- Existing Japanese safety Q&A already explains that reactions and raise hand are meeting-visible signals, but the scripted Japanese tour still lacks point-of-use narration for the Raise hand toolbar step.

## Product And User Need

Japanese presenters need the controls tour to continue from Reactions into Raise hand without blending the two controls. Reactions are short-lived feedback choices from a reaction strip. Raise hand is different: it is a persistent attention signal that remains visible in the meeting until lowered. In a moderated conversation, that persistence is useful because the user can request attention without interrupting the current speaker, but it also creates a clearer cleanup obligation than a passive explanation.

The localized narration should therefore do four jobs:

- Explain that Raise hand is for requesting attention or a speaking turn without talking over someone.
- Identify it as a meeting-visible signal, not a private note or local-only indicator.
- Make clear that AiPresenter does not raise or lower the hand unless the user has explicitly confirmed the action or demo.
- State that after any confirmed demonstration, AiPresenter lowers the hand again so the meeting is not left with a stale attention signal.

## Recommended Scope

Owned future implementation scope:

- Add `localizedText.ja` under `packages/ringcentral-video.yaml` -> `meeting-controls-tour` -> `explain-raise-hand` -> `narration`.
- Preserve the existing `entrypointId`, `operation: toggle`, `placement: during`, and `actionOffsetMs: 350`.
- Keep the wording focused on Raise hand only.
- Describe Raise hand as a persistent meeting-visible attention signal used for moderated discussion or requesting a speaking turn.
- Distinguish Raise hand from reactions: do not call it lightweight feedback, an emoji reaction, or a reaction-strip option.
- Include the no-automatic-action boundary: AiPresenter should not raise or lower the hand unless the user explicitly confirms the action or the demo.
- Include cleanup intent: after any confirmed demonstration, lower the hand again.
- Update only the focused Japanese localization expectations, any focused unit test for this step, and source-index wording needed to reflect the new coverage state in the implementation cycle.

This Cycle 072 handoff itself is documentation-only and should not modify YAML, tests, runtime code, git state, or existing Cycle 071 artifacts.

## Strict Non-Goals

- Do not localize `explain-more` or later steps in the same slice.
- Do not change the neighboring `explain-reactions` step or reaction behavior.
- Do not merge raise-hand behavior with reactions; Raise hand is a persistent toggle with a cleanup requirement.
- Do not add or change Q&A, aliases, diagnostics behavior, CLI implementation, route matching, locators, runtime execution, state extraction, or live acceptance evidence.
- Do not add a new automatic live-meeting raise-hand workflow.
- Do not imply AiPresenter may raise a hand, lower a hand, or leave a hand raised without explicit user confirmation.
- Do not claim Raise hand is private, invisible, temporary, automatically self-clearing, or safe to use without confirmation.
- Do not broaden the slice into recording, notes, settings, background, leave/end, screenshots, live meeting validation, or a general confirmed-action policy.
- Do not change English or Chinese narration unless a separate review scopes that work.

## Acceptance Criteria

- Japanese demo narration advances from `22/51` to `23/51`.
- `meeting-controls-tour` advances from `15/22` to `16/22`.
- First missing controls-tour step advances from `explain-raise-hand` to `explain-more`.
- `explain-raise-hand` keeps `operation: toggle` on `ringcentral.video.toolbar.raise-hand`.
- Japanese `localizedText.ja` exists, is authored Japanese text, and does not fall back to English or Chinese.
- Japanese text explains Raise hand as a way to request attention or a speaking turn without interrupting the current speaker.
- Japanese text treats Raise hand as a persistent meeting-visible signal, not as a reaction or private note.
- Japanese text says AiPresenter does not raise or lower the hand unless the user explicitly confirms the action or demo.
- Japanese text says the hand is lowered after any confirmed demonstration.
- Japanese Q&A and alias counts remain unchanged.
- Japanese `--require-complete` remains incomplete because later controls-tour steps are still missing.

## Next Candidate

After this, `explain-more` should receive its own demand and risk review. It is the expansion menu for deeper meeting tools and should stay separate from Raise hand because its downstream entries include higher-risk surfaces such as recording, notes, background, settings, and leave/end behavior.
