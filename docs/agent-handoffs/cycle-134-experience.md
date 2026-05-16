# Cycle 134 Experience Synthesis: Durable Localization Authoring Docs

Date: 2026-05-16
Cycle: 134
Scope: experience synthesis only. This file is the only intended edit from this
agent. Do not stage or commit.

## Product Lesson

Cycle134 did the quiet but important product work after three implementation
cycles: it turned localized entrypoint behavior into durable authoring guidance.

Cycle131 added optional localized title and purpose fields. Cycle132 seeded two
Spanish RingCentral Video examples. Cycle133 made the partial state inspectable
through `entrypoints --language`. Cycle134's lesson is that a visible authoring
surface needs a durable interpretation layer before the repo adds more content.

The useful product move was not to make a bigger Spanish claim. It was to
document what the product can honestly say:

- Spanish required package localization is complete for demo narration and Q&A.
- Spanish entrypoint display metadata is intentionally partial at `2/27` titles
  and `2/27` purposes as of 2026-05-16.
- Package-local inspection can show localized and fallback display text without
  saying anything about speech providers, local voices, or live RingCentral
  acceptance.

That distinction gives future authors room to improve the experience without
turning every partial metadata count into a false readiness signal.

## Technical And Documentation Pattern

Keep package-local display metadata separate from runtime voice support.

The durable docs now treat `localizedTitles.<lang>` and
`localizedPurposes.<lang>` as optional package-local display metadata. They can
improve entrypoint answer rendering and author inspection, but they must stay
out of:

- matching candidates;
- alias ordering;
- Q&A precedence;
- safety gating;
- controller interrupts;
- provider routing;
- voice asset checks;
- live acceptance claims.

The corresponding CLI pattern is the same one established by Cycle133:
`entrypoints --language <lang>` is a raw package metadata lookup. It prints the
requested `Language: <key>`, then marks each display field as `localized` when
nonblank package copy exists or `fallback` when canonical English copy is shown.
It should not call runtime voice validation, normalize the language into a
runtime-supported set, or imply provider readiness.

Cycle134 also made a good documentation-shape choice: put the canonical rule in
`docs/knowledge/language-lifecycle.md`, and keep the RingCentral-specific source
index to a short dated count and wording cleanup. That avoids creating another
parallel localization guide.

## Guardrails For Future Count Updates

Counts are useful only when they are dated, source-backed, and scoped to the
right coverage dimension.

When updating counts, rerun or cite the relevant command in the same cycle:

- `localization-report --package ringcentral-video --language es --require-complete`
- `entrypoints --package ringcentral-video --language es`
- package YAML searches for `localizedTitles:` and `localizedPurposes:`

Keep these count families separate:

- required demo narration and Q&A completeness;
- localized question alias coverage;
- optional localized entrypoint title coverage;
- optional localized entrypoint purpose coverage;
- runtime voice/provider support;
- live acceptance evidence.

Do not update one durable count without checking nearby count mentions in
`README.md`, `docs/knowledge/language-lifecycle.md`,
`docs/knowledge/ringcentral-video/source-index.md`, and any other touched
RingCentral knowledge packet. Prefer wording such as "as of 2026-05-16" when a
durable doc includes exact totals.

## Guardrails For Docs Wording

Use precise verbs and nouns. Say "required package localization is complete"
when referring to demo narration and Q&A. Say "optional entrypoint display
metadata is partial" when referring to `localizedTitles` and
`localizedPurposes`.

Avoid these shortcuts unless a future cycle proves them:

- "Spanish RingCentral Video is fully localized" without immediately limiting
  the claim to required demo narration and Q&A.
- "All Spanish entrypoints are localized."
- "`--require-complete` validates localized titles and purposes."
- "`entrypoints --language es` validates Spanish runtime support."
- "Spanish local SAPI/Piper is ready."
- "CLI/unit-test evidence proves live RingCentral acceptance."

