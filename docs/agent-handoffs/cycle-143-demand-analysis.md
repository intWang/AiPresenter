# Cycle 143 Demand Analysis: Entrypoints Language Inspection Docs Alignment

Date: 2026-05-17
Cycle: 143
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`
Scope: demand analysis only. This file is the only intended edit for this
analysis slice. Do not edit source code, tests, package YAML, README,
language lifecycle docs, generated artifacts, staging, commits, or pre-existing
dirty files from this slice.

Worktree note: `.coverage` was already modified while this analysis was
prepared. Treat it as unrelated concurrent state. Do not revert, stage, or
claim ownership of it from this doc-only slice.

## Context

Cycle142 added focused CLI tests for `entrypoints --language` Spanish package
inspection. The guard proves that `es`, `Spanish`, and `es-MX` all resolve to
the package key `es`, print `Language: es`, and show localized/fallback source
markers for optional RingCentral Video entrypoint display metadata.

That behavior is intentionally package-local. It is about inspecting
`localizedTitles.<lang>` and `localizedPurposes.<lang>` display metadata after
language-key normalization. It is not runtime voice support, provider
compatibility, controller/demo execution support, query-routing eligibility, or
live RingCentral Video acceptance.

Current durable docs already point in this direction:

- `README.md` has a package-local Spanish entrypoint inspection example and
  says it does not validate runtime voice support, providers, local SAPI/Piper
  assets, controller/demo execution, or live acceptance.
- `docs/knowledge/language-lifecycle.md` has an "Entrypoint display metadata
  inspection" lifecycle gate that describes `entrypoints --language <lang>` as
  package-local inspection with `localized` and `fallback` source markers.

The remaining Cycle143 value is alignment and precision: README and the
language lifecycle should describe the Cycle142 CLI inspection contract using
the same marker-based vocabulary, including Spanish alias normalization, while
avoiding any wording that could be read as runtime support evidence.

## User Value

- Maintainers get one clear interpretation of `entrypoints --language`: it is a
  package-local display metadata audit surface.
- Future agents are less likely to turn localized/fallback marker tests into
  runtime-language, provider, matcher, or live-acceptance claims.
- README users can run the same inspection examples covered by Cycle142 tests
  and understand why `Spanish` or `es-MX` still prints `Language: es`.
- The language lifecycle remains the durable boundary document for separating
  package metadata inspection from runtime promotion.
- Documentation stays stable around copy edits because the important contract
  is source markers and resolved package keys, not exact Spanish prose.

## Exact Recommended Scope

Implement a docs-only alignment pass limited to durable documentation.

Recommended files:

- `README.md`
- `docs/knowledge/language-lifecycle.md`

Recommended README edits:

- In the package inspection section, add one or two adjacent examples showing
  that Spanish aliases can be inspected through the same package-local surface,
  for example:
  - `entrypoints --package ringcentral-video --language es`
  - `entrypoints --package ringcentral-video --language es-MX`
- State that known presenter-language aliases such as `Spanish` and `es-MX`
  normalize to the package key `es` for inspection, so the CLI header prints
  `Language: es`.
- Name the visible marker contract: entrypoint title and purpose rows can show
  `localized` when package-local display metadata exists and `fallback` when
  canonical package copy is shown.
- Keep the existing runtime boundary, but tighten it around this command:
  `entrypoints --language` does not validate runtime voice support, providers,
  local SAPI/Piper/OpenAI compatibility, controller/demo execution, matcher
  eligibility, or live RingCentral Video acceptance.

Recommended language lifecycle edits:

- In lifecycle gate 3, make the first sentence explicitly call this
  "package-local marker-based display metadata inspection."
- Keep `localizedTitles.<lang>` and `localizedPurposes.<lang>` framed as
  optional display metadata for answer rendering and CLI inspection.
- Preserve the existing list of non-effects: matching candidates, alias
  ordering, Q&A precedence, safety gating, controller interrupts, provider
  routing, voice assets, and live acceptance.
- Add or tighten a note that Cycle142-style CLI tests prove only:
  - language input normalization to a package key;
  - the `Language: <key>` header;
  - localized/fallback source markers for title and purpose fields.
- Make clear that these tests do not prove runtime support. If Spanish runtime
  support is mentioned elsewhere, keep its existing separate OpenAI-profile
  boundary and do not conflate it with entrypoint inspection.
- Keep optional Spanish `localizedTitles.es` and `localizedPurposes.es`
  described as partial, not as required localization completeness.

Preferred style:

- Use the words `package-local`, `display metadata`, `localized/fallback
  markers`, and `resolved package key` consistently.
- Avoid saying `entrypoints --language es` "supports Spanish" without
  qualifying that the support is package-local inspection only.
- Avoid adding long historical Cycle142 narrative to README; reserve durable
  lifecycle detail for `docs/knowledge/language-lifecycle.md`.

## Approaches Considered

Recommended: a small durable-docs alignment in README and the language
lifecycle. This gives users a concise command-level explanation in README and a
precise lifecycle boundary for future maintainers.

Acceptable but weaker: update only README. This helps command users but leaves
the durable lifecycle wording less directly tied to the Cycle142 marker-based
test contract.

Avoid: changing CLI output or adding behavior tests. Cycle142 already owns the
runtime behavior guard, and current behavior is the thing being documented. A
small docs guard test is acceptable if it prevents README/lifecycle wording from
drifting back into runtime-support claims.

## Out-of-Scope Boundaries

- Do not edit source code.
- Do not edit behavior tests. A focused docs guard in `tests/unit/test_cli.py`
  is acceptable if it only checks README/lifecycle wording.
- Do not edit package YAML.
- Do not change CLI output formatting, language normalization, source marker
  strings, package loading, localization status, matcher behavior, Q&A
  precedence, aliases, safety gating, providers, profiles, voice assets, demo
  flows, controller options, or runtime language support.
- Do not expand Spanish optional entrypoint display metadata beyond the current
  partial state.
- Do not make `localizedTitles.<lang>` or `localizedPurposes.<lang>` part of
  `localization-report --require-complete`.
- Do not claim local SAPI/Piper Spanish readiness, OpenAI profile readiness
  beyond the existing documented runtime boundary, or live RingCentral Video
  acceptance.
- Do not touch generated artifacts such as `.coverage`.
- Do not stage or commit unless a later implementation task explicitly asks for
  it.

## Acceptance Criteria

- The implementation diff is documentation-focused and normally limited to
  `README.md`, `docs/knowledge/language-lifecycle.md`, and at most one focused
  docs guard in `tests/unit/test_cli.py`.
- README includes package-local `entrypoints --language` wording that names the
  localized/fallback marker contract.
- README makes clear that Spanish aliases such as `Spanish` and `es-MX`
  normalize to the package key `es` for CLI inspection and therefore print
  `Language: es`.
- README explicitly says this inspection does not validate runtime voice
  support, providers, controller/demo execution, matcher eligibility, or live
  RingCentral Video acceptance.
- The language lifecycle describes entrypoint display metadata inspection as
  package-local marker-based display metadata inspection.
- The language lifecycle says Cycle142-style tests prove resolved package keys
  and localized/fallback markers only, not runtime support.
- The existing separate Spanish runtime boundary remains intact: any OpenAI
  speech support language is described separately from entrypoint inspection,
  and local SAPI/Piper/live acceptance are not overclaimed.
- Spanish optional entrypoint display metadata remains documented as partial,
  not a `--require-complete` requirement.
- No source, behavior tests, package YAML, generated artifacts, localization
  counts, or unrelated dirty files change.
- Final hygiene checks:

```powershell
git diff -- README.md docs\knowledge\language-lifecycle.md tests\unit\test_cli.py
git diff --check -- README.md docs\knowledge\language-lifecycle.md tests\unit\test_cli.py
git status --short
```

Expected status should show only intended docs changes plus any pre-existing
unrelated dirty artifacts.

## Implementation Handoff Prompt

```text
Implement Cycle143's docs-only entrypoints language inspection alignment in
C:\Users\rcadmin\Documents\Repos\AiPresenter.

