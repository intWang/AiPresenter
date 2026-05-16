# Cycle 142 Experience Notes

## What Changed

Cycle142 added CLI inspection tests only. The tests now guard that
`entrypoints --language` continues to normalize Spanish language aliases and
show localized/fallback markers for the Cycle140 display metadata entries.

Covered paths:

- `--language es`
- `--language Spanish`
- `--language es-MX`
- `Meeting toolbar`
- `More menu`

The guard covers localized title and purpose markers for:

- `ringcentral.video.toolbar.audio-menu`
- `ringcentral.video.toolbar.video-menu`
- `ringcentral.video.more.background`

It also keeps fallback title and purpose markers visible for nearby entries:

- `ringcentral.video.toolbar.audio`
- `ringcentral.video.more.recording`

## Useful Pattern

For CLI display inspection, prefer marker-centered helpers over full prose
assertions. The durable contract is:

- the command resolves known aliases to `Language: es`;
- the expected entrypoint id appears in the requested area;
- the title marker is `localized` or `fallback` as expected;
- the following purpose line carries the matching source marker.

Exact Spanish prose belongs in package/model tests. CLI tests should prove that
the command selects package-local display metadata and labels its source, while
remaining tolerant of future copy edits.

## Review Lesson

The first alias test covered only `Meeting toolbar`, so it missed
`ringcentral.video.more.background` in `More menu`. When a cycle says "all
Cycle140 entries," each area that contains a scoped entry should be represented
for every language alias under test.

## Next Cycle Seed

Consider a docs-only guard that keeps README and lifecycle wording aligned with
the tested CLI contract: `entrypoints --language` is package-local inspection,
not runtime Spanish readiness, matcher expansion, provider validation, or live
RingCentral acceptance.
