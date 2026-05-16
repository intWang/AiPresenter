# Cycle 095 Risk Scan: RingCentral Video Control Map Recording JA

## Risk summary

Risk review for adding Japanese `localizedText.ja` to `packages/ringcentral-video.yaml` -> `meeting-control-map-demo` -> `control-map-recording`.

Current Japanese localization baseline is `45/51` demo steps overall, with `meeting-control-map-demo` at `16/22`; the first missing step is `control-map-recording`. This is a higher-risk slice than the prior `More` localization because the visible label is `Start recording`, but the control-map step must remain explain-only. Recording can change meeting state, affect every participant, trigger consent or policy obligations, depend on host or moderator permissions, and create persistent meeting artifacts.

The safe target is a narrow narration-only localization. The implementation should preserve:

- `action.entrypointId: ringcentral.video.more.recording`
- `action.operation: explain`
- `narration.placement: before`
- no `narration.actionOffsetMs` on this step
- `openSteps: []` on the `ringcentral.video.more.recording` entrypoint
- English and Chinese narration text
- the step position after `control-map-more` and before `control-map-notes`

The core safety rule is: the Japanese narration may explain where recording lives and why it requires confirmation, but it must not create or imply permission to start, stop, pause, resume, or inspect recording.

## Allowed behavior

- Add exactly one Japanese narration block for `meeting-control-map-demo` -> `control-map-recording`.
- Describe `Start recording` as the recording entrypoint under `More`.
- Say recording changes meeting state and can affect participants.
- Say recording may require explicit consent, organization policy compliance, and suitable host or moderator permissions.
- Say AiPresenter will explain the entrypoint during this tour and will ask before starting or stopping recording.
- Acknowledge that meeting state matters: not joined, waiting-room, permission-dialog, already-recording, or ended-meeting states should not be treated as authorization to act.
- Keep the wording calm and product-demo-like, not legalistic or alarmist.

## Forbidden behavior

- Do not click `Start recording`.
- Do not add `openSteps`, locator steps, action offsets, cleanup actions, or executable routing to `ringcentral.video.more.recording`.
- Do not change `control-map-recording.action.operation` from `explain`.
- Do not start, stop, pause, resume, toggle, verify, or promise recording.
- Do not imply AiPresenter has host permission, moderator permission, organization policy approval, or participant consent.
- Do not say recording is safe, automatic, immediate, available to everyone, or already approved.
- Do not inspect, read, summarize, download, or otherwise reference recording contents or post-meeting artifacts.
- Do not broaden this slice into `control-map-notes`, `control-map-background`, `control-map-settings`, `control-map-leave`, `control-map-summary`, Q&A, aliases, presenter notes, source-index text, validation target changes, or route execution.

## Consent And Policy Wording

The Japanese narration should explicitly separate explanation from action. It should convey these semantics:

- `Start recording` is the entrypoint, not an action being performed.
- Recording changes meeting state and may affect all participants.
- Starting or stopping recording requires the user's explicit current-meeting request.
- Role and permission checks matter; host or moderator capabilities should not be assumed.
- Consent and policy requirements must be clear before any future recording action.

Avoid overclaiming policy compliance. The copy should not state that the app guarantees legal consent, company policy compliance, or recording availability. Safer wording is conditional: "may require", "should be confirmed", and "before starting or stopping, ask and confirm role, permissions, consent, and meeting agreement."

## Host Permissions And Meeting State

Recording is role-gated and state-sensitive. Treat these as review blockers:

- The entrypoint title is `Start recording`, but `control-map-recording` must stay explain-only.
- If the current user is not host or moderator, the narration must not imply they can record.
- If recording is already active, the narration must not imply AiPresenter can stop it without confirmation.
- If a consent prompt, policy notice, permission dialog, waiting room, host-not-started state, or ended meeting appears, the presenter should not continue as though the normal in-meeting control is actionable.
- If live validation is performed, it should record only sanitized control labels and state labels, not participant names, meeting IDs, policy dialogs with account details, or recording artifacts.

## Modal And Menu Cleanup

This step should not open a menu or modal. The prior `control-map-more` step owns opening `More` and its Escape cleanup. For cycle 095:

- Do not add any recording-specific cleanup path because no recording UI should be opened.
- Confirm the prior `More` menu cleanup still leaves the meeting surface neutral before `control-map-recording`.
- Fail review if the `More` menu remains open and a follow-up click could land on `Start recording`.
- Fail review if any recording prompt, consent dialog, toast, or state indicator appears as a result of this localization slice.

## Localization Boundary

Expected coverage movement after implementation:

- Overall Japanese demo narration: `45/51` -> `46/51`
- `meeting-control-map-demo`: `16/22` -> `17/22`
- First missing Japanese step: `control-map-recording` -> `control-map-notes`
- Remaining missing steps should start with `control-map-notes`, then `control-map-background`, `control-map-settings`, `control-map-leave`, and `control-map-summary`

Do not imply full Japanese coverage for `meeting-control-map-demo` until all 22 steps are localized. Japanese `--require-complete` should still fail after this slice because later control-map steps remain untranslated.

## Suggested Test Guardrails

Implementation tests should confirm:

- `control-map-recording` has `localizedText.ja`.
- `control-map-notes` remains without Japanese narration and becomes the first missing step.
- Coverage updates exactly to `46/51` overall and `17/22` for `meeting-control-map-demo`.
- `ringcentral.video.more.recording` still has `openSteps == []`.
- `control-map-recording` still has `operation == "explain"`, `placement == "before"`, and no action offset.
- `questionAliases.ja` remains unchanged for recording; do not add Japanese aliases in this slice.
- The Japanese copy includes `Start recording` and concepts equivalent to meeting state, participants, consent, policy, host permission, entrypoint, explicit request, and no start/stop action.
- The Japanese copy avoids action phrases equivalent to "I will record", "I will start recording", "I will stop recording", "click Start recording", "click", "automatic", or "immediately".

Review should also check CLI localization report expectations if those tests are part of the implementation owner scope. This risk-scan handoff itself does not edit tests.

## Commit Hygiene

This risk-scan agent should create only `docs/agent-handoffs/cycle-095-risk-scan.md`.

For the implementation owner:

- Do not stage `.coverage`; test runs may modify it.
- Do not stage unrelated handoff docs, generated artifacts, screenshots, logs, or other agents' WIP.
- Re-check `git status --short` immediately before staging because other agents may be working in parallel.
- If tests, package YAML, or source-index files are already modified by another agent, review those diffs as shared workspace state rather than reverting them.
- Keep the implementation commit narrow: the one YAML localization block and only the test/doc expectation updates explicitly owned by that implementation slice.

## Reviewer Checklist

- Confirm this risk-scan subagent changed only `docs/agent-handoffs/cycle-095-risk-scan.md`.
- Confirm no YAML, code, tests, `.coverage`, screenshots, logs, or generated files were changed by this risk-scan subagent.
- Confirm the implementation adds only `meeting-control-map-demo` -> `control-map-recording` -> `narration.localizedText.ja`.
- Confirm recording remains explain-only with no executable route.
- Confirm the Japanese narration distinguishes recording location from recording action.
- Confirm the Japanese narration mentions consent, policy, participant impact, host permissions, and explicit confirmation without overclaiming any of them.
- Confirm no menu, modal, prompt, recording state, recording artifact, or participant-identifying content is created by this slice.
- Confirm Japanese coverage advances one step only and the next missing control-map step is `control-map-notes`.
