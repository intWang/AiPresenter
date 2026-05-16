# Cycle 134 Technical Scan: Localization Lifecycle Authoring Docs

Date: 2026-05-16

## Scope

Investigated durable documentation updates for the localization lifecycle and
entrypoint display-copy authoring after Cycle133.

This agent changed only this handoff file. No source, tests, package YAML,
durable knowledge docs, staging, or commits were changed.

## Current Baseline

Cycle131 added optional `OperationEntrypoint.localizedTitles` and
`localizedPurposes` schema fields plus fallback helpers in
`src/ai_presenter/packages/models.py`. Cycle132 seeded Spanish display metadata
for exactly two RingCentral Video entrypoints. Cycle133 added read-only
`entrypoints --language` inspection with localized/fallback source markers.

Current command output confirms the important distinction:

```powershell
.\.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language es
```

Reports:

```text
- questionAliases.es present on 26/27 entrypoints (69 aliases)
- localizedTitles.es present on 2/27 entrypoints
- localizedPurposes.es present on 2/27 entrypoints
Localization report: 51/51 demo steps, 12/12 Q&A questions, 12/12 Q&A answers localized for es.
```

So Spanish required package localization is complete, while Spanish
entrypoint display metadata is intentionally partial at `2/27`. Do not collapse
those two facts into a single "Spanish is fully localized" claim.

Current `entrypoints --language es` output uses package-local metadata only. It
shows localized copy for:

- `ringcentral.video.overview`
- `ringcentral.video.top.network-quality`

All other entrypoints currently show canonical fallback titles and purposes with
explicit source markers such as `(title: fallback)` and `(fallback)`.

## Durable Documentation Targets

Best primary target:

- `docs/knowledge/language-lifecycle.md`

This is already the canonical lifecycle boundary doc. Update it rather than
creating a new standalone doc unless the section becomes too large. The current
doc names `localizedText`, `localizedQuestions`, `localizedAnswers`, and
`questionAliases`, but it does not yet name `localizedTitles` or
`localizedPurposes` in the lifecycle gates.

Likely edits:

- In `Package seed`, add `localizedTitles.<lang>` and
  `localizedPurposes.<lang>` as package-local text examples.
- Add a short "Entrypoint Display Metadata" subsection after `Package seed` or
  after `Package localization complete`.
- State that `localizedTitles` and `localizedPurposes` are package-local display
  metadata for answer/rendering/inspection, not query matching, safety routing,
  action routing, or runtime voice support.
- State that these fields are optional and are counted by `localization-report`
  for author visibility, but they do not participate in
  `required_localization_complete`.
- Document `entrypoints --language <lang>` as the inspection command for this
  metadata. It should be described as a package-local lookup that prints
  localized values when present and canonical fallbacks with source markers when
  missing.
- Keep the boundary explicit: a language key in package YAML does not imply
  runtime `demo/controller --language`, provider routing, local voice assets, or
  live RingCentral acceptance.
- In `Current Spanish State`, add the current `localizedTitles.es 2/27` and
  `localizedPurposes.es 2/27` counts. Keep the separate facts that required
  Spanish demo/Q&A localization is `51/51`, `12/12`, `12/12`, and that Spanish
  runtime output is OpenAI-backed only.
- Add "claims to avoid": do not say Spanish entrypoint display metadata is
  complete; do not say `2/27` means Spanish package localization is incomplete;
  do not say package-local Spanish keys prove SAPI/Piper support or live
  acceptance.

Secondary target:

- `docs/knowledge/ringcentral-video/source-index.md`

Likely edits:

- In the `packages/ringcentral-video.yaml` repository signal row, include the
  optional display-copy state: Spanish entrypoint display metadata currently
  covers `2/27` titles and `2/27` purposes.
- Fix or soften the `src/ai_presenter/runtime/questions.py` row wording that
  currently says Spanish "remains package-only". That phrase is stale after
  limited OpenAI-backed runtime promotion. Prefer: "Spanish aliases are
  package-owned query metadata; runtime Spanish output is profile/provider
  gated separately."
- In the `Coverage Implications` localization bullet, add the
  `localizedTitles.es` / `localizedPurposes.es` `2/27` counts next to alias
  counts. Keep the OpenAI-only runtime boundary and live-acceptance caveat.

Tertiary target:

- `README.md`

Likely edits:

- Under the entrypoints section, add an example:
  `.\.venv\Scripts\ai-presenter entrypoints --package ringcentral-video --language es`
- Mention that this inspects package-local display metadata and marks localized
  versus fallback output. It does not validate runtime voice/provider support.
