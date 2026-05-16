# Cycle 143 Review: Entrypoints Language Inspection Docs

Date: 2026-05-17
Cycle: 143
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`
Scope: Review of current Cycle143 diff for `README.md`,
`docs/knowledge/language-lifecycle.md`, `tests/unit/test_cli.py`, and
`docs/agent-handoffs/cycle-143-*.md`. This review writes only this handoff.

## Findings

### P2 - README still omits the alias-normalization behavior promised by the Cycle143 handoff

`README.md:53-59` explains only the `--language es` path. It says that this
input prints `Language: es` and describes localized/fallback markers, but it
does not tell README users that `Spanish` and `es-MX` normalize to the same
package key for inspection. That misses the acceptance target in
`docs/agent-handoffs/cycle-143-demand-analysis.md:48-49` and
`docs/agent-handoffs/cycle-143-demand-analysis.md:149-151`, which explicitly
asks README users to understand why `Spanish` or `es-MX` still prints
`Language: es`.

The new docs test does not catch the gap: `tests/unit/test_cli.py:616-628`
checks only the `entrypoints --package ringcentral-video --language es`
README command and shared marker/boundary phrases. It never requires the README
to mention `Spanish` or `es-MX`.
The later implementation handoff repeats the same README contract shape at
`docs/agent-handoffs/cycle-143-implementation.md:88-109`: the README contract
mentions only `--language es`, while alias normalization is documented under
the lifecycle contract instead.

Recommendation: add one README sentence near the entrypoints example, such as
"Known aliases such as `Spanish` and `es-MX` normalize to package key `es`, so
those inputs also print `Language: es`." If the docs guard remains, extend it
to check that README-specific alias promise rather than only the `es` example.

### P2 - Cycle143 handoffs conflict over whether test edits are in scope

The handoffs give future agents incompatible instructions. The demand analysis
says to avoid adding tests (`docs/agent-handoffs/cycle-143-demand-analysis.md:120-121`),
says not to edit tests (`docs/agent-handoffs/cycle-143-demand-analysis.md:126`),
and makes "No source, tests..." an acceptance criterion
(`docs/agent-handoffs/cycle-143-demand-analysis.md:164-165`). The risk scan
also warns against requiring test edits for wording-only changes
(`docs/agent-handoffs/cycle-143-risk-scan.md:195-208`). But the technical scan
then instructs the implementer to add a focused docs guard in
`tests/unit/test_cli.py` (`docs/agent-handoffs/cycle-143-technical-scan.md:116-118`)
and includes that file in final hygiene
(`docs/agent-handoffs/cycle-143-technical-scan.md:199-203`).

The current diff follows the technical scan and modifies
`tests/unit/test_cli.py`, so the same Cycle143 packet makes the test edit look
both required and forbidden. That will make later review and cleanup ambiguous,
especially because the risk scan identified doc-test expansion as a risk.
The implementation handoff preserves the ambiguity: it records the added
`tests/unit/test_cli.py` guard at
`docs/agent-handoffs/cycle-143-implementation.md:57-66`, then lists
`tests/unit/test_cli.py` under "Do not change" at
`docs/agent-handoffs/cycle-143-implementation.md:173-182`.

Recommendation: reconcile the handoffs. Either keep Cycle143 docs-only and
remove the test-edit instruction/current test change, or explicitly amend the
demand and risk handoffs to allow a lightweight docs guard.

### P3 - The new docs guard is prose-brittle while underchecking the actual overclaim risk

`tests/unit/test_cli.py:620-628` requires both README and the lifecycle doc to
contain exact prose fragments such as `display-source labels only`,
`not evidence of runtime Spanish readiness`, `matcher expansion`, and
`live RingCentral Video acceptance`. That makes harmless copy edits, shorter
README wording, or lifecycle rephrasing fail even when the docs still preserve
the correct contract. At the same time, `tests/unit/test_cli.py:630-633` bans
only one exact old overclaim phrase, so a differently worded runtime overclaim
could still pass.

Recommendation: if the test stays, make it less tied to duplicated prose.
Prefer one durable exact-contract check in `docs/knowledge/language-lifecycle.md`
plus a lighter README check for the command, alias note, and an explicit
runtime/provider/matcher/live boundary. The existing CLI behavior tests already
verify the real marker output and runtime-voice isolation.

## Non-Findings

- No new durable-doc overclaim found for runtime Spanish readiness, provider
  compatibility, local SAPI/Piper assets, controller/demo execution, or live
  RingCentral Video acceptance. `README.md:57-59` and
  `docs/knowledge/language-lifecycle.md:83-86` explicitly preserve those
  boundaries.
- No stale count issue found in this diff. The focused count sentinel passed,
  and the lifecycle still describes optional display metadata as partial at
  `docs/knowledge/language-lifecycle.md:131-133`.
- No issue found with optional `localizedTitles.<lang>` or
  `localizedPurposes.<lang>` being treated as required. The lifecycle keeps
  them outside `--require-complete` at `docs/knowledge/language-lifecycle.md:39-41`.
- No query-routing expansion claim found. The lifecycle keeps display metadata
  out of matching candidates and provider/runtime surfaces at
  `docs/knowledge/language-lifecycle.md:50-58`.

## Verification

Focused tests:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_cli.py::test_package_language_alias_normalization_is_documented tests\unit\test_cli.py::test_entrypoints_language_marker_contract_is_documented tests\unit\test_cli.py::test_entrypoints_language_inspects_ringcentral_localized_and_fallback_copy tests\unit\test_cli.py::test_entrypoints_language_normalizes_spanish_alias_for_display_metadata tests\unit\test_cli.py::test_entrypoints_language_uses_package_local_metadata_without_runtime_voice_validation tests\unit\test_material_packages.py::test_ringcentral_spanish_display_metadata_counts_match_durable_docs tests\unit\test_material_packages.py::test_entrypoint_localized_title_and_purpose_do_not_affect_match_candidates tests\unit\test_questions.py::test_ringcentral_spanish_display_metadata_is_not_part_of_match_candidates tests\unit\test_questions.py::test_ringcentral_spanish_display_metadata_fragments_do_not_create_matches
```

