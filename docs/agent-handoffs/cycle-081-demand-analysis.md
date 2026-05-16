# Cycle 081 Demand Analysis

## Verdict/Recommendation

Proceed with a narrow Japanese localization slice for `meeting-control-map-demo` -> `control-map-network` only.

This step should explain `Network quality` as the meeting-health entrypoint for checking diagnostic indicators such as packet loss, jitter, and latency across audio, video, and sharing. The Japanese narration may frame the control as a starting point for troubleshooting unstable meeting media, but it must stay observational: it should not claim the network is the confirmed root cause, promise a fix, change network or meeting settings, or read/store exact private telemetry values.

The implementation should remain package-content-only for this step. Add `narration.localizedText.ja` to the existing `control-map-network` step, and update only directly related localization coverage expectations and handoff/source-index notes if that is part of the implementation cycle. Do not change runtime behavior, locators, action operation, action timing, cleanup, aliases, Q&A, or flow order.

## Current Gap

- Current Japanese demo narration coverage is `31/51`.
- `meeting-control-map-demo` Japanese coverage is `2/22`.
- The first missing Japanese narration step is `meeting-control-map-demo` -> `control-map-network`.
- Existing localization report tests expect:
  - `Localization report: 31/51 demo steps`
  - `- meeting-control-map-demo: 2/22 narration localized`
  - `missing: control-map-network`
- The existing step uses `entrypointId: ringcentral.video.top.network-quality`, `operation: open`, `placement: during`, and `actionOffsetMs: 350`. Those execution semantics should remain unchanged.
- `ringcentral.video.top.network-quality` is a top-bar coordinate route at `x=68,y=21` with `cleanup: escape`; this slice should not modify locator or cleanup behavior.
- `meeting-controls-tour` already has Japanese narration for `explain-network-quality`, and the Japanese Q&A answer for audio/video instability already routes to `Network quality` while avoiding exact cause claims. The control-map copy should align with those boundaries without broadening Q&A or alias scope.
- `docs/knowledge/ringcentral-video/source-index.md` currently says Japanese coverage includes the control-map overview plus meeting-information steps, with remaining control-map narration still future work.

## User Need

Japanese users need a clear mental model for the top-bar `Network quality` control inside the broader meeting-control map. After learning where meeting information lives, they need to know where to look when the meeting feels unstable, especially when audio cuts out, video freezes, or sharing quality degrades.

The Japanese text must express these intentions:

- `Network quality` is the next top-bar meeting-health entrypoint.
- It is used to check diagnostic indicators for audio, video, and sharing quality.
- Important examples include packet loss, jitter, and latency.
- The panel can help users investigate where a problem may be showing up, but it is not a guarantee that the presenter can determine the true cause.
- The presenter explains the purpose and observable categories, not exact private values by default.
- If exact diagnostics are requested later, they should only be read or summarized when visibly available and appropriate for the current privacy context.

The tone should be concise, natural Japanese product narration for a live meeting tour. It can use the product label `Network quality` as-is, matching the existing package style.

## Acceptance Criteria

- `control-map-network` has `narration.localizedText.ja` attached to the existing step in `packages/ringcentral-video.yaml`.
- The existing action block remains unchanged:
  - `entrypointId: ringcentral.video.top.network-quality`
  - `operation: open`
  - `placement: during`
  - `actionOffsetMs: 350`
- The existing route remains unchanged:
  - top-bar `Network quality`
  - coordinate route `x=68,y=21`
  - `cleanup: escape`
- Japanese demo narration coverage advances from `31/51` to `32/51`.
- `meeting-control-map-demo` advances from `2/22` to `3/22`.
- The first remaining missing Japanese step for `meeting-control-map-demo` becomes `control-map-views`.
- Japanese `--require-complete` still fails because 19 control-map steps remain untranslated.
- Q&A counts remain unchanged at `12/12` localized questions and `12/12` localized answers.
- `questionAliases.ja` coverage remains unchanged unless a separate task explicitly requests alias work.
- The localized narration includes the key concepts of meeting health, audio/video/sharing quality, and packet loss/jitter/latency diagnostics.
- The localized narration must not say or imply:
  - the network is definitely the root cause;
  - the presenter can fix the issue;
  - opening the panel changes the network, devices, meeting settings, or media behavior;
  - the presenter reads, records, stores, or transmits exact packet loss, jitter, latency, CPU, connection, or other private diagnostics by default.
- Focused localization tests and localization report expectations should be adjusted only to reflect the one-step coverage increase.

## Non-goals

- Do not localize `control-map-views` or any later `meeting-control-map-demo` step in this slice.
- Do not change `operation: open`, timing, placement, locator references, cleanup behavior, or demo sequencing.
- Do not add or modify Japanese aliases, Q&A, presenter notes, manual controls, profile settings, runtime behavior, diagnostics logic, or CLI formatting beyond directly required count expectations.
- Do not add logic that reads exact packet loss, jitter, latency, CPU, connection-health, device, or private network values.
- Do not add network troubleshooting automation, network repair behavior, device switching, setting changes, refresh behavior, or report submission.
- Do not promise that all diagnostics are always present or that the panel can conclusively identify every audio, video, or sharing issue; availability and meaning may depend on meeting state, account, role, device, and current RingCentral build.
- Do not broaden this slice into `Report issue`, settings, device troubleshooting, recording, chat, participant identity, or post-meeting analytics.

## Suggested Next Slice

After `control-map-network` is localized and reviewed, continue `meeting-control-map-demo` Japanese coverage with `control-map-views` as the next isolated slice.

That next slice should shift from meeting-health diagnostics to local view layout. It should explain that `Views` changes how the user sees the meeting, such as gallery or full-screen style viewing, without implying changes to other participants' experience or meeting state.
