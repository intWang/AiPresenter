# Cycle 116 Technical Scan: Spanish Runtime vs Tone Expansion

Date: 2026-05-16
Scope: technical scan only. This handoff creates only this file and does not edit production code, tests, profiles, packages, coverage artifacts, or Codex home files.

## Verdict

The safest next implementation slice is a new tone alias that maps to an existing canonical tone. A new canonical tone type is still smaller than runtime Spanish, but it should be treated as a style-only runtime feature with focused tests.

Do not add runtime Spanish support as the next slice after Cycle 113's Spanish package seed. Spanish is currently a report-only package wedge: `es` has 0/51 localized demo narration steps, 1/12 localized Q&A questions, 1/12 localized Q&A answers, and `questionAliases.es` on 1/27 entrypoints with 3 aliases. Opening `PresenterVoiceSettings(language="es")` now would expose mixed English/Spanish runtime behavior unless a larger package and runtime readiness slice lands with it.

If product priority is Spanish, the safer Spanish-adjacent next slice is to expand package/report Spanish coverage first, especially the full Q&A safety set, while keeping runtime Spanish unsupported.

## Current State

| Area inspected | Current state | Scan note |
| --- | --- | --- |
| Runtime languages | `src/ai_presenter/runtime/voice.py` defines `PresenterLanguage = Literal["en", "zh", "ja"]`, labels, aliases, and public choices for English, Chinese, and Japanese. | Spanish is intentionally rejected today; `tests/unit/test_voice.py` and `tests/unit/test_cli.py` assert that `es` is unsupported. |
| Runtime tones | `src/ai_presenter/runtime/voice.py` defines `professional`, `conversational`, `concise`, `friendly`, `coach`, `formal`, `support`, and `careful`, with aliases and descriptions centralized in the same file. | Adding an alias to an existing tone is tiny. Adding a canonical tone is moderate but contained if style-only. |
| CLI | `src/ai_presenter/cli.py` resolves voice settings before `demo`, `controller`, `voices`, and `doctor`; `localization-report` accepts arbitrary language strings because it is package/report-only. | Spanish report support already exists; Spanish runtime support does not. |
| Controller | `src/ai_presenter/runtime/controller.py` builds language and tone selectors from `PRESENTER_LANGUAGE_CHOICES` and `PRESENTER_TONE_CHOICES`; `controller_view_model.py` renders labels through shared helpers. | New canonical tones flow to the UI via constants, but tests still need label and option coverage. |
| Diagnostics | `src/ai_presenter/runtime/diagnostics.py` uses `PresenterVoiceSettings` for voice checks and `build_localization_status()` for `--require-localization`. | Runtime Spanish plus incomplete package Spanish would make `doctor --require-localization` fail for the right reason, but ordinary `demo`/`controller` do not require localization. |
| Package schema | `src/ai_presenter/packages/models.py` accepts arbitrary `localizedText`, `localizedQuestions`, `localizedAnswers`, and `questionAliases` language keys. | Package Spanish can grow without touching runtime language support. |
| Package content | `packages/ringcentral-video.yaml` contains the Cycle 113 Spanish seed for the background privacy Q&A and background settings aliases only. | The seed is too partial for live runtime Spanish. |
| README | `README.md` documents `zh` localization checks, voice aliases, Chinese runtime examples, and tone aliases. | Runtime Spanish docs should wait until Spanish is genuinely supported and its limits are explicit. |
| Profiles | `profiles/*.yaml` and `src/ai_presenter/profiles/ringcentral-video.yaml` configure providers, soul/memory/skills, and speech routes; they do not carry selected language or tone values. | No profile change is needed for a tone alias. Runtime Spanish should probably be OpenAI-only unless a future asset cycle validates local Spanish TTS. |

## Slice Comparison

### Option A: New Tone Alias

Recommended if the requested user value can map to an existing tone such as `support`, `careful`, `friendly`, or `coach`.

Likely files:

- `src/ai_presenter/runtime/voice.py`
- `tests/unit/test_voice.py`
- `tests/unit/test_cli.py` only if the public `voices` catalog output should show the alias
- `README.md` only if the alias becomes documented operator guidance

Likely tests:

- `tests/unit/test_voice.py::test_voice_settings_normalize_expanded_tones`
- `tests/unit/test_voice.py::test_presenter_tone_aliases_and_description_are_public`
- `tests/unit/test_cli.py::test_voices_lists_language_tone_choices`
- `tests/unit/test_cli.py::test_voices_catalog_output_is_ascii_safe_for_legacy_windows_console`

Expected commands:

