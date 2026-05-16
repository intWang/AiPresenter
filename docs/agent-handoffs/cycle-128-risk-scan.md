# Cycle 128 Risk Scan: Spanish Runtime Promotion

Date: 2026-05-16
Scope: risk scan only for enabling `--language es`. This file is the only
intended edit for this task. Do not stage or commit.

## Executive Boundary

Recommendation: no-go for simply enabling `--language es` by adding an alias or
choice value. Spanish package localization is complete, but runtime support is
still intentionally absent. A go decision requires a runtime-promotion change
set that owns voice normalization, provider routing, controller/demo UI, doctor
behavior, docs, tests, and acceptance evidence together.

The safe current state is:

- `localization-report --language es --require-complete` passes for package
  content.
- `doctor --require-localization --localization-language es` reports package
  localization OK and runtime language support FAIL.
- `demo --language es --dry-run`, `controller --language es --dry-run`, and
  `doctor --language es` reject before runtime with `Unsupported presenter
  language: es`.

## Inspected Surfaces

- Runtime language model: `src/ai_presenter/runtime/voice.py` currently defines
  `PresenterLanguage = Literal["en", "zh", "ja"]`, public choices for English,
  Chinese, Japanese, and no Spanish aliases. `validate_profile_voice()` only
  has provider rules for `zh`, `ja`, and the English/SAPI mismatch case.
- Demo/controller CLI paths: `src/ai_presenter/cli.py` resolves
  `PresenterVoiceSettings` before demo/controller/doctor execution. That keeps
  `--language es` from reaching desktop automation.
- Controller UI path: `src/ai_presenter/runtime/controller.py` builds its
  language dropdown from `PRESENTER_LANGUAGE_CHOICES` and validates voice before
  Start or question submit.
- Provider routing: OpenAI speech is generic but uses one configured voice;
  Piper is fixed to `en_US-lessac-medium`; Windows SAPI readiness checks only
  Zira and Huihui. There is no Spanish SAPI/Piper asset contract.
- Package-local docs: `README.md` and `docs/knowledge/language-lifecycle.md`
  explicitly say Spanish localization is complete while `--language es` remains
  unsupported until promotion.
- Package localization: `packages/ringcentral-video.yaml` includes Spanish
  `localizedText`, `localizedQuestions`, `localizedAnswers`, and
  `questionAliases.es`.
- Tests: focused coverage exists for Spanish localization success, runtime
  language rejection, doctor package-only language boundaries, accent-folding
  diagnostics, controller voice readiness, and provider validation.

## Current Verification Signals

Commands run from `C:\Users\rcadmin\Documents\Repos\AiPresenter`:

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language es --require-complete
```

Result: exit `0`; `51/51` demo steps, `12/12` Q&A questions, `12/12` Q&A
answers; `questionAliases.es` on `26/27` entrypoints with `69` aliases.

```powershell
.\.venv\Scripts\ai-presenter.exe doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --require-localization --localization-language es
```

Result: exit `1`; `[OK] localization: required es localization complete` and
`[FAIL] runtime language support: localization language es is package-only
here; presenter runtime does not support --language es`.

```powershell
.\.venv\Scripts\ai-presenter.exe demo --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo --language es --dry-run
.\.venv\Scripts\ai-presenter.exe controller --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo --language es --dry-run
.\.venv\Scripts\ai-presenter.exe doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo --language es
```

Result: all exit `1` with `Invalid value: Unsupported presenter language: es`.

```powershell
.\.venv\Scripts\ai-presenter.exe voices --profile ringcentral-video-bind-speaker
```

Result: catalog lists English, Chinese, Japanese only. The bind-speaker profile
supports English via `windows-sapi-en`, Chinese via `windows-sapi-zh`, and marks
Japanese unsupported without OpenAI.

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_voice.py tests\unit\test_cli.py tests\unit\test_diagnostics.py tests\unit\test_controller.py tests\unit\test_controller_view_model.py tests\unit\test_material_packages.py
```

Result: `282 passed in 44.30s`.

## Go/No-Go Boundaries

Go only if all of these are true in the same promotion:

- `PresenterLanguage`, labels, aliases, and `PRESENTER_LANGUAGE_CHOICES` add
  Spanish deliberately.
