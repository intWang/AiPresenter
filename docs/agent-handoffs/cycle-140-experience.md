# Cycle 140 Experience Notes

## What Changed

Cycle140 expanded Spanish optional entrypoint display metadata from `5/27` to
`8/27` RingCentral Video entrypoints by adding `localizedTitles.es` and
`localizedPurposes.es` for:

- `ringcentral.video.toolbar.audio-menu`
- `ringcentral.video.toolbar.video-menu`
- `ringcentral.video.more.background`

The implementation stayed package-local. It did not change matcher behavior,
runtime language support, device selection behavior, live RingCentral
acceptance, or the `--require-complete` contract.

## Useful Pattern

When expanding optional display metadata, update three things together:

1. The package YAML copy.
2. Count-backed CLI/package tests and durable docs.
3. Any exact-set guard that enumerates localized display-copy entrypoints.

The stale guard in `test_ringcentral_spanish_entrypoint_copy_pilot_is_present`
was the important catch this round. It intentionally protects the exact set of
entrypoints with optional Spanish display copy, so legal expansion must update
that set instead of only updating aggregate `8/27` counts.

## Copy Boundary

For menu surfaces, Spanish purpose text should describe opening and reviewing
visible UI surfaces. It should not promise that AiPresenter:

- switches microphones, speakers, cameras, audio routes, or video settings;
- reads private device labels or room/account data;
- selects Blur, uploads images, or changes background settings;
- validates local SAPI/Piper Spanish support;
- proves live RingCentral acceptance.

Keeping visible product labels such as `Microphone`, `Speaker`, `More video
settings`, `Background`, and `Blur` literal helps users match the Spanish
explanation to the English RingCentral UI.

## Next Cycle Seed

Cycle141 should consider hardening focused question-answer coverage for the
three newly localized entrypoints without adding new aliases or changing
matching semantics. A good slice would prove that localized display metadata is
shown in `entrypoints --language Spanish` / `es-MX` while Spanish query routing
still depends only on existing `questionAliases.es` and Q&A material.
