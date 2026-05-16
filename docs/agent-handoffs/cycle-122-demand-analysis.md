# Cycle 122 Demand Analysis: Spanish Meeting Controls Tour Wedge

Date: 2026-05-16
Cycle: 122
Scope: demand analysis only. This handoff is the only file edited by this subagent; no code, package YAML, tests, runtime presenter skills, durable knowledge, or generated artifacts should be changed here.

## User value

The next useful user-facing increment is to make Spanish RingCentral Video package coverage visibly progress into the main meeting controls tour while preserving the current safety boundary: Spanish remains reportable package localization, not a supported runtime presenter language.

Cycle 121 implemented the diagnostics index guard instead of the proposed Spanish narration wedge. That means the performance/diagnostics candidate has already received the highest-value near-term treatment, while the Spanish package report still shows `meeting-controls-tour: 0/22` and total Spanish demo narration at `7/51`. With `doctor --localization-language es` now available and the diagnostics path indexed, a small Spanish meeting-controls wedge is the clearest next step.

## Recommended slice

Proceed with the Spanish `meeting-controls-tour` orientation wedge that Cycle 121 demand analysis identified, keeping it package-local and narrow.

Add `narration.localizedText.es` only to these four `meeting-controls-tour` steps in `packages/ringcentral-video.yaml`:

- `meeting-overview`
- `explain-meeting-info`
- `explain-network-quality`
- `explain-view-layout`

Expected coverage delta:

- Spanish demo narration moves from `7/51` to `11/51`.
- `meeting-controls-tour` moves from `0/22` to `4/22`.
- `vbg-blur-demo` remains `4/4`.
- `meeting-basics-demo` remains `3/3`.
- `meeting-control-map-demo` remains `0/22`.
- Spanish Q&A remains `12/12` questions and `12/12` answers.
- Spanish aliases remain present on `1/27` entrypoints with `3` aliases.
- Runtime Spanish remains unsupported.

This is higher value than another docs-only or diagnostics-polish slice because it uses the new diagnostic guard to advance actual product content. It is safer than translating a full 22-step flow because the first four steps cover orientation, meeting information privacy, network-quality visibility, and local view layout without entering invite, chat, participants, sharing, recording, notes/transcript, settings, or leave/end controls.

## Acceptance signals

- Exactly four new Spanish narration strings are added, all under `meeting-controls-tour`.
- The four changed step ids are only `meeting-overview`, `explain-meeting-info`, `explain-network-quality`, and `explain-view-layout`.
- English, Chinese, and Japanese text remains unchanged.
- Existing `placement` and `actionOffsetMs` values remain unchanged.
- The Spanish meeting-info narration preserves privacy boundaries around host, meeting ID, link, dial-in information, and encryption status.
- The Spanish network-quality narration names the visible diagnostics surface without inventing causes or claiming observed packet loss, jitter, latency, device, or meeting-health facts.
- The Spanish view-layout narration frames Gallery view and Full screen as local display choices, not changes to participants, media, sharing, recording, or meeting membership.
- `localization-report --package ringcentral-video --language es` reports `11/51` demo steps and `meeting-controls-tour: 4/22 narration localized`.
- The same Spanish report still shows `vbg-blur-demo: 4/4`, `meeting-basics-demo: 3/3`, `meeting-control-map-demo: 0/22`, Q&A `12/12`, and aliases `1/27 (3 aliases)`.
- `doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --require-localization --localization-language es` still exits nonzero with incomplete Spanish localization and runtime language support failure.
- `demo --profile ringcentral-video --package ringcentral-video --flow meeting-controls-tour --language es --dry-run` still rejects Spanish as an unsupported runtime presenter language.
- Chinese and Japanese `localization-report --require-complete` checks still pass.
- `.coverage` remains unstaged and out of scope.

## Risks/Dependencies

- The main risk is boundary drift: adding Spanish package text must not be interpreted as Spanish runtime voice support. Do not add `es` to runtime language choices, controller selectors, provider routing, profiles, speech assets, no-match answers, or `voices`.
- The meeting-info step touches private meeting details. Spanish wording should explain location and purpose, not read or expose host, meeting ID, links, dial-in details, or encryption values by default.
- The network-quality step can easily overclaim. Keep it as a surface description unless live observations explicitly provide metrics.
- The view-layout step should stay local-display only. Do not imply it changes other participants or meeting state.
- Do not combine this with `meeting-control-map-demo`, Q&A, aliases, route ordering, diagnostics behavior, package indexes, action placement, locators, README, durable knowledge, runbooks, presenter skills, or live RingCentral acceptance.
- Current worktree evidence showed `.coverage` modified before this handoff; future agents should leave it alone.

## Handoff prompt

You are the Cycle 122 implementation subagent for AiPresenter. Implement only the Spanish package-local `meeting-controls-tour` orientation wedge. In `packages/ringcentral-video.yaml`, add `narration.localizedText.es` for exactly four steps: `meeting-overview`, `explain-meeting-info`, `explain-network-quality`, and `explain-view-layout`. Preserve all existing English, Chinese, Japanese, `placement`, `actionOffsetMs`, actions, locators, Q&A, aliases, diagnostics, package indexes, runtime voice validation, presenter skills, README, docs, and live-acceptance claims. Update focused localization/package/CLI tests so Spanish demo coverage moves from `7/51` to `11/51` and `meeting-controls-tour` moves from `0/22` to `4/22`, while Spanish runtime remains unsupported and Spanish required localization remains incomplete. Run the Spanish localization report, Spanish doctor localization diagnostics, Spanish demo dry-run rejection, Chinese/Japanese complete localization reports, focused tests, `git diff --check`, and verify `.coverage` is not staged.

## Read-only evidence

- `localization-report --package ringcentral-video --language es` currently reports `7/51` demo steps, `meeting-controls-tour: 0/22`, `meeting-control-map-demo: 0/22`, Q&A `12/12`, and Spanish aliases `1/27 (3 aliases)`.
- `doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --require-localization --localization-language es` reaches diagnostics and exits nonzero with incomplete Spanish localization plus runtime language support failure.
- Cycle 121 implementation and test review confirm the completed slice was a diagnostics index guard, with no package YAML, Spanish coverage, runtime voice, CLI wording, or live RingCentral acceptance changes.
- `packages/ringcentral-video.yaml` currently has Japanese and Chinese localized text for the first four `meeting-controls-tour` steps but no Spanish localized text there.