Context:
- Cycle142 added CLI tests proving:
  - entrypoints --language es
  - entrypoints --language Spanish
  - entrypoints --language es-MX
  all resolve to Language: es for RingCentral Video package inspection and show
  localized/fallback markers for optional entrypoint title/purpose display
  metadata.
- This is package-local display metadata inspection only. It is not runtime
  voice support, provider compatibility, controller/demo acceptance, matcher
  eligibility, or live RingCentral Video acceptance.

Scope:
- Docs only.
- Prefer limiting changes to:
  - README.md
  - docs/knowledge/language-lifecycle.md

README requirements:
- In the entrypoints/package inspection section, show or mention package-local
  Spanish inspection with --language es and an alias such as --language es-MX
  or --language Spanish.
- Explain that known aliases such as Spanish and es-MX normalize to the package
  key es for inspection, so the command prints Language: es.
- Explain that title and purpose rows use localized/fallback source markers:
  localized means package-local display metadata exists; fallback means
  canonical package copy is shown.
- State that entrypoints --language does not validate runtime voice support,
  providers, local SAPI/Piper/OpenAI compatibility, controller/demo execution,
  matcher eligibility, or live RingCentral Video acceptance.

Language lifecycle requirements:
- In the Entrypoint display metadata inspection gate, describe the command as
  package-local marker-based display metadata inspection.
- Keep localizedTitles.<lang> and localizedPurposes.<lang> framed as optional
  display metadata for answer rendering and inspection.
- Preserve the non-effects list: matching candidates, alias ordering, Q&A
  precedence, safety gating, controller interrupts, provider routing, voice
  assets, and live acceptance.
- Add or tighten wording that Cycle142-style CLI tests prove only resolved
  package keys, the Language: <key> header, and localized/fallback title and
  purpose markers.
- Do not conflate that inspection with runtime support. If Spanish runtime
  support is mentioned, keep the existing separate OpenAI-profile boundary and
  do not imply local SAPI/Piper or live acceptance readiness.
- Keep optional Spanish localizedTitles.es and localizedPurposes.es documented
  as partial and not part of --require-complete.

Boundaries:
- Do not edit source code, tests, package YAML, generated artifacts, providers,
  profiles, voice assets, matcher logic, aliases, Q&A, demo flows, controller
  options, localization counts, or runtime language support.
- Do not expand Spanish optional display metadata.
- Do not make entrypoint display metadata part of localization-report
  --require-complete.
- Do not touch unrelated dirty files such as .coverage.
- Do not stage or commit unless explicitly asked.

Verification:
- Review the docs diff:
  git diff -- README.md docs\knowledge\language-lifecycle.md
- Check whitespace:
  git diff --check -- README.md docs\knowledge\language-lifecycle.md
- Confirm worktree scope:
  git status --short

Acceptance:
- README and docs/knowledge/language-lifecycle.md consistently describe
  entrypoints --language as package-local marker-based display metadata
  inspection.
- The docs mention Spanish alias normalization to Language: es for inspection.
- The docs explain localized/fallback markers for title and purpose display
  fields.
- The docs explicitly avoid treating this command or the Cycle142 tests as
  runtime voice support, provider compatibility, matcher eligibility,
  controller/demo acceptance, or live RingCentral Video acceptance.
- No source, tests, package YAML, generated artifacts, localization counts, or
  unrelated dirty files are changed.
```
