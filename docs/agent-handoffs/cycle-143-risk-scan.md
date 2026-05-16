# Cycle 143 Risk Scan: README And Language Lifecycle Entrypoint Inspection Alignment

Date: 2026-05-17
Cycle: 143
Scope: risk scan for a docs-only README and language-lifecycle alignment around
`entrypoints --language` package-local localized/fallback marker inspection.

This scan owns only this handoff. Do not modify source, tests, package YAML, or
generated artifacts for this risk-scan task. Do not revert concurrent work by
other agents.

## Read Basis

- `README.md`
- `docs/knowledge/language-lifecycle.md`
- `docs/knowledge/ringcentral-video/runtime-safety-routing.md`
- `docs/agent-handoffs/cycle-141-risk-scan.md`
- `docs/agent-handoffs/cycle-142-risk-scan.md`
- `src/ai_presenter/cli.py`
- `src/ai_presenter/packages/models.py`
- `src/ai_presenter/runtime/questions.py`
- `tests/unit/test_cli.py`
- `tests/unit/test_material_packages.py`

Initial `git status --short` showed a pre-existing modified `.coverage`
artifact. This scan does not edit or normalize it.

## Current State Observed

- `entrypoints --package ringcentral-video --language es` is documented in the
  README as a package-local inspection command for localized and fallback
  entrypoint title/purpose metadata.
- The command resolves known language aliases such as `Spanish` and `es-MX` to
  package key `es`, prints `Language: es`, and marks each entrypoint title and
  purpose independently as `localized` or `fallback`.
- `localizedTitles.<lang>` and `localizedPurposes.<lang>` are optional display
  metadata. They are not part of `--require-complete`.
- Spanish required package localization is currently complete for RingCentral
  Video demo narration and Q&A. Spanish runtime support is limited to
  OpenAI-backed speech profiles.
- Local SAPI/Piper/fake speech routes and live RingCentral Video acceptance are
  still separate boundaries. Package-local inspection does not prove either.
- Current durable count references say Spanish has `questionAliases.es` on
  `26/27` entrypoints with `69` aliases, and optional `localizedTitles.es` and
  `localizedPurposes.es` on `8/27` entrypoints.

## Candidate Shape

The next implementation should be docs-only and limited to alignment between
the README and `docs/knowledge/language-lifecycle.md`.

Good target wording:

- Explain that `entrypoints --language <lang>` inspects package-local display
  metadata only.
- Explain `localized` and `fallback` markers as field-level title/purpose source
  markers.
- Keep `Spanish`, `es-MX`, and `es` normalization framed as package-key
  inspection behavior, not broad runtime readiness.
- Keep the Spanish runtime statement profile-scoped: OpenAI-backed speech only.
- Keep local SAPI/Piper and live acceptance explicitly future/evidence-gated.

Out of scope:

- Source changes.
- Test changes.
- Package YAML changes.
- Query alias expansion.
- Provider/profile changes.
- Live RingCentral evidence changes.
- Rewriting historical handoffs only to refresh old snapshots.

## Risk: Overclaiming Spanish Runtime Support

Risk: high.

The README now contains both the package-local `entrypoints --language es`
inspection example and Spanish runtime wording. A small docs alignment can
accidentally make those look like the same support level.

No-go wording:

- "Spanish is supported" without naming the OpenAI-backed speech profile
  boundary.
- "`entrypoints --language es` proves Spanish demo/controller support."
- "Spanish voice support is ready" when local SAPI/Piper/fake routes still
  reject Spanish.
- "Spanish output works in RingCentral" without profile, command, and acceptance
  evidence.

Safer wording:

- "Spanish package localization is complete for required RingCentral Video demo
  narration and Q&A."
- "Spanish runtime output is selectable only with OpenAI-backed speech
  profiles."
- "`entrypoints --language es` inspects package-local entrypoint display
  metadata and does not validate voice providers or demo execution."

## Risk: Optional Metadata Becomes Required

Risk: medium-high.

`localizedTitles.es` and `localizedPurposes.es` are intentionally partial.
Alignment docs should make the marker contract clearer without turning missing
display metadata into a failure.

No-go patterns:

- Saying Spanish is fully localized across entrypoint display metadata.
- Treating `fallback` markers as an error or incomplete localization.
- Saying `--require-complete` includes localized entrypoint title/purpose
  metadata.
- Updating docs so every future language must have localized titles and
  purposes before package localization can pass.

Safer framing:

- Required localization covers demo narration, Q&A questions, and Q&A answers.
- Optional entrypoint display metadata can be partial while required package
  localization is complete.
- `fallback` means canonical package copy was shown for that field. It is an
  expected inspection result, not a failure state.

## Risk: Query Routing Implications

Risk: high.

Entrypoint display metadata and query metadata are adjacent but different.
The docs should not imply that localized titles/purposes become route
candidates because they appear in CLI inspection output.