```powershell
.\.venv\Scripts\python.exe -m pytest -q -o addopts="" tests\unit\test_voice.py::test_voice_settings_normalize_expanded_tones tests\unit\test_voice.py::test_presenter_tone_aliases_and_description_are_public tests\unit\test_cli.py::test_voices_lists_language_tone_choices tests\unit\test_cli.py::test_voices_catalog_output_is_ascii_safe_for_legacy_windows_console
.\.venv\Scripts\ai-presenter.exe voices
.\.venv\Scripts\ai-presenter.exe doctor --profile ringcentral-video --language en-US --tone <new-alias>
```

Expected diagnostic behavior: the doctor command should normalize to the existing canonical tone and report the English fake-speech profile as voice-compatible, with no package localization change.

### Option B: New Canonical Tone Type

Acceptable only if a simple alias cannot express the product need.

Likely files:

- `src/ai_presenter/runtime/voice.py`
- `tests/unit/test_voice.py`
- `tests/unit/test_cli.py`
- `tests/unit/test_controller.py`
- `tests/unit/test_controller_view_model.py`
- `tests/unit/test_runtime_factory.py` only if Chinese local SAPI rate behavior changes
- `tests/unit/test_questions.py` only if the tone is safety-sensitive and must prove route identity/can-operate parity
- `README.md` only if operator docs mention the new tone

Expected commands:

```powershell
.\.venv\Scripts\python.exe -m pytest -q -o addopts="" tests\unit\test_voice.py tests\unit\test_cli.py::test_voices_lists_language_tone_choices tests\unit\test_controller.py::test_render_voice_label_uses_language_and_tone_labels tests\unit\test_controller_view_model.py
.\.venv\Scripts\ruff.exe check --no-cache src\ai_presenter\runtime\voice.py src\ai_presenter\runtime\controller.py src\ai_presenter\runtime\controller_view_model.py tests\unit\test_voice.py tests\unit\test_cli.py tests\unit\test_controller.py tests\unit\test_controller_view_model.py
.\.venv\Scripts\mypy.exe --no-incremental src\ai_presenter\runtime\voice.py src\ai_presenter\runtime\controller.py src\ai_presenter\runtime\controller_view_model.py
.\.venv\Scripts\ai-presenter.exe demo --profile ringcentral-video --package ringcentral-video --flow meeting-controls-tour --language English --tone <new-tone> --dry-run
```

Expected diagnostic behavior: the new tone should change phrasing only. It must not change package routing, `can_operate`, profile compatibility, or localization counts.

### Option C: Runtime Spanish Support

Not recommended as the immediate next slice.

Likely production files if done safely:

- `src/ai_presenter/runtime/voice.py` for `PresenterLanguage`, labels, aliases, instructions, validation, and routing policy
- `src/ai_presenter/runtime/questions.py` for `_NO_MATCH_ANSWERS["es"]` and no-match safety wording
- `src/ai_presenter/runtime/voice_assets.py` only if Spanish asset readiness needs explicit status messaging
- `src/ai_presenter/runtime/factory.py` only if Spanish local TTS routes or rates are introduced; prefer avoiding this and requiring OpenAI
- `src/ai_presenter/runtime/diagnostics.py` if diagnostic wording needs explicit Spanish support notes
- `src/ai_presenter/cli.py` if help text or user-facing examples change beyond consuming shared constants
- `src/ai_presenter/runtime/controller.py` and `src/ai_presenter/runtime/controller_view_model.py` through shared language choices and labels
- `packages/ringcentral-video.yaml` if runtime Spanish is paired with enough Spanish Q&A/narration to avoid mixed-language behavior
- `README.md` and possibly `docs/runbooks/ringcentral-manual-acceptance.md` if Spanish becomes a documented operator path
- `profiles/*.yaml` only if a Spanish-specific profile is deliberately added; otherwise use the existing OpenAI example/profile path

Likely tests:

- `tests/unit/test_voice.py`
- `tests/unit/test_cli.py`
- `tests/unit/test_questions.py`
- `tests/unit/test_material_packages.py`
- `tests/unit/test_controller.py`
- `tests/unit/test_controller_view_model.py`
- `tests/unit/test_runtime_factory.py`
- `tests/unit/test_voice_assets.py` if asset checks change
- `tests/unit/test_diagnostics.py`
- `tests/integration/test_presenter_loop.py` only if provider/runtime behavior changes enough to need integration coverage

Expected commands for a future Spanish runtime implementation:

