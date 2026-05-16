# Cycle 133 Demand Analysis: Localized Entrypoint Inspection

Date: 2026-05-16
Cycle: 133
Scope: demand analysis only. This file is the only intended edit. Do not
modify source, tests, package YAML, profiles, durable docs, generated artifacts,
staging, commits, or live acceptance evidence in this analysis slice.

## Question

After Cycle131 added optional `localizedTitles` / `localizedPurposes` schema and
runtime answer rendering, and Cycle132 seeded Spanish localized title/purpose
copy for `ringcentral.video.overview` and
`ringcentral.video.top.network-quality`, what is the best narrow Cycle133
slice?

Recommendation: add a read-only `entrypoints --language` inspection mode for
package authors and operators. It should show localized title and purpose copy
when present, show explicit fallback status when missing, and preserve the
current default English `entrypoints` output.

## Current Product State

The Spanish localization wedge has moved from infrastructure to a tiny real
content pilot:

- Required Spanish package localization is complete for demo narration and
  Q&A: `51/51` demo steps, `12/12` localized questions, and `12/12` localized
  answers.
- Spanish entrypoint aliases are broad but still informational:
  `questionAliases.es` covers `26/27` entrypoints with `69` aliases.
- Spanish localized entrypoint display copy is intentionally partial:
  `localizedTitles.es` and `localizedPurposes.es` cover `2/27` entrypoints.
- `localization-report` exposes those counts, but it does not let an author or
  operator inspect the actual per-entrypoint localized display copy.
- `entrypoints` remains useful for canonical inventory, but it prints only
  English title plus area. For the two seeded Spanish entrypoints, the command
  hides the new localized copy completely.

That means Cycle132 created a concrete authoring pattern, but the fastest
operator-facing verification path is still indirect: run a localization count,
then inspect YAML or ask runtime questions. The next slice should make that
state visible without touching runtime matching, safety, or package content.

## Options Compared

### 1. Add CLI `entrypoints --language` Inspection

This is the best next slice. The feature became timely only after Cycle132:
there is now real Spanish localized entrypoint title/purpose content to inspect,
and there are still 25 unseeded entrypoints where fallback visibility matters.

The command should remain read-only and package-local. A conservative design:

- default `entrypoints --package ringcentral-video` output stays byte-for-byte
  compatible except for unrelated Typer formatting;
- `entrypoints --language es` prints the selected language in the header;
- each entrypoint displays the localized title if `localizedTitles.es` is
  present and nonblank, otherwise the canonical title;
- each entrypoint displays the localized purpose if `localizedPurposes.es` is
  present and nonblank, otherwise the canonical purpose;
- each entrypoint marks title and purpose source, such as `localized` or
  `fallback`;
- the command does not imply Spanish runtime voice readiness, live acceptance,
  or required localization completeness.

This helps package authors review copy before seeding the next entries, helps
operators understand which answers are still mixed-language fallbacks, and gives
future reviewers a stable CLI fixture for localized entrypoint copy.

### 2. Seed 1-2 More Spanish Localized Entrypoint Copies

This remains valuable, but it is no longer the highest-leverage immediate
slice. More copy would move Spanish from `2/27` toward `3/27` or `4/27`, yet it
would continue the content treadmill before the repo has a friendly inspection
surface for reviewing the seeded pattern.

If this option is chosen later, good candidates should remain low-risk,
explain-first surfaces such as view layout or report issue, not privacy- or
state-changing controls. It should still avoid chat, participants, invite,
share, recording, notes, microphone, camera, and leave unless a risk scan
explicitly scopes them.

### 3. Add Durable Localization Authoring Docs

This is also important. `docs/knowledge/language-lifecycle.md` still describes
package seed examples as `localizedText`, `localizedQuestions`,
`localizedAnswers`, and `questionAliases`; it does not yet name
`localizedTitles` / `localizedPurposes` or the new `2/27` Spanish entrypoint
copy state. Durable docs should catch up soon.

However, docs alone would not give authors an ergonomic way to check what the
runtime-facing package inventory looks like. The CLI slice can be tested
against current behavior and then a small docs cycle can document the command
and authoring rules with less guesswork.

