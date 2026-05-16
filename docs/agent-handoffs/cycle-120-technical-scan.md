# Cycle 120 Technical Scan: Localization Runtime Guard

Scope: technical scan only. This handoff is the only file changed by this subagent. Do not stage or commit from this scan.

## Baseline

Cycle 119 Spanish state is confirmed:

- `localization-report --package ringcentral-video --language es` reports `7/51` demo steps: `vbg-blur-demo 4/4`, `meeting-basics-demo 3/3`, and both long flows `0/22`.
- Spanish Q&A is `12/12` questions and `12/12` answers.
- Spanish aliases remain `questionAliases.es present on 1/27 entrypoints (3 aliases)`.
- Runtime Spanish remains unsupported: `demo --language es --dry-run` exits nonzero with `Unsupported presenter language: es`.

Focused baseline command run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_localization_status_reports_spanish_short_demo_wedges tests\unit\test_cli.py::test_localization_report_outputs_spanish_short_demo_wedges tests\unit\test_cli.py::test_demo_rejects_unknown_language_before_runtime
```

Result: `3 passed`.

## Scan Findings

`src/ai_presenter/packages/localization_status.py` already supports arbitrary package localization language keys. It does not depend on runtime voice language support, which is why Spanish package coverage can be reported today.

`src/ai_presenter/runtime/voice.py` supports only runtime presenter languages `en`, `zh`, and `ja`. `PresenterVoiceSettings(language="es")` raises `ValueError`, and CLI `demo`, `controller`, `voices`, and `doctor --language es` inherit that behavior.

`src/ai_presenter/runtime/diagnostics.py` already has `require_localization` and `localization_language`, but it does not explicitly report whether the localization language is a runnable runtime voice language. Direct diagnostics can check `localization_language="es"` today, but the CLI cannot pass Spanish through `doctor --language es` because `--language` is voice runtime input.

`src/ai_presenter/cli.py` currently passes `localization_language=voice.language if voice is not None else None`, so `doctor --require-localization` defaults to Chinese unless a valid runtime voice language is selected.

Package tests already cover Spanish coverage and the safety Q&A path without runtime Spanish. CLI tests already pin `demo --language es` as invalid. Diagnostics tests cover required localization for Chinese/Japanese and incomplete package localization, but not the package-localization/runtime-language distinction.

## Recommendation

Recommend the diagnostics guard as the smallest safe Cycle 120 implementation slice.

Why this slice:

- It addresses the main ambiguity after Spanish package progress: localized package content is not the same thing as runnable runtime Spanish.
- It avoids broad package edits and does not consume the next Spanish narration wedge.
- It is smaller and safer than the performance/index guard, which touches package model indexes, question matching, and diagnostics loops.
- It can be tested directly in diagnostics and through `doctor` without enabling Spanish runtime.

## Exact Semantics

Add a doctor-only package localization selector:

```text
doctor --localization-language es --require-localization
```

Do not change the meaning of `--language`; it remains the runtime presenter voice selector and must still reject `es`.

Suggested output semantics when Spanish is requested through the new localization selector:

```text
[FAIL] localization: required es localization incomplete: 7/51 demo steps, 12/12 Q&A questions, 12/12 Q&A answers
[FAIL] runtime language support: localization language es is package-only here; presenter runtime does not support --language es
```

The second check should be present whenever `--require-localization` is used with a localization language that is not accepted by `normalize_presenter_language`. It should be `FAIL`, not `WARN`, so a future fully localized Spanish package cannot make doctor exit `0` while runtime Spanish is still unavailable.

For supported runtime localization languages, include an `OK` check:

```text
[OK] runtime language support: localization language zh is recognized by the presenter runtime as Chinese
```

Keep provider/voice compatibility separate. This guard answers only "is this language in the runtime language catalog?" Existing `voice` diagnostics still handle profile/provider compatibility when `--language` or `--tone` is selected.

Expected CLI behavior:

- `doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --require-localization --localization-language es` exits `1` and prints both localization coverage and runtime support failure.
- `doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --require-localization --localization-language zh` exits `0` aside from any unrelated local RingCentral config warning.
- `doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --require-localization --language es` still exits before diagnostics with `Unsupported presenter language: es`.
- `demo --language es`, `controller --language es`, and `voices --language es` remain unsupported.
- `localization-report --language es` remains the package-only coverage report and should not gain runtime checks.

## File Map

Change:

- `src/ai_presenter/runtime/diagnostics.py`
  - Import `normalize_presenter_language`.
  - Add a helper such as `_diagnose_runtime_language_support(language: str) -> DiagnosticCheck`.
  - In `diagnose_configuration`, when `require_localization` is true, compute the existing localization language once and append both `_diagnose_required_localization(...)` and `_diagnose_runtime_language_support(...)`.
  - Do not construct `PresenterVoiceSettings` for unsupported languages.

- `src/ai_presenter/cli.py`
  - Add `localization_language: str | None = typer.Option(None, "--localization-language", help=...)` to `doctor`.
  - Pass `localization_language=localization_language or (voice.language if voice is not None else None)`.
  - Do not reuse `--language` for package-only languages.

Update tests:

- `tests/unit/test_diagnostics.py`
  - Add direct diagnostics test for `require_localization=True, localization_language="es"` on RingCentral package.
  - Assert localization check is `FAIL` with `required es localization incomplete` and `7/51 demo steps`.
  - Assert runtime language support check is `FAIL` and mentions `--language es`.
  - Add/extend supported-language test for `zh` or `ja` asserting runtime language support is `OK`.

- `tests/unit/test_cli.py`
  - Add doctor CLI test for `--localization-language es --require-localization`.
  - Assert exit `1`, localization `FAIL`, runtime language support `FAIL`, and no `Unsupported presenter language: es` Typer parse error.
  - Add doctor CLI test for `--localization-language zh --require-localization` preserving exit `0` with the RingCentral config discovery monkeypatch used by adjacent tests.
  - Keep `test_demo_rejects_unknown_language_before_runtime` unchanged.
  - Optionally add `doctor --language es` explicit regression if desired, but the existing demo rejection already pins runtime parsing.

No expected changes:

- `src/ai_presenter/runtime/voice.py`
- `src/ai_presenter/packages/localization_status.py`
- `packages/ringcentral-video.yaml`
- `src/ai_presenter/runtime/questions.py`
- `src/ai_presenter/packages/models.py`

## TDD Plan

Red first:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_diagnostics.py::test_diagnostics_require_localization_flags_package_only_runtime_language tests\unit\test_cli.py::test_doctor_require_localization_accepts_package_only_spanish_language
```

