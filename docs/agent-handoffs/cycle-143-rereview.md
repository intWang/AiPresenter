# Cycle 143 Re-Review: Entrypoints Language Inspection Docs

Date: 2026-05-17
Cycle: 143
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`
Scope: focused re-review of the current Cycle143 diff only:
`README.md`, `docs/knowledge/language-lifecycle.md`,
`tests/unit/test_cli.py`, and `docs/agent-handoffs/cycle-143-*.md`.
This re-review writes only this handoff.

## Findings

No findings.

The prior review findings appear resolved in the current diff:

- README now documents Spanish alias normalization. `README.md:60-61` says
  `Spanish` and `es-MX` normalize to package key `es` and print
  `Language: es`.
- README no longer presents the entrypoints inspection example as runtime
  Spanish support. `README.md:52-59` frames the command as package-local
  display metadata inspection and explicitly excludes runtime readiness,
  matcher expansion, provider availability, local SAPI/Piper assets,
  controller/demo execution, and live RingCentral Video acceptance.
- The language lifecycle now carries the Spanish marker contract at
  `docs/knowledge/language-lifecycle.md:65-68` and preserves the runtime
  boundary at `docs/knowledge/language-lifecycle.md:83-86`.
- The handoffs now allow a single documentation guard while keeping behavior
  tests out of scope. The clearest contract is in
  `docs/agent-handoffs/cycle-143-demand-analysis.md:120-129` and
  `docs/agent-handoffs/cycle-143-implementation.md:171-183`.
- The docs guard is narrower than the first review version: it checks README
  alias wording and lifecycle marker wording separately, and bans multiple
  README runtime-overclaim patterns in `tests/unit/test_cli.py:616-647`.

## Residual Risks

- The docs guard remains phrase-based. That is acceptable for this cycle
  because the guarded phrases are the durable boundary language, but future
  harmless copy edits may need matching updates in
  `tests/unit/test_cli.py:620-638`.
- `docs/agent-handoffs/cycle-143-risk-scan.md` still uses broad shorthand such
  as "Test changes" being out of scope at lines `63-67` and a broad no-go at
  lines `269-270`. The same risk scan softens that at `199-202`, and the
  demand/implementation/experience handoffs clarify that one docs guard is
  acceptable. A future reader who skims only the no-go list could still need
  that context.
- This re-review did not run the full test suite or live RingCentral checks.
  That matches the documentation-focused scope; runtime acceptance remains out
  of scope.

## Verification

Focused docs/CLI/package/matcher sentinels:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_cli.py::test_package_language_alias_normalization_is_documented tests\unit\test_cli.py::test_entrypoints_language_marker_contract_is_documented tests\unit\test_cli.py::test_entrypoints_language_inspects_ringcentral_localized_and_fallback_copy tests\unit\test_cli.py::test_entrypoints_language_normalizes_spanish_alias_for_display_metadata tests\unit\test_cli.py::test_entrypoints_language_uses_package_local_metadata_without_runtime_voice_validation tests\unit\test_material_packages.py::test_ringcentral_spanish_display_metadata_counts_match_durable_docs tests\unit\test_material_packages.py::test_entrypoint_localized_title_and_purpose_do_not_affect_match_candidates tests\unit\test_questions.py::test_ringcentral_spanish_display_metadata_is_not_part_of_match_candidates tests\unit\test_questions.py::test_ringcentral_spanish_display_metadata_fragments_do_not_create_matches
```

Result: `10 passed in 2.63s`.

Whitespace check:

```powershell
git diff --check -- README.md docs\knowledge\language-lifecycle.md tests\unit\test_cli.py docs\agent-handoffs\cycle-143-demand-analysis.md docs\agent-handoffs\cycle-143-risk-scan.md docs\agent-handoffs\cycle-143-technical-scan.md docs\agent-handoffs\cycle-143-implementation.md docs\agent-handoffs\cycle-143-experience.md docs\agent-handoffs\cycle-143-review.md
```

Result: exit code `0`; PowerShell printed only existing LF-to-CRLF working copy
warnings for the three tracked changed files.

Post-write handoff whitespace check:

```powershell
git diff --check -- docs\agent-handoffs\cycle-143-rereview.md
```

Result: exit code `0`.

Status before writing this re-review:

```text
 M .coverage
 M README.md
 M docs/knowledge/language-lifecycle.md
 M tests/unit/test_cli.py
?? docs/agent-handoffs/cycle-143-demand-analysis.md
?? docs/agent-handoffs/cycle-143-experience.md
?? docs/agent-handoffs/cycle-143-implementation.md
?? docs/agent-handoffs/cycle-143-review.md
?? docs/agent-handoffs/cycle-143-risk-scan.md
?? docs/agent-handoffs/cycle-143-technical-scan.md
```

Expected additional status entry after this handoff is
`?? docs/agent-handoffs/cycle-143-rereview.md`.

Final status after writing this handoff included that additional entry and no
unexpected source or test files beyond the pre-existing Cycle143 surface.
