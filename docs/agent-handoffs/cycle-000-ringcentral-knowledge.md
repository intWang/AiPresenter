# Cycle 000 RingCentralVideo Knowledge Package Handoff

## Scope And Sources

This handoff summarizes the current RingCentralVideo knowledge package and proposes the next expansion path. It is based on repository-local sources only:

- `packages/ringcentral-video.yaml`
- `profiles/ringcentral-video*.yaml`
- `src/ai_presenter/profiles/ringcentral-video.yaml`
- `src/ai_presenter/adapters/ringcentral.py`
- `src/ai_presenter/packages/models.py`
- `src/ai_presenter/runtime/package_demo.py`
- `src/ai_presenter/runtime/adaptive_demo.py`
- `src/ai_presenter/runtime/questions.py`
- `docs/runbooks/ringcentral-manual-acceptance.md`
- RingCentral-related specs, plans, and tests under `docs/superpowers/` and `tests/`

I did not run product automation or tests for this handoff. The findings below are a repository knowledge review, not a fresh manual acceptance result.

## Current Package Coverage

The package currently exposes `ringcentral-video` as a material package with five associated profiles:

- `ringcentral-video`: full launch path from `RingCentralDevelop`, fake providers, speaker plus virtual mic output.
- `ringcentral-video-openai`: same launch path, OpenAI narration and speech, fake vision.
- `ringcentral-video-codex-cli-speaker`: same launch path, Codex CLI narration, Windows SAPI speaker output.
- `ringcentral-video-bind-speaker`: bind to an already running meeting window, fake narration, Windows SAPI English speaker output.
- `ringcentral-video-piper-speaker`: bind to an already running meeting window, fake narration, Piper speaker output.

The package has 27 operation entrypoints:

- Launch surface: Video tab in `RingCentralDevelop`, Start meeting.
- Meeting surface: overview, meeting information, network quality, view layout, report issue.
- Main canvas and people: Add coworkers, Invite, Participants, Chat.
- Media readiness: microphone toggle, microphone/speaker menu, camera toggle, camera menu, More video settings.
- Background and appearance: Background settings, Select blur background, More > Background.
- Presentation and interaction: Share, Reactions, Raise hand.
- Advanced/overflow: More, Start recording, Notes and transcript, Settings.
- Closeout: Leave meeting.

The four demo flows are:

- `vbg-blur-demo`: open video settings, open background panel, select blur, verify video.
- `meeting-basics-demo`: microphone, participants, chat.
- `meeting-controls-tour`: English tour from top bar through leave control.
- `meeting-control-map-demo`: bilingual English/Chinese map of status, people, media, interaction, More, and closeout.

The 17 explainers cover launch, overview, meeting info, network quality, view layout, report issue, invite, audio, video, video settings, reactions, raise hand, More, notes, recording, background, settings, participants, sharing, chat, and leave.

The QA section is intentionally small today:

- Protecting the real background.
- Whether the presenter can describe shared-screen content.
- How to bring people into the meeting.

Manual controls are defined as `say`, `skip`, and `focus`. Runtime tests confirm these are consumed by the synchronized timeline runner: `say:` replaces narration, `skip` can skip the next or matching step, and `focus:` skips ahead until a matching step.

## Runtime And Acceptance Coverage

Profiles bind to `process=RingCentralVideo` and `windowClass=RingCentralVideoClass`, observe every second, and use screenshot, Windows UI Automation, and window metadata. The configured events are `meeting_joined`, `mic_state_changed`, `camera_state_changed`, `participant_count_changed`, `dialog_appeared`, and `connection_warning`.

The RingCentral adapter extracts:

- Meeting joined, only when the correct process/class is present and useful in-meeting evidence exists.
- Mic state from exact `Mute microphone` / `Unmute microphone` labels.
- Camera state from exact `Start video` / `Stop video` labels.
- Participant count from `Participants 3`, `Participants (3)`, or `Participants: 3`.
- Prejoin dialogs for permission and waiting-room states.
- Connection warning for exact reconnecting/unstable labels.