```powershell
.\.venv\Scripts\python.exe -m pytest -q -o addopts="" tests\unit\test_voice.py tests\unit\test_cli.py tests\unit\test_questions.py tests\unit\test_material_packages.py tests\unit\test_controller.py tests\unit\test_controller_view_model.py tests\unit\test_runtime_factory.py tests\unit\test_diagnostics.py
.\.venv\Scripts\ai-presenter.exe voices
.\.venv\Scripts\ai-presenter.exe voices --profile ringcentral-video --language es --tone professional
.\.venv\Scripts\ai-presenter.exe voices --profile profiles\ringcentral-video-openai.example.yaml --language es --tone professional
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language es
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language es --require-complete
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language zh --require-complete
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ja --require-complete
.\.venv\Scripts\ai-presenter.exe demo --profile profiles\ringcentral-video-openai.example.yaml --package ringcentral-video --flow meeting-controls-tour --language es --tone professional --dry-run
```

Expected diagnostic behavior if Spanish is OpenAI-only:

- `voices --profile ringcentral-video --language es --tone professional` should exit nonzero because the fake profile must not be treated as real Spanish speech support.
- `voices --profile profiles\ringcentral-video-openai.example.yaml --language es --tone professional` should report Spanish support via `openai`.
- `localization-report --language es --require-complete` should continue to exit `1` until Spanish has full required package coverage.
- Existing `zh` and `ja` `--require-complete` checks should stay green.

## Runtime Spanish Risks

- Mixed-language output: `render_narration_text()` falls back to English narration when `localizedText.es` is missing, and the package currently has 0/51 Spanish demo narration steps.
- Mixed Q&A output: `_qa_answer_text()` falls back to English answers for 11/12 current Q&A items.
- Crash risk: `src/ai_presenter/runtime/questions.py` currently has no `_NO_MATCH_ANSWERS["es"]`; adding `es` only to `PresenterLanguage` can make no-match questions fail at runtime.
- Profile confusion: Spanish should probably require `openai` at first. Allowing fake, Piper, Windows SAPI English, or Windows SAPI Chinese routes would overstate speech readiness.
- Completeness-gate bypass: `demo` and `controller` validate voice compatibility but do not require localization completeness, so runtime Spanish can launch before Spanish package coverage is ready.
- Matcher risk: package-owned `questionAliases.es` already participate in entrypoint matching if a caller can construct an `es` voice. More Spanish aliases should be narrow and covered by matcher/doctor tests.
- Documentation risk: README or handoffs could accidentally say "Spanish supported" when only package/report coverage exists.
- Coverage churn: `.coverage` is already modified locally and should remain out of scope.

## Current Evidence From This Scan

Commands run:

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language es
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language es --require-complete
.\.venv\Scripts\ai-presenter.exe voices
.\.venv\Scripts\ai-presenter.exe demo --profile ringcentral-video --package ringcentral-video --flow meeting-controls-tour --language es --dry-run
```

Observed results:

- Spanish localization report exited `0` and reported `0/51` demo steps, `1/12` localized questions, `1/12` localized answers, and `questionAliases.es present on 1/27 entrypoints (3 aliases)`.
- Spanish `--require-complete` exited `1` with `Localization coverage incomplete for es.`
- `voices` listed English, Chinese, and Japanese only; tones listed Professional, Conversational, Concise, Friendly, Coach, Formal, Support, and Careful.
- `demo --language es --dry-run` exited `1` with `Unsupported presenter language: es`.

## Handoff Scope Check

This Cycle 116 technical scan should create exactly one file:

```text
docs/agent-handoffs/cycle-116-technical-scan.md
```

It intentionally does not implement runtime Spanish, add or change tone metadata, edit package YAML, update tests, change profiles, modify README, touch `.coverage`, or edit Codex home files.

## Lightweight Validation

After creating this file, run:

```powershell
rg -n "[ \t]$" docs\agent-handoffs\cycle-116-technical-scan.md
rg -n "TB[D]|TO[D]O|implement late[r]|fill in detail[s]" docs\agent-handoffs\cycle-116-technical-scan.md
git ls-files --others --exclude-standard docs\agent-handoffs\cycle-116-technical-scan.md
git status --short --untracked-files=all
```

Observed results:

- The trailing-whitespace scan found no matches.
- The placeholder scan found no matches.
- `git ls-files --others --exclude-standard` listed this handoff file as untracked.
- `git status --short --untracked-files=all` showed this handoff plus concurrent out-of-scope worktree changes: `.coverage`, `tests/unit/test_cli.py`, `tests/unit/test_questions.py`, `tests/unit/test_voice.py`, `docs/agent-handoffs/cycle-116-demand-analysis.md`, and `docs/agent-handoffs/cycle-116-risk-scan.md`. Those files were left untouched by this scan.