Use "package-local", "inspection-only", "optional display metadata",
"OpenAI-backed runtime support", and "live acceptance remains unproven" where
those boundaries matter.

## Claims Still Unproven

- Full Spanish entrypoint display localization remains unproven; the durable
  count is still `2/27`, not `27/27`.
- Localized titles and purposes are not proven safe or desirable as matcher,
  routing, alias, Q&A precedence, safety, or controller inputs.
- Spanish local SAPI/Piper support remains unproven.
- OpenAI-backed Spanish runtime selection is not the same as live RingCentral
  Video acceptance.
- `entrypoints --language` output does not prove audio output, provider
  credentials, desktop automation, network behavior, or real meeting behavior.
- No new dated live acceptance record was created in Cycle134.
- Dated counts in durable docs can drift when package content changes.

## Suggested Cycle135 Options

1. Add the next small Spanish entrypoint display-copy slice.
   Choose one or two low-risk explanatory or diagnostic RingCentral entrypoints,
   keep `localizedTitles` / `localizedPurposes` display-only, and update exact
   optional count assertions. This is the best next content move now that the
   authoring contract is documented.

2. Add focused docs/tests around count drift if content growth continues.
   A lightweight verifier or focused test around optional display-copy counts
   would reduce the chance that durable docs and package state silently diverge.

3. Add a concise README inspection example.
   Cycle134 intentionally left README untouched. A future operator-facing slice
   could add `entrypoints --package ringcentral-video --language es` with one
   sentence that it is package-local display inspection, not runtime voice
   validation.

4. Refine localized inspection UX only after observed friction.
   Source labels, compact modes, or formatting polish can wait until someone
   reports the current output is hard to use. Preserve default no-language
   output compatibility.

5. Defer runtime/local voice expansion until it has its own acceptance plan.
   Spanish SAPI/Piper, broader provider routing, or live RingCentral claims need
   separate implementation, profile validation, and dated acceptance evidence.

## Verification Commands Worth Reusing

Current Spanish package and optional display count check:

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language es --require-complete
```

Localized entrypoint inspection:

```powershell
.\.venv\Scripts\ai-presenter.exe entrypoints --package ringcentral-video --language es
```

Focused CLI tests for the documented behavior:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_cli.py::test_localization_report_outputs_complete_spanish_package tests\unit\test_cli.py::test_entrypoints_language_inspects_ringcentral_localized_and_fallback_copy tests\unit\test_cli.py::test_entrypoints_language_uses_package_local_metadata_without_runtime_voice_validation tests\unit\test_cli.py::test_doctor_rejects_package_only_language_after_complete_localization tests\unit\test_cli.py::test_doctor_openai_profile_accepts_spanish_runtime_language
```

Docs wording and count scan:

```powershell
rg -n "localizedTitles|localizedPurposes|entrypoints --language|2/27|package-local|runtime|live acceptance|fully localized|require-complete" README.md docs
```

Package source spot check:

```powershell
rg -n "localizedTitles:|localizedPurposes:" packages\ringcentral-video.yaml
```

Repository hygiene:

```powershell
git diff --check
git status --short
```

Do not stage `.coverage` or unrelated durable docs unless the active cycle
explicitly owns them.

## Current Diff Summary

At synthesis time, the worktree showed:

- `.coverage` modified as unrelated generated state.
- `docs/knowledge/language-lifecycle.md` modified with the durable entrypoint
  display metadata rules, package-local inspection semantics, Spanish `2/27`
  optional counts, and runtime/live-acceptance boundaries.
- `docs/knowledge/ringcentral-video/source-index.md` modified with Spanish
  optional display metadata counts and stale "package-only" wording replaced by
  a package-alias versus runtime-provider boundary.
- Cycle134 demand analysis, technical scan, risk scan, and implementation
  handoff files were untracked handoff artifacts.

No source, tests, package YAML, staging, or commits were changed by this
experience synthesis agent.