Tests intentionally guard against false positives such as `Mute participants`, bare `Mute`, split `Start` + `video`, `Permission settings`, `Waiting room settings`, and `Reconnecting help`.

The package executor supports `clickWindowRelative`, `clickWindowControl`, and `pressKey`. Cleanup modes include `escape`, `modal`, `toggle`, `settings`, and `sidePanel`. `recording` and `leave` are explain-only in current flows because their entrypoints have no executable `openSteps` and are treated as state-changing or destructive.

The runbook covers dry-run smoke tests, real OpenAI/audio checks, controller acceptance, target selection, text questions, Chinese answers, and safe/risky question behavior. It also notes the `DisableAffinityMask=true` `config.ini` requirement for reliable meeting child-window capture.

## Safety And Privacy Boundaries

The package and profiles already make several boundaries explicit:

- Shared-screen content must not be inferred or described unless captured by an approved observation source and allowed by the user.
- Meeting IDs, invite links, dial-in details, and copy-link values should not be read aloud unless explicitly requested.
- Chat content is private by default.
- Participant names and attendee identities should not be read unless requested and verified from visible UI text.
- Recording, notes/transcript start, final Share, Leave/End, and similar state-changing actions require confirmation.
- Recording and notes are described as features; their content should not be read by default.
- Background blur is framed as a privacy-preserving default.
- Profile narration uses `confidenceThreshold: 0.75` and `forbidSharedScreenInterpretation: true`.
- Question handling marks risky controls as answer-only when labels include words such as `invite`, `leave`, `record`, `share`, `start`, `stop`, `toggle`, `mute`, `unmute`, or `send`.

These rules are currently scattered across profile fields, presenter notes, explainers, QA, and runtime heuristics. There is no single structured safety policy block in the package schema.

## Suspicious Or Needs Verification

The most brittle areas are locator reliability and layout variance:

- Several top-bar controls still use coordinates: meeting info at `x=31,y=21`, network quality at `x=68,y=21`, view layout by `xFromRight=237,y=21`, and report issue by `xFromRight=168,y=21`.
- Runtime side-panel cleanup uses a hard-coded close point around `878,75`; blocker clearing also uses several hard-coded points. These should be validated against window size, DPI scaling, and full-screen state.
- Toolbar More occurrences are overloaded: audio menu uses `More` occurrence 1, camera menu occurrence 2, and overflow More occurrence 3. This is likely fragile if the toolbar order, visible buttons, or locale changes.
- Notes has conflicting package evidence: one note says the current two-person layout exposes Notes directly on the toolbar, while the `ringcentral.video.more.notes` route says the current observed build nests Notes under More as `onconf.controls.NOTES`.
- `ringcentral.video.more.notes` has `area: Meeting toolbar` but its route opens More and then a menu item. A future schema should express both source area and panel destination.
- `Settings` may open the last selected section, so `More > Settings` cannot guarantee a predictable panel without additional navigation.
- `Report issue` says Escape did not reliably close the dialog, while the package depends on modal cleanup. This needs acceptance evidence for the current build.
- The adapter only recognizes English UI Automation labels. Chinese narration exists, but localized RingCentral UI labels are not represented in state extraction or package locators.
- Empty-room behavior is only partly adaptive. `Add coworkers` is rewritten to `Invite` when `participant_count >= 2`, but states for one-person active meetings, unknown counts, participant tiles, and hidden badges still need observation.
- Prejoin coverage is minimal: permission and waiting room are recognized, but join-audio prompts, camera preview, left-meeting state, meeting ended, host not started, recording consent, sharing active, and device warning states are not modeled.
- `Start recording` and `Leave meeting` are explain-only. That is safe, but the package also lacks durable locators and recovery notes for future confirmed execution.
- The design spec planned broader lifecycle, captions, transcription, whiteboard, AI summaries, host/security, breakout rooms, scheduling, joining, and post-meeting surfaces. The current package is strongest for in-meeting controls and still thin outside that core.