- Under localization report examples, mention the optional title/purpose counts
  are informational and separate from `--require-complete`.
- Keep the existing Spanish runtime note, but ensure it does not imply local
  SAPI/Piper or live acceptance.

Do not edit source or tests for a documentation-only implementation unless the
docs update uncovers an actual behavior bug.

## Existing Code and Test Anchors

Use these anchors when implementing the docs update:

- `src/ai_presenter/packages/models.py:53` and `:54` define
  `localizedTitles` and `localizedPurposes`.
- `src/ai_presenter/packages/models.py:63` and `:68` expose
  `title_for_language()` and `purpose_for_language()` fallback behavior.
- `src/ai_presenter/packages/localization_status.py:86` to `:99` counts
  entrypoint aliases, localized titles, and localized purposes.
- `src/ai_presenter/packages/localization_status.py:138` to `:181` renders the
  optional report counts.
- `src/ai_presenter/cli.py:252` to `:296` owns `entrypoints --language`,
  including localized/fallback source markers.
- `src/ai_presenter/cli.py:299` to `:317` owns `localization-report`; it does
  not load or validate runtime voice providers.
- `src/ai_presenter/cli.py:515` to `:551` shows the separate
  `doctor --localization-language` path.
- `tests/unit/test_cli.py:550` to `:568` asserts the Spanish report counts,
  including `localizedTitles.es present on 2/27 entrypoints` and
  `localizedPurposes.es present on 2/27 entrypoints`.
- `tests/unit/test_cli.py:658` to `:738` asserts `entrypoints --language`
  localized/fallback output and protects the no-runtime-voice-validation
  boundary.
- `tests/unit/test_cli.py:1498` to `:1521`, `:1524` to `:1588`, and `:1591` to
  `:1622` cover the diagnostics boundary between package localization language,
  unsupported package-only languages, and OpenAI-backed Spanish runtime support.
- `packages/ringcentral-video.yaml:46` to `:49` and `:104` to `:107` are the
  only current Spanish localized title/purpose seeds.

## Verification Commands

For a docs-only implementation, recommended verification:

```powershell
.\.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language es
.\.venv\Scripts\ai-presenter entrypoints --package ringcentral-video --language es
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_cli.py::test_localization_report_outputs_complete_spanish_package tests\unit\test_cli.py::test_entrypoints_language_inspects_ringcentral_localized_and_fallback_copy tests\unit\test_cli.py::test_entrypoints_language_uses_package_local_metadata_without_runtime_voice_validation tests\unit\test_cli.py::test_doctor_rejects_package_only_language_after_complete_localization tests\unit\test_cli.py::test_doctor_openai_profile_accepts_spanish_runtime_language
```

If README examples are touched, also run:

```powershell
rg -n "localizedTitles|localizedPurposes|entrypoints --package ringcentral-video --language|Spanish|package-local|runtime" README.md docs\knowledge\language-lifecycle.md docs\knowledge\ringcentral-video\source-index.md
```

No full test suite should be required for copy-only docs, but the focused CLI
tests are a useful guard because these docs describe exact command behavior.

## Risks

- The biggest documentation risk is making `2/27` sound like Spanish package
  localization is incomplete. It is only the optional entrypoint display
  metadata count; required demo narration and Q&A localization are complete.
- The second biggest risk is implying that package-local language keys prove
  runtime voice or provider support. They do not. Runtime Spanish support is
  limited to OpenAI-backed speech profiles.
- `entrypoints --language` should be documented as inspection, not a preflight
  command. It intentionally avoids runtime voice/provider validation.
- Avoid saying Spanish local SAPI/Piper is supported, asset-ready, or accepted.
  Current docs should keep those as future work.
- Avoid saying OpenAI-backed Spanish support is live RingCentral Video
  acceptance. It is runtime-selectable with the OpenAI example profile; live
  acceptance remains separate evidence.
- Do not stage `.coverage`; it is already modified in the working tree and is
  unrelated generated state.

## Recommended Implementation Summary

Implement as a documentation-only patch:

1. Update `docs/knowledge/language-lifecycle.md` with an entrypoint display
   metadata subsection, optional-report semantics, `entrypoints --language`
   inspection guidance, Spanish `2/27` current state, and explicit claims to
   avoid.
2. Update `docs/knowledge/ringcentral-video/source-index.md` to include the
   `2/27` display-metadata counts and remove stale "Spanish remains
   package-only" phrasing.
3. Optionally update `README.md` with a compact operator example for
   `entrypoints --language es` and a reminder that report display counts are
   informational.

Keep the change out of source, tests, package YAML, and git staging unless a
future implementation cycle explicitly broadens scope.