- `render_narration_text()` selects `localizedText.es`, and non-localized
  fallback behavior is explicitly acceptable or blocked.
- `validate_profile_voice()` has a Spanish provider rule. The rule should not
  silently allow fake, English-only Piper, or English/Chinese SAPI routes to
  speak Spanish.
- `resolve_speech_provider_name()` and `create_provider_registry()` route
  Spanish to a real, accepted speech provider.
- `check_voice_asset_availability()` has Spanish asset checks if local speech is
  supported, or explicitly returns not-applicable only for OpenAI.
- CLI `demo`, `controller`, `doctor`, and `voices` outputs describe Spanish
  accurately.
- Controller language dropdown exposes Spanish only after the runtime route is
  valid for the selected profile.
- Docs are updated from "package-local only" to "runtime-supported under these
  profiles/providers" without implying live acceptance beyond evidence.
- Manual or automated acceptance proves at least one Spanish demo route in the
  target environment.

No-go if any of these remain true:

- Spanish is added only to aliases or UI choices.
- `--language es` can run with `fake`, `piper` English assets, or English/Chinese
  SAPI by fallback.
- `voices --profile ...` lists Spanish as supported without asset/provider
  evidence.
- `doctor --require-localization --localization-language es` loses the separate
  runtime language support boundary before runtime support is complete.
- Docs imply live RingCentral Spanish acceptance from package localization tests
  alone.

## Must-Have Negative Tests

Keep or add these before promotion:

- `PresenterVoiceSettings(language="es")` rejects until the promotion cycle
  intentionally adds Spanish.
- `demo --language es --dry-run` and `controller --language es --dry-run` do not
  call runtime when Spanish is unsupported.
- `doctor --language es` rejects as an invalid runtime language while
  unsupported.
- `doctor --require-localization --localization-language es` can still report
  package localization separately from runtime language support.
- If Spanish is promoted through OpenAI only, Spanish with fake, Piper
  `en_US-lessac-medium`, `windows-sapi-en`, and `windows-sapi-zh` fails early.
- If Spanish local speech is promoted, missing Spanish SAPI/Piper assets block
  Start and Submit in controller view-model/readiness tests.
- Spanish Q&A prompts and aliases remain Q&A-first for risky controls such as
  recording, notes/transcript, invite, share, mute/unmute, and leave.
- Spanish accent-insensitive matching does not become fuzzy matching,
  transliteration, stemming, or cross-language semantic matching.

## Rollback Concerns

- Do not stage `.coverage`; it is already modified in this workspace.
- Runtime promotion is not cleanly reversible if docs, tests, and UI are changed
  without a feature boundary. Roll back by removing Spanish from
  `PRESENTER_LANGUAGE_CHOICES`, language aliases/labels, provider routing, voice
  asset checks, and any docs that claim runtime support.
- If Spanish OpenAI speech is accepted first, keep local profiles unsupported
  rather than letting them fall through to English assets.
- Preserve `--localization-language` for package inspection even after Spanish
  runtime support lands; it prevents future package-local languages from being
  mistaken for runnable voices.
- Acceptance evidence should live in the runbook/knowledge evidence trail, not
  only in test output or this handoff.

## Suggested Promotion Verification

Before any Spanish runtime merge, run:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_voice.py tests\unit\test_cli.py tests\unit\test_diagnostics.py tests\unit\test_controller.py tests\unit\test_controller_view_model.py tests\unit\test_material_packages.py tests\unit\test_questions.py
.\.venv\Scripts\ai-presenter.exe voices --profile <spanish-supported-profile>
.\.venv\Scripts\ai-presenter.exe doctor --profile <spanish-supported-profile> --package ringcentral-video --flow meeting-control-map-demo --language es --require-localization
.\.venv\Scripts\ai-presenter.exe demo --profile <spanish-supported-profile> --package ringcentral-video --flow meeting-control-map-demo --language es --dry-run
.\.venv\Scripts\ai-presenter.exe controller --profile <spanish-supported-profile> --package ringcentral-video --flow meeting-control-map-demo --language es --dry-run
.\.venv\Scripts\ai-presenter.exe doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo --language es
git diff --check
git status --short
```

Expected after promotion: supported Spanish profile passes; unsupported local
profiles still fail with explicit provider/asset reasons; docs and tests do not
claim live Spanish acceptance until a real acceptance run records it.
