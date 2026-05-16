# Cycle 134 Risk Scan: Durable Localization And RingCentral Docs

Date: 2026-05-16
Cycle: 134
Scope: risk scan only for updating durable localization and RingCentral docs
after Cycles 131-133. This handoff is the only intended edit for this task.
Do not edit source code, tests, existing docs, package YAML, generated
artifacts, staging, or commits from this scan.

## Current Baseline

Cycle 131 added optional `localizedTitles` and `localizedPurposes` fields on
operation entrypoints. They are display-only package metadata. They do not feed
matching, aliases, routing, safety gates, controller interrupts, provider
selection, voice validation, or package completeness gating.

Cycle 132 seeded Spanish entrypoint title/purpose copy for exactly two
RingCentral Video entrypoints:

- `ringcentral.video.overview`
- `ringcentral.video.top.network-quality`

Current Spanish entrypoint display-copy coverage is therefore
`localizedTitles.es` on `2/27` entrypoints and `localizedPurposes.es` on `2/27`
entrypoints. Spanish required package localization remains complete for the
existing required contract: demo narration plus Q&A questions and answers.
Those are different coverage dimensions.

Cycle 133 added `ai-presenter entrypoints --language <lang>` as read-only
package-local inspection. It can show localized title/purpose metadata and
fallback source markers, but it does not prove runtime voice support, provider
compatibility, local SAPI/Piper availability, or live RingCentral acceptance.

Existing durable docs already contain useful boundaries in:

- `README.md`
- `docs/knowledge/language-lifecycle.md`
- `docs/knowledge/ai-presenter-maintenance.md`
- `docs/knowledge/ringcentral-video/runtime-safety-routing.md`
- `docs/knowledge/ringcentral-video/source-index.md`
- `docs/knowledge/ringcentral-video/acceptance-runs.md`
- `docs/runbooks/ringcentral-manual-acceptance.md`

The main Cycle 134 risk is not code behavior. It is documentation language that
quietly overstates what Cycles 131-133 proved.

## Risk Register

### R1: Overclaiming Spanish Completion

Risk: durable docs may say Spanish is "fully localized" without naming the
coverage dimension. That would blur required package localization with optional
entrypoint display-copy coverage.

Correct wording:

- Spanish required package localization is complete for demo narration and Q&A.
- Spanish entrypoint display copy is partial: `2/27` localized titles and
  `2/27` localized purposes as of Cycle 132.
- `localizedTitles.es` and `localizedPurposes.es` are optional inspection and
  answer-rendering metadata, not required localization gates.

Avoid:

- "Spanish RingCentral Video is fully localized" unless the sentence
  immediately defines "required demo narration and Q&A only."
- "All Spanish entrypoints are localized."
- "Spanish localization completeness now includes entrypoint titles/purposes."

### R2: Stale Count Drift

Risk: hardcoded totals such as `2/27`, `26/27`, `69 aliases`, `51/51`, or
`12/12` can become stale as package content changes.

Mitigations:

- Keep counts only where they are operationally useful.
- Prefer dated wording: "as of Cycle 132" or "as of 2026-05-16."
- If durable docs mention counts, require the updater to rerun the relevant CLI
  report or package assertions in the same cycle.
- Keep required localization counts separate from optional entrypoint copy
  counts.
- Do not update one count family without checking adjacent count families in
  `runtime-safety-routing.md`, `source-index.md`, `README.md`, and
  `language-lifecycle.md`.

Highest-stale-risk counts:

- Required localized demo/Q&A coverage.
- Alias counts by language.
- Entry point count denominator.
- Spanish optional `localizedTitles` / `localizedPurposes` counts.
- Test pass totals in handoff prose.

### R3: Required Localization Versus Optional Entrypoint Copy

Risk: docs may imply `--require-complete` checks localized entrypoint titles or
purposes. It does not, based on the Cycle 131-132 contract.

Required doc boundary:

- `localization-report --require-complete` gates required demo narration and
  Q&A localized questions/answers.
- Entrypoint `localizedTitles` and `localizedPurposes` are reported as optional
  counts.
- Missing localized entrypoint copy must fall back to canonical title/purpose or
  existing Spanish alias-label behavior, not fail the package.

No durable doc should instruct operators to treat `2/27` entrypoint copy as a
failed Spanish package, and no doc should present `--require-complete` success
as proof that every entrypoint has Spanish display copy.

### R4: Package-Local Language Versus Runtime Voice Support

Risk: docs may present `entrypoints --language es`, package aliases, or passing
localization reports as proof that every profile can speak Spanish.

Correct boundary:

- Package-local inspection accepts language keys that may not be supported by
  runtime voices.
- Spanish runtime presenter support is OpenAI-backed only.
- Fake, Piper, `windows-sapi`, `windows-sapi-en`, and `windows-sapi-zh` profiles
  must still reject Spanish unless a separate promotion cycle changes that
  contract.
- Local SAPI/Piper Spanish support remains future work unless new voice assets,
  profile validation, and acceptance evidence are added.

Docs should not merge these commands into one meaning:

- `localization-report --language es --require-complete`: package content.
- `entrypoints --language es`: package-local display metadata inspection.
- `doctor --language es`: runtime/profile compatibility.
- `demo --language es` / `controller --language es`: runtime behavior.
- `voices --profile ...`: available provider routes and assets.