Expected red:

- Missing diagnostics runtime language support check.
- Missing `doctor --localization-language` option.

Green after implementation:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_diagnostics.py::test_diagnostics_require_localization_flags_package_only_runtime_language tests\unit\test_diagnostics.py::test_diagnostics_require_localization_reports_supported_runtime_language tests\unit\test_cli.py::test_doctor_require_localization_accepts_package_only_spanish_language tests\unit\test_cli.py::test_doctor_require_localization_passes_for_chinese_package tests\unit\test_cli.py::test_demo_rejects_unknown_language_before_runtime
```

Focused CLI verification:

```powershell
.\.venv\Scripts\ai-presenter.exe doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --require-localization --localization-language es
.\.venv\Scripts\ai-presenter.exe doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --require-localization --localization-language zh
.\.venv\Scripts\ai-presenter.exe demo --profile ringcentral-video --package ringcentral-video --flow meeting-basics-demo --language es --dry-run
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language es
```

Broader focused regression:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_diagnostics.py tests\unit\test_cli.py tests\unit\test_material_packages.py::test_ringcentral_localization_status_reports_spanish_short_demo_wedges tests\unit\test_questions.py::test_ringcentral_spanish_safety_questions_match_qas_without_runtime_spanish
```

Diff hygiene:

```powershell
git diff --check -- src\ai_presenter\runtime\diagnostics.py src\ai_presenter\cli.py tests\unit\test_diagnostics.py tests\unit\test_cli.py
git status --short
```

## Non-Goals

- Do not add Spanish to `PresenterLanguage`, `PRESENTER_LANGUAGE_CHOICES`, `_LANGUAGE_ALIASES`, or voice labels.
- Do not make `demo`, `controller`, or `voices` accept Spanish.
- Do not add Spanish narration, aliases, Q&A, or package route changes in this slice.
- Do not change localization report semantics.
- Do not start the performance/index guard in the same cycle.
