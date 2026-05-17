# Cycle 180 Demand Analysis: Participants Panel Privacy Boundary

Date: 2026-05-17

## User Need

Users ask about RingCentralVideo participants in two different ways:

- Navigation: open or locate the Participants panel/button so they can see the meeting roster surface.
- Disclosure or control: list who is present, read names, reveal roles, identify host/moderator status, or use host controls.

Cycle 179 intentionally avoided broad `show participants` because it can mean either surface navigation or identity disclosure. Cycle 180 should make that boundary explicit instead of letting fallback matching decide.

## Repository Signals

- `docs/knowledge/ringcentral-video/privacy-matrix.md` allows explaining the Participants panel purpose and verified count, but disallows reading names/roles by default.
- `docs/knowledge/ringcentral-video/runtime-safety-routing.md` requires Q&A/safety matching before aliases and keeps `can_operate` as the operation gate.
- `packages/ringcentral-video.yaml` already has `ringcentral.video.toolbar.participants` with open steps and notes warning not to identify participants unless verified and allowed.
- Current behavior before this cycle: plain `show participants` routes operably to the Participants panel, while `Please be brief and show participants` returns a generic Presenter settings answer.

## Recommended Slice

Support explicit Participants panel navigation. Reject broad participant disclosure phrases as answer-only privacy guidance.

The narrow policy:

- `participants`, `participants panel`, `open participants panel`, `show participants panel`, `where is the Participants panel`, and `participants button` are navigation/control-surface requests.
- `show participants`, `list participants`, `who is in the meeting`, `read participant names`, `show participant roles`, and `who is host or moderator` are disclosure-adjacent requests unless they explicitly include `panel` or `button`.

## Acceptance Criteria

- `Please be brief and open participants panel` routes to `ringcentral.video.toolbar.participants`.
- Safe panel requests have `can_operate is True`, answer with `Participants panel:`, and create an interrupt.
- Idle controller starts `question-answer-demo` for safe panel requests.
- Running controller queues the interrupt without stopping the active demo.
- `show participants` and `Please be brief and show participants` stay answer-only.
- Broad participant disclosure prompts have `entrypoint_id is None`, `can_operate is False`, no interrupt, and no controller demo.
- The privacy answer should mention participant names, roles/private tabs, explicit user request, and verified visible context.
- `show participants panel` must remain operable and must not be swallowed by the broad privacy guard.

## Non-Goals

- Do not read participant names, roles, private tabs, or host/moderator identity.
- Do not mute, remove, admit, lock, unlock, or change security settings.
- Do not add broad fuzzy routing for participant terms.
- Do not expand localized participant behavior beyond focused sentinels in this cycle.
- Do not stage `.coverage`; it is local test output.
