# Cycle 123 Implementation: Language Lifecycle Guardrail

Date: 2026-05-16

## Scope

This cycle intentionally did not complete Spanish `meeting-control-map-demo`. Demand and technical scans recommended that package-local content slice, but the risk scan highlighted a more urgent boundary: once Spanish package coverage reaches `51/51`, operators may mistake package completeness for presenter runtime support.

Implemented a lifecycle guardrail first:

- Added durable language lifecycle documentation under `docs/knowledge/language-lifecycle.md`.
- Linked that document from `README.md` near the existing localization-report and doctor guidance.
- Added a diagnostics regression test proving that a package can be complete for `es` while the separate `runtime language support` diagnostic still fails.

## Behavior Locked

The new test builds a synthetic package with:

- `localizedText.es` for all demo steps;
- `localizedQuestions.es` for all Q&A questions;
- `localizedAnswers.es` for all Q&A answers.

Diagnostics must then report:

- `[OK] localization` with complete `es` package counts;
- `[FAIL] runtime language support` because presenter runtime still does not support `--language es`.

This is the future-proof case needed before Spanish package content becomes complete in the real RingCentral package.

## Verification

Focused verification:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_diagnostics.py::test_diagnostics_runtime_language_support_stays_separate_after_package_localization_complete tests\unit\test_diagnostics.py::test_diagnostics_require_localization_flags_package_only_runtime_language tests\unit\test_cli.py::test_doctor_require_localization_accepts_package_only_spanish_language
```

Result: `3 passed`.

Documentation checks:

```powershell
rg -n "Spanish is supported|Spanish supported|Spanish runtime supported|es is supported|runtime-ready|voice-ready|live-ready" README.md docs\knowledge\language-lifecycle.md
git diff --check -- README.md docs\knowledge\language-lifecycle.md tests\unit\test_diagnostics.py docs\agent-handoffs\cycle-123-*.md
```

The lifecycle document did not already exist before this cycle. `.coverage` remained unrelated generated drift and must stay unstaged.

## Next Handoff

Next implementation can safely complete Spanish `meeting-control-map-demo` as package-local content:

- expected Spanish package coverage: `29/51` -> `51/51`;
- expected `meeting-control-map-demo`: `0/22` -> `22/22`;
- Spanish `localization-report --require-complete` may pass once package content is complete;
- `doctor --require-localization --localization-language es` must still fail the separate runtime language support check;
- `demo --language es --dry-run` must still reject `Unsupported presenter language: es`.