### R5: Live Acceptance Claims From Local Evidence

Risk: docs may treat unit tests, CLI samples, or read-only package inspection as
live RingCentral acceptance.

Required boundary:

- Live acceptance requires dated evidence in
  `docs/knowledge/ringcentral-video/acceptance-runs.md`.
- A runbook checkbox is procedure, not proof.
- Existing Cycle 003 evidence is read-only observation for a specific app build,
  locale, DPI, window bounds, and empty-room state. It is not broad live route
  acceptance.
- Cycles 131-133 did not perform live RingCentral UI acceptance, audio
  acceptance, local Spanish voice acceptance, or production readiness
  validation.

Any doc line that says "accepted," "validated live," "ready for live demo," or
"works in RingCentral" must name the dated evidence record, environment, route,
and result. Otherwise use "repo-tested," "package-local," "inspection-only," or
"future live acceptance needed."

### R6: Docs Becoming Too Verbose

Risk: durable docs may copy cycle handoff detail into user-facing or maintainer
docs, making them harder to use and easier to leave stale.

Mitigations:

- Put the durable rule in the durable doc; leave cycle history in handoffs.
- Prefer short boundary tables over long narrative duplication.
- Mention exact counts only once per durable doc section unless the count is
  the point of the section.
- Link to `language-lifecycle.md` for package-versus-runtime language rules
  instead of repeating the whole lifecycle everywhere.
- Link to `acceptance-runs.md` for live evidence rules instead of restating the
  manual template in localization docs.
- Keep README wording operator-focused and concise.

## No-Go Conditions

Do not accept durable doc updates if any of these are true:

- Spanish is described as fully localized without limiting that claim to
  required demo narration and Q&A.
- Docs claim all Spanish entrypoint titles or purposes are localized while the
  current known count is `2/27`.
- `localizedTitles` or `localizedPurposes` are described as required
  localization, matcher input, alias input, safety input, routing input,
  provider input, or controller interrupt input.
- `entrypoints --language` is described as runtime voice validation or provider
  support.
- Passing `localization-report --require-complete` is described as proof of
  local Spanish SAPI/Piper support, audio output, controller readiness, or live
  RingCentral acceptance.
- Docs imply Spanish local SAPI/Piper support exists without a separate
  implementation, provider validation, and acceptance record.
- Any live acceptance claim lacks a dated record in `acceptance-runs.md`.
- Runbook checklist completion is treated as evidence before a dated run is
  recorded.
- Count updates are made without rerunning or citing the command/source that
  produced the new counts.
- Durable docs duplicate full cycle handoff details instead of summarizing the
  stable rule and linking to the right source.
- Documentation edits stage or include unrelated generated artifacts such as
  `.coverage`.

## Must-Have Doc Checks

Before accepting a Cycle 134 durable-doc update, the implementation owner should
perform these checks:

- Search for overbroad Spanish claims:
  `rg -n "fully localized|complete|runtime support|live acceptance|accepted|ready" README.md docs`
- Search for entrypoint copy semantics:
  `rg -n "localizedTitles|localizedPurposes|entrypoints --language|2/27|27 entrypoints" README.md docs`
- Verify each `localizedTitles` / `localizedPurposes` mention says optional,
  display-copy, package-local, or inspection-only unless it is describing exact
  schema fields.
- Verify each `--require-complete` mention says it gates required demo
  narration plus Q&A, not optional entrypoint copy.
- Verify each `entrypoints --language` mention says package-local inspection and
  does not claim runtime voice/provider support.
- Verify each Spanish runtime mention distinguishes OpenAI-backed support from
  local SAPI/Piper future work.
- Verify each live RingCentral acceptance claim points to a dated
  `acceptance-runs.md` record.
- Verify README remains concise and does not become a mini cycle-history log.
- Run `git diff --check` after doc edits.
- Run `git status --short` and confirm only intended documentation files are
  modified; do not stage `.coverage`.

Optional count refresh commands if the doc update changes counts:

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language es --require-complete
.\.venv\Scripts\ai-presenter.exe entrypoints --package ringcentral-video --language es
rg -n "localizedTitles:|localizedPurposes:" packages\ringcentral-video.yaml
```

## Recommended Durable-Doc Shape

If Cycle 134 updates durable docs, prefer this compact structure:

- README: one short note that Spanish required package localization is complete,
  Spanish runtime speech is OpenAI-backed only, local SAPI/Piper remains
  unsupported, and `entrypoints --language` inspects package-local display
  metadata.
- `language-lifecycle.md`: one entrypoint-display-copy paragraph under package
  localization, explicitly saying optional title/purpose counts do not affect
  `--require-complete`.
- `runtime-safety-routing.md`: one boundary note that localized entrypoint copy
  does not affect matching, Q&A precedence, safety routing, or controller
  interrupts.
- `source-index.md`: one dated count summary, if counts are refreshed in the
  same cycle.
- `acceptance-runs.md` and the runbook: no acceptance status change unless a
  real dated run occurred.

## Recommendation

Proceed with durable doc updates only if the edits preserve the package-local,
optional, display-only nature of entrypoint title/purpose copy and keep live
acceptance, runtime voice support, and required localization as separate
concepts. The safest update is short, cross-linked, and count-light. If counts
are included, make them dated and source-backed.