Keep these boundaries explicit:

- `questionAliases.<lang>` and localized Q&A prompts are query/routing metadata.
- `localizedTitles.<lang>` and `localizedPurposes.<lang>` are display and
  inspection metadata.
- A localized or fallback marker says how a title/purpose line was rendered
  after selecting an entrypoint for display. It does not say that the displayed
  text can be used as a user prompt.
- Q&A-first precedence, alias ordering, operation permission, safety gating,
  and controller interrupts are not changed by docs alignment.

No-go if the README or lifecycle note says or implies that
`entrypoints --language es` expands query matching, makes localized title text a
supported prompt, or changes `can_operate`.

## Risk: Live RingCentral Acceptance Overclaim

Risk: high.

The command name and examples sit near RingCentral demo commands, so docs can
blur inspection with operational acceptance.

Do not claim:

- current live acceptance for any RingCentral route;
- locator reliability for audio menu, video menu, More menu, Background,
  Settings, Notes, Add coworkers, or top-bar coordinate routes;
- virtual microphone readiness for Spanish;
- local Spanish speech assets;
- camera/device/background state changes are safe to perform live.

Use evidence-scoped language:

- Package inspection is local repo behavior.
- Unit tests are repo evidence.
- `doctor` and `voices` are preflight diagnostics.
- Live acceptance requires a dated acceptance run with profile, route, build,
  locale, DPI, window bounds, and result recorded in the RingCentral knowledge
  evidence docs.

## Risk: Stale Counts

Risk: medium.

The current README/lifecycle alignment may need to mention counts, but counts
are the easiest part of the docs to rot. They should be included only where they
add value.

Current source-backed count snapshot:

- Required Spanish package localization: `51/51` demo steps, `12/12` Q&A
  questions, `12/12` Q&A answers.
- Spanish aliases: `questionAliases.es` on `26/27` entrypoints with `69`
  aliases.
- Spanish optional display metadata: `localizedTitles.es` on `8/27` entrypoints
  and `localizedPurposes.es` on `8/27` entrypoints.

If a future docs edit changes these numbers, it should cite the command or test
that refreshed them. If the docs only need to explain behavior, prefer
count-free wording such as "optional display metadata remains partial" and keep
the exact counts in the lifecycle current-state section and test assertions.

## Risk: Overdocumenting Tests

Risk: medium.

The candidate is a documentation alignment task, not a new behavior guard
cycle. A small docs guard can be useful when the risk is wording drift, but the
handoff should not push future implementers into behavior tests unless they
change behavior or factual counts.

Avoid:

- adding long pytest command blocks to README;
- repeating the full Cycle 142 test plan inside user-facing docs;
- presenting unit tests as live RingCentral acceptance;
- requiring behavior-test edits for wording-only changes;
- documenting internal helper names where a user-facing command explanation is
  enough.

Better verification for the docs-only implementation:

- Review the README and lifecycle wording side by side.
- Run `git diff --check`.
- Run `git status --short` and confirm only intended docs changed, plus any
  pre-existing unrelated artifacts such as `.coverage`.
- Run focused tests only if the docs edit changes numeric claims or source-backed
  behavior descriptions.

## Recommended Docs Direction

For README:

- Keep the command example short.
- Define `localized` and `fallback` in one or two sentences.
- State that the command does not validate runtime providers, controller/demo
  execution, local voice assets, or live RingCentral acceptance.
- Keep the Spanish runtime note separate and profile-scoped.

For `docs/knowledge/language-lifecycle.md`:

- Preserve the lifecycle separation: package seed, package localization
  complete, entrypoint display inspection, diagnostics, runtime voice readiness,
  live acceptance.
- Keep optional display metadata outside required localization.
- Keep package-key normalization separate from runtime `--language` promotion.
- Keep "query-ready" tied to curated package Q&A/aliases, not localized
  title/purpose display text.

## Verification To Require

For the future docs-only alignment:

```powershell
git diff --check
git status --short
```

Optional only if count claims are touched:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_cli.py::test_localization_report_outputs_complete_spanish_package tests\unit\test_material_packages.py::test_ringcentral_spanish_display_metadata_counts_match_durable_docs
```

Do not run or require live RingCentral checks for this docs-only alignment unless
the docs are adding a dated acceptance claim, which should be a separate task.

## Go/No-Go Recommendation

Go, with docs-only scope.

This is a good cleanup if it tightens README and language-lifecycle wording
around the package-local `entrypoints --language` inspection contract while
preserving the separate Spanish runtime, routing, optional metadata, and live
acceptance boundaries.

No-go if the change modifies source, tests, package YAML, aliases, provider
profiles, or evidence docs; treats `fallback` markers as failures; implies
localized titles/purposes affect query routing; overstates Spanish local voice
support; or claims live RingCentral acceptance without a dated acceptance run.