### 4. Small UI/Performance/Tooling Improvement From Current Context

The best small tooling improvement I found is adjacent to option 1: make
localized entrypoint inspection expose purpose copy, not just localized titles
or aggregate counts. The current `entrypoints` command is compact but too thin
for localization review because `localizedPurposes` are the field most likely
to carry mixed-language fallback risk.

I do not recommend a performance slice here. The relevant localization and
entrypoint inspection paths are offline CLI/reporting paths, not hot demo or
controller loops. A performance cycle would be speculative unless it targets a
known runtime path with structural tests.

I do not recommend a controller UI slice in Cycle133 either. Spanish runtime is
OpenAI-profile-bound and live RingCentral acceptance remains unproven; changing
the controller language UI now would risk over-signaling demo readiness.

## Recommended Cycle133 Slice

Implement read-only localized entrypoint inspection in the CLI:

1. Add `--language <lang>` to `ai-presenter entrypoints`.
2. Preserve the current default output when `--language` is omitted.
3. When `--language` is provided, render per-entrypoint localized display copy
   for title and purpose using the same fallback contract as the package model:
   nonblank localized value first, canonical English fallback otherwise.
4. Mark whether title and purpose came from localized copy or fallback.
5. Add focused CLI tests using the real RingCentral package:
   - seeded Spanish entries show localized title and purpose;
   - an unseeded Spanish entry shows canonical fallback and is marked as
     fallback;
   - default `entrypoints` behavior remains unchanged;
   - area filtering still works with `--language`.
6. Optionally add one README command example only if the implementation cycle
   has enough room after tests; durable authoring guidance should stay a
   separate docs-owned slice.

This creates a useful bridge between localization-report counts and runtime
question-answer behavior without broadening the content surface.

## Acceptance Criteria

- `ai-presenter entrypoints --package ringcentral-video` retains the current
  compact English inventory behavior.
- `ai-presenter entrypoints --package ringcentral-video --language es` prints a
  language-aware inventory that includes title and purpose inspection for each
  listed entrypoint.
- `ringcentral.video.overview` and
  `ringcentral.video.top.network-quality` show Spanish localized title and
  purpose copy, with source markers indicating localized values.
- At least one unseeded Spanish entrypoint, such as
  `ringcentral.video.toolbar.participants`, shows canonical fallback title and
  purpose with source markers indicating fallback.
- `--area` filtering still applies before rendering and works together with
  `--language`.
- The command remains read-only and does not load speech providers, run desktop
  automation, validate runtime voice support, or change package localization
  completeness rules.
- Localization reports remain count-based and unchanged except for tests that
  may call both commands side by side.
- Runtime Q&A rendering, alias matching, operation safety gating, controller UI,
  profile voice compatibility, and package YAML content are unchanged.
- Verification for the implementation cycle includes focused CLI tests,
  relevant package/model tests if helper methods are touched, `ruff`, and
  `git diff --check`.

## Out Of Scope

- No additional Spanish localized entrypoint title/purpose content.
- No full `27/27` Spanish entrypoint localization target.
- No Chinese or Japanese localized title/purpose content.
- No matching, ranking, alias, duplicate-diagnostic, or Q&A precedence changes.
- No runtime presenter language promotion, local Spanish SAPI/Piper support,
  OpenAI model change, or live audio claim.
- No controller UI localization or language picker behavior change.
- No live RingCentral Video acceptance claim.
- No durable language lifecycle or authoring docs in the same implementation
  slice unless explicitly approved after the CLI tests pass.
- No staging, commit, generated artifact cleanup, or `.coverage` handling.

## Why This Beats The Alternatives

Cycle131 made localized entrypoint display copy possible. Cycle132 proved it on
two safe RingCentral surfaces. Cycle133 should make that partial state easy to
inspect before adding more content. Otherwise future agents have to choose
between aggregate counts, YAML spelunking, or runtime question probes to review
localized title/purpose quality.

The CLI slice is narrow, testable, and operator-visible. It improves tooling
without claiming full Spanish localization, without touching safety-sensitive
RingCentral actions, and without pretending package text equals live demo
acceptance. More Spanish copy and durable authoring docs should follow, but the
inspection surface will make both of those future slices cleaner.
