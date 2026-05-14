# RingCentral Video Material Package Expansion Design

Date: 2026-05-14

## Goal

Expand the RingCentral Video material package so the AI presenter has a broad, structured map of RingCentral Video while staying optimized for live demo behavior.

The package should support three jobs:

- Guide the AI presenter through selected live demo flows.
- Give concise, product-aware answers about RingCentral Video features.
- Preserve strict privacy boundaries around participants, chat, shared content, recordings, transcripts, notes, and meeting links.

## Scope

This design expands `packages/ringcentral-video.yaml` only. It does not add a new package format, does not wire a CLI command for demo flow execution, and does not change desktop automation behavior.

The expanded package should cover RingCentral Video broadly, but the first implementation should keep each demo flow short and reliable. The package is a knowledge map first and a full automation suite later.

## Source References

The feature map is based on public RingCentral documentation and product pages:

- RingCentral Video in-meeting controls: https://support.ringcentral.com/au/en/video/in-meeting-controls.html
- RingCentral Video joining and scheduling: https://support.ringcentral.com/ca/en/video/joining-scheduling.html
- RingCentral Video attendee controls: https://support.ringcentral.com/es/es/shared/content/app/using-ringcentral-video-attendee-controls-desktop-web.html
- RingCentral Video product overview: https://www.ringcentral.com/video

## Content Architecture

Use the existing package sections:

- `operationEntrypoints`: the functional map of RingCentral Video surfaces and controls.
- `demoFlows`: curated live demo scripts made from package entry points.
- `explainers`: reusable short explanations keyed by feature area.
- `qa`: anticipated questions and safe answers.
- `manualControls`: live presenter override phrases.

Do not introduce new schema fields in this expansion. The current Pydantic model forbids unknown fields, so this keeps the change low-risk and validation-friendly.

## Entrypoint Coverage

Keep existing entry points and add new ones across these areas:

- Meeting lifecycle: schedule meeting, join meeting, copy meeting link/details, recent meetings, recent recordings.
- Readiness: microphone menu, audio device selection, speaker/mic test, camera menu, video source selection, background and effects, appearance improvements.
- In-meeting collaboration: share screen, share computer audio, stop sharing, whiteboard, chat, participants, invite, reactions, raise hand, captions.
- Host and moderator controls: recording, participant management, mute others, turn off participant video, security settings, waiting room, moderator assignment, breakout rooms.
- AI and post-meeting context: live transcription, closed captions, AI summaries or recaps, recordings, transcripts, collaborative notes.
- Meeting health: network connection and CPU usage, connection warning, feedback/help.

Each entry point should include:

- A stable id using the existing dotted namespace style.
- A user-facing title.
- An area that matches the surface where the action happens.
- A clear purpose.
- Minimal `openSteps` that describe the intended route without overclaiming executable support.
- Presenter notes that state privacy limits and useful demo context.

## Demo Flows

Add a curated first batch of short flows. Each flow should be 3-5 steps so it can be used during a live presenter demo without becoming brittle.

Recommended flows:

1. `meeting-readiness-demo`
   Covers audio, camera, background/effects, and connection readiness. This helps the AI presenter explain how a host gets ready before speaking.

2. `collaboration-basics-demo`
   Covers invite, participants, chat, reactions, raise hand, and whiteboard. This shows how people interact without turning the demo into a full training session.

3. `presentation-and-share-demo`
   Covers screen share, share audio, annotations or whiteboard context, and stop sharing. This flow must emphasize that the presenter cannot interpret shared content unless the user explicitly allows and the content is verified.

4. `accessibility-and-ai-context-demo`
   Covers captions, live transcription, AI summaries or recaps, and post-meeting transcripts/recordings. This should frame AI output as meeting context, not as content the presenter may read aloud by default.

5. `host-control-demo`
   Covers recording, participant management, mute others, security settings, waiting room, and breakout rooms. This should clearly distinguish attendee controls from host or moderator-only controls.

6. `meeting-lifecycle-demo`
   Covers schedule, join, invite/copy details, live meeting, and post-meeting recordings or summaries. This gives the package a complete before-during-after story.

Keep the existing `vbg-blur-demo` and `meeting-basics-demo`, but it is acceptable to refine their wording for consistency with the new package style.

## Explainers

Expand explainers into a reusable knowledge base for live answers. Add or refine keys for:

- `readiness`
- `audio`
- `camera`
- `background`
- `sharing`
- `whiteboard`
- `participants`
- `chat`
- `reactions`
- `captions`
- `recording`
- `host_controls`
- `security`
- `breakout_rooms`
- `scheduling`
- `joining`
- `ai_summaries`
- `meeting_health`

Each explainer should have a short script, practical details, and related entry point ids. Short scripts should sound like a live presenter, not documentation copied into YAML.

## Q&A

Add anticipated questions that the AI presenter can answer safely during a live demo:

- How do I make sure my audio and camera are ready?
- How do I protect my real background?
- Can you describe what is being shared?
- How do I invite people or copy meeting details?
- How do I use captions or live transcription?
- Where do recordings, summaries, or transcripts appear after a meeting?
- What can hosts or moderators control?
- Can the presenter read chat or participant names?
- How do I troubleshoot connection quality?
- How do I run a quick before-during-after meeting demo?

Answers must stay within verified UI state and package knowledge. They must not invent plan availability, attendee identities, private chat contents, shared-screen contents, or recording/transcript contents.

## Privacy And Safety Rules

The package must keep these rules explicit in presenter notes, explainers, and QA:

- Shared screen content is sensitive by default.
- Chat text is private by default.
- Participant names and roles should not be read unless the user asks and the UI text is verified.
- Meeting links and dial-in details should not be read aloud unless the user explicitly asks.
- Recordings, transcripts, AI summaries, collaborative notes, and highlights should be described as features, not read as content unless explicitly allowed.
- Destructive actions such as leaving, ending, removing participants, muting others, and changing security settings require confirmation before execution.
- Host-only and moderator-only controls should be labeled as permission-dependent.

## Validation

Implementation should update package tests so the expansion is protected by assertions without making the tests brittle. The tests should verify:

- The package still loads successfully.
- Representative new entry points exist.
- New demo flows reference known entry points.
- Key explainers and QA entries exist.
- Privacy-critical entry points such as sharing, chat, recordings, transcripts, and invite details carry safe notes or answers.

Run targeted package tests after editing, then run the full test suite if the local environment has dev dependencies installed.

## Non-Goals

- No new YAML schema fields.
- No CLI command for running demo flows.
- No desktop automation implementation for new open step action names.
- No claim that every entry point is executable today.
- No generated transcript, recording, or shared-screen content.

## Acceptance Criteria

The expansion is accepted when:

1. `packages/ringcentral-video.yaml` reads as a broad RingCentral Video knowledge map.
2. The package includes short demo flows for live AI presenter use.
3. The first implementation covers lifecycle, readiness, collaboration, presentation, accessibility/AI context, host controls, and meeting health.
4. Safety and privacy boundaries are visible in the package content.
5. Existing package validation passes without schema changes.