Result: `10 passed in 3.02s`.

Whitespace check:

```powershell
git diff --check -- README.md docs\knowledge\language-lifecycle.md tests\unit\test_cli.py
```

Result: exit code `0`; PowerShell printed only the existing LF-to-CRLF working
copy warnings for the three changed files.

Scope check before writing this review file:

```powershell
git status --short
```

Result:

```text
 M .coverage
 M README.md
 M docs/knowledge/language-lifecycle.md
 M tests/unit/test_cli.py
?? docs/agent-handoffs/cycle-143-demand-analysis.md
?? docs/agent-handoffs/cycle-143-risk-scan.md
?? docs/agent-handoffs/cycle-143-technical-scan.md
```

Expected additional final status entry after this review is
`?? docs/agent-handoffs/cycle-143-review.md`. A concurrent
`?? docs/agent-handoffs/cycle-143-implementation.md` appeared while this review
was being finalized and was reviewed for the findings above.

## Main-Session Resolution

All findings were addressed after this review:

- README now states that known aliases such as `Spanish` and `es-MX` normalize
  to package key `es`, so those inputs also print `Language: es`.
- Cycle143 handoffs now describe the scope as documentation-focused, with one
  acceptable docs guard in `tests/unit/test_cli.py`; behavior tests and source
  changes remain out of scope.
- The docs guard now checks README-specific alias wording and lifecycle-specific
  marker-contract wording separately, and bans a small set of runtime-support
  overclaim patterns instead of only one exact removed sentence.

Post-resolution focused verification:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_cli.py::test_package_language_alias_normalization_is_documented tests\unit\test_cli.py::test_entrypoints_language_marker_contract_is_documented tests\unit\test_cli.py::test_entrypoints_language_inspects_ringcentral_localized_and_fallback_copy tests\unit\test_cli.py::test_entrypoints_language_normalizes_spanish_alias_for_display_metadata tests\unit\test_cli.py::test_entrypoints_language_uses_package_local_metadata_without_runtime_voice_validation
```

Expected result: passing focused docs/CLI guard.
