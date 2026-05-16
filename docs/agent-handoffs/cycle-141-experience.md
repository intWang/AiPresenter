# Cycle 141 Experience Notes

## What Changed

Cycle141 added tests only. The new guards prove that the Cycle140 Spanish
optional display metadata remains a rendering/inspection feature and does not
become a routing signal.

The key behaviors now covered in the real RingCentral Video package are:

- Existing `questionAliases.es` still route to `audio-menu`, `video-menu`, and
  `more.background`.
- Once routed, answers render `localizedTitles.es` and
  `localizedPurposes.es`.
- The real package `entrypoint_match_candidates` for those three entrypoints are
  still built from canonical `id`, `title`, `area`, `purpose`, and
  `title_or_id` token fields.
- Spanish-only display metadata tokens do not create an entrypoint match.

## Review Lesson

The first negative test was too sample-shaped. It checked handpicked safety
fragments and also pinned the current Spanish no-match fallback wording. The
review caught both issues.

The sturdier pattern is:

1. Prove candidate construction directly with package model data.
2. Build entrypoint-matcher probes from localized-only tokens.
3. Subtract all existing package candidate tokens, including `title_or_id`
   tokens, before probing because display metadata can intentionally contain
   product labels such as `Blur`, `video`, `Background`, or `Settings`.
4. Assert `_match_entrypoint()` behavior, not incidental fallback copy or
   unrelated Q&A responses.

This keeps tests aligned with the actual contract: localized display metadata
can reuse visible product labels, but it must not become a new source of match
candidates.

## Next Cycle Seed

Cycle142 can move the same boundary to CLI inspection without touching matcher
behavior:

- Assert `entrypoints --language es`, `--language Spanish`, and
  `--language es-MX` show localized/fallback markers for the Cycle140 entries.
- Keep package YAML, aliases, runtime source, providers, and localization counts
  unchanged.
- Avoid re-testing live RingCentral Video acceptance unless a cycle explicitly
  scopes live validation.