## Suggested Package Fields And Document Structure

The current Pydantic model forbids unknown fields, so these suggestions require either a schema migration or a companion markdown/JSON observation log first.

Recommended package-level metadata:

- `observedAt`, `observedBy`, `sourceType`, `sourceRefs`
- `productVersion`, `appChannel`, `osVersion`, `locale`, `dpiScale`
- `meetingScenario`: empty room, one participant, two-plus participants, host, attendee, sharing active, recording active
- `acceptanceStatus`: unverified, smoke-passed, manually-accepted, stale

Recommended entrypoint fields:

- `applicability`: meeting state, role requirement, locale, layout variant
- `locators`: UIA target, alternate target, occurrence, coordinate fallback, coordinate basis, confidence
- `sideEffects`: none, opens menu, opens modal, toggles state, starts recording, leaves meeting
- `safety`: sensitive values, confirmation required, default operation, redaction rule
- `cleanup`: primary close path, fallback close path, expected blocker type
- `recovery`: failure symptom, safe rollback, next best route
- `evidence`: screenshot/reference id, observed window bounds, validation date, tester notes

Recommended docs structure:

- `docs/knowledge/ringcentral-video/observation-log.md`: append-only observations by date, app version, meeting state, locale, and source.
- `docs/knowledge/ringcentral-video/locator-matrix.md`: entrypoint locators, coordinate basis, UIA target, fallbacks, cleanup.
- `docs/knowledge/ringcentral-video/state-matrix.md`: premeeting, prejoin, empty meeting, active meeting, sharing, recording, side panels, settings, left meeting.
- `docs/knowledge/ringcentral-video/privacy-matrix.md`: sensitive surfaces, allowed summaries, disallowed readings, confirmation prompts.
- `docs/knowledge/ringcentral-video/acceptance-runs.md`: command, profile, package flow, version, date, pass/fail, failure recovery.

## Next-Round Knowledge And Acceptance Checklist

- Record a fresh manual acceptance run with RingCentral version/build, Windows version, locale, DPI, window bounds, meeting role, participant count, and screenshots for every executable entrypoint.
- Build a locator matrix for all `clickWindowRelative` and `clickWindowControl` paths; prefer UI Automation targets where stable, and keep coordinates as documented fallbacks with window-size assumptions.
- Resolve Notes/More/Settings variants by documenting direct-toolbar Notes, nested More Notes, `onconf.controls.NOTES`, and last-selected Settings behavior as separate layout variants or applicability rules.
- Expand adapter and tests for additional meeting states: audio-join prompt, camera preview, one-person active meeting, sharing active, recording active, left/ended meeting, host-not-started, permissions, and transient device toasts.
- Expand package knowledge to the spec-intended surfaces: scheduling, joining, whiteboard, captions, live transcription, AI summaries/recaps, post-meeting recordings/transcripts, host/security controls, waiting room, and breakout rooms.
- Add more QA entries for captions, transcription, recordings, participant privacy, chat privacy, connection quality, invite links, host controls, and before/during/after meeting workflows.
- Add bilingual coverage consistently: localized narration exists for `meeting-control-map-demo`, but explainers, QA, locator labels, and adapter label recognition are still English-centric.
- Update the manual acceptance runbook with dated acceptance records, failure recovery recipes, and explicit safe-abort instructions for modal, side panel, settings, recording, share picker, and leave paths.

## High-Value Summary

The current package is a good in-meeting control map, not yet a complete RingCentral Video product knowledge base. Its strongest areas are toolbar/top-bar tours, background blur, participants/chat, synchronized narration, manual overrides, and conservative privacy posture. The next cycle should focus on evidence: versions, layout variants, state matrix, and locator confidence. That will let the package grow without turning every new RingCentral UI observation into a fragile one-off.
