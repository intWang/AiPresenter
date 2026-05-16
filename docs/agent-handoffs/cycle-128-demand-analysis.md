# Cycle 128 Demand Analysis: Spanish Limited Runtime Promotion

Date: 2026-05-16
Cycle: 128
Scope: demand analysis only. This handoff is the only intended edit. Do not
modify source, package YAML, existing docs, tests, profiles, generated artifacts,
staging, or commits in this analysis slice.

## Question

Should the next optimization promote Spanish from package-only localization to a
limited runtime presenter language?

Recommendation: yes, but only as an explicitly limited runtime promotion. The
minimum useful slice should enable Spanish presenter selection for the OpenAI
speech route and dry-run/controller surfaces, while keeping local SAPI/Piper
Spanish, live RingCentral acceptance, and broader locale work out of scope.

## Current Evidence

Spanish has crossed the package-readiness threshold that blocked earlier runtime
promotion:

- Cycle 124 completed Spanish package narration: `51/51` demo steps, including
  `22/22` for `meeting-control-map-demo`.
- Spanish package Q&A is complete: `12/12` localized questions and `12/12`
  localized answers.
- Cycle 125 expanded `questionAliases.es` to `26/27` RingCentral Video
  entrypoints with `69` aliases.
- Cycle 126 made package aliases, localized Q&A prompts, diagnostics, token
  fallback, and legacy alias precomputation share Latin-diacritic-insensitive
  matching, so accented and unaccented Spanish prompts route consistently.
- Cycle 127 refreshed durable docs so README and `language-lifecycle.md` now say
  Spanish is package-local complete and query-ready, but still not runtime
  supported.

The remaining hard boundary is runtime voice support:

- `src/ai_presenter/runtime/voice.py` defines `PresenterLanguage =
  Literal["en", "zh", "ja"]`.
- `_LANGUAGE_ALIASES`, `_LANGUAGE_LABELS`, `PRESENTER_LANGUAGE_CHOICES`, voice
  instruction rendering, localized narration selection, and profile validation
  do not include `es`.
- `tests/unit/test_voice.py` and `tests/unit/test_cli.py` intentionally assert
  that `PresenterVoiceSettings(language="es")` and
  `demo --language es --dry-run` fail with `Unsupported presenter language: es`.
- Voice asset checks only have local SAPI special cases for English `Zira` and
  Chinese `Huihui`; Piper defaults to an English model; Japanese already uses
  OpenAI-only validation.
- Profiles are provider-route oriented, not language-specific: the OpenAI
  profile is the only current route that plausibly supports Spanish without
  adding local voice asset discovery.

## User Value

Spanish is now complete enough inside the RingCentral Video package that runtime
rejection has become the visible limitation. A user can inspect complete Spanish
package coverage and ask Spanish-looking package questions, but cannot select
Spanish as the presenter language for the existing localized scripts.

Promoting Spanish in a limited runtime slice would unlock:

- Spanish narration for existing localized demo flows without adding new package
  content.
- Spanish controller/demo dry-run parity with Chinese and Japanese language
  selection.
- A cleaner lifecycle story: Spanish moves from "package complete, runtime
  rejected" to "runtime selectable on supported speech routes, not yet live
  accepted."
- Better validation of the package work already completed in Cycles 124-126,
  because localized Spanish text would flow through the same runtime selection
  path as English, Chinese, and Japanese.

This is now higher value than another package-local Spanish slice. The known
package gaps are no longer coverage or matching; they are voice/provider/runtime
surface ownership.

## Constraints

- Do not let package completeness imply live readiness. Spanish runtime support
  can be added before Spanish live RingCentral acceptance, but docs and doctor
  output must say so clearly.
- Keep RingCentral UI labels literal where the package text already does so.
  Runtime promotion should not translate UIA locators or claim RingCentral's UI
  itself is localized.
- Avoid local Spanish voice asset promises. Windows SAPI voice discovery is
  currently hard-coded around English and Chinese names, and Piper downloads an
  English model by default.
- Preserve current English, Chinese, and Japanese behavior, including Chinese
  SAPI fallback and Japanese OpenAI-only validation.
- Keep Latin-diacritic folding scoped to question matching. Runtime voice
  normalization should accept Spanish aliases, but must not become fuzzy
  language detection.
- Preserve tone as style only. Spanish support should use authored localized
  package text and avoid adding English prefixes such as `Happy to help.` to
  Spanish narration.
- Diagnostics must separate package localization, runtime language support,
  profile voice support, and local asset readiness.
- Shared worktree hygiene still applies: `.coverage` is already modified locally
  and must not be staged by this work.

## Recommended Minimum Viable Scope

Implement Spanish as a runtime presenter language for OpenAI-backed speech first.
The smallest safe slice is:

1. Add canonical `es` to presenter language types, labels, public choices, and
   aliases such as `es`, `es-es`, `es-mx`, `spanish`, and `espanol`.
2. Make `render_voice_instruction()` say Spanish for `es`.
3. Make `render_narration_text()` prefer `localizedText.es` when language is
   Spanish.
4. Ensure authored Spanish localized text does not receive English tone prefixes.
   A practical first pass can mirror Japanese behavior: apply only concise
   first-sentence trimming and otherwise leave authored Spanish intact.
5. Update `validate_profile_voice()` so Spanish is supported only when the
   resolved speech provider is `openai`.
6. Keep `resolve_speech_provider_name()` unchanged for local routes unless a
   test proves a narrow adjustment is required. Fake, Piper, Windows SAPI
   English, and Windows SAPI Chinese should remain unsupported for Spanish.
7. Update `voices`, `doctor`, `demo`, and `controller` CLI/controller tests so
   Spanish appears as a selectable runtime language but reports unsupported for
   incompatible profiles.
8. Update README/lifecycle docs only if implementation happens in the next
   cycle, and only to say Spanish runtime is limited to the OpenAI route until
   live/manual acceptance and local voice support land.
9. Add or update focused tests for Spanish language aliases, labels, localized
   narration selection, profile validation, OpenAI acceptance, local-route
   rejection, doctor voice checks, voices catalog output, and demo/controller
   dry-run behavior.

This scope intentionally treats Spanish like Japanese for provider support:
runtime-selectable, OpenAI-only, and not automatically local-voice-ready.

## Out Of Scope

- Do not add Spanish SAPI voice discovery or hard-code a Windows Spanish voice
  name.
- Do not add Spanish Piper voice downloads, model selection, or asset readiness.
- Do not change OpenAI provider internals unless existing provider tests show it
  cannot speak Spanish after `render_voice_instruction()` changes.
- Do not add package YAML content, aliases, Q&A, locators, open steps, cleanup,
  demo flows, or safety policy.
- Do not broaden Latin-diacritic matching or add unaccented duplicate YAML
  aliases.
- Do not claim Spanish live RingCentral Video acceptance.
- Do not translate RingCentral UI labels, UIA locators, screenshots, or product
  control names.
- Do not make Spanish the default language or alter English/Chinese/Japanese
  defaults.
- Do not stage or commit, and do not touch `.coverage`.

## Acceptance Criteria For A Promotion Cycle

Runtime language and rendering:

- `PresenterVoiceSettings(language="es").language == "es"`.
- Spanish aliases normalize predictably, including `Spanish`, `es-ES`, and
  `es-MX`.
- `language_label("es") == "Spanish"`.
- `PRESENTER_LANGUAGE_CHOICES` and `ai-presenter voices` list Spanish.
- `render_voice_instruction(PresenterVoiceSettings(language="es"))` instructs
  Spanish output.
- `render_narration_text()` uses `localizedText.es` for Spanish demo steps.
- Spanish authored localized text is not prefixed with English tone phrases.
- Concise tone trims Spanish localized text consistently with Japanese/localized
  behavior.

Provider/profile behavior:

- `validate_profile_voice()` accepts Spanish with
  `profiles/ringcentral-video-openai.example.yaml`.
- `validate_profile_voice()` rejects Spanish for fake, Piper, `windows-sapi`,
  `windows-sapi-en`, and `windows-sapi-zh` profiles with an error that names
  Spanish and the required OpenAI route.
- `voices --profile ringcentral-video-openai.example.yaml --language es` reports
  Spanish supported.
- `voices --profile ringcentral-video-bind-speaker --language es` exits nonzero
  and explains the incompatible local speech route.
- Local voice asset checks do not pretend to verify Spanish assets.

CLI/controller behavior:

- `demo --profile profiles/ringcentral-video-openai.example.yaml --package
  ringcentral-video --flow meeting-control-map-demo --language es --dry-run`
  exits 0 and reports `Loaded voice: Spanish / Professional`.
- `controller --profile profiles/ringcentral-video-openai.example.yaml --package
  ringcentral-video --flow meeting-control-map-demo --language es --dry-run`
  exits 0 and reports Spanish voice selection.
- The same demo/controller commands with `ringcentral-video-bind-speaker` fail
  before runtime launch with a profile voice compatibility error.
- `doctor --profile profiles/ringcentral-video-openai.example.yaml --package
  ringcentral-video --flow meeting-control-map-demo --language es
  --require-localization` reports package localization OK and Spanish voice OK.
- `doctor --profile ringcentral-video-bind-speaker --package ringcentral-video
  --language es --require-localization` reports package localization OK but
  voice/profile support failure.
- Once Spanish is runtime-supported, `doctor --require-localization
  --localization-language es` should no longer fail the separate runtime
  language support check solely because `es` is package-only; any nonzero exit
  should come from profile voice incompatibility or other real failures.

Regression boundaries:

- Existing English, Chinese, and Japanese voice tests still pass.
- Existing localization counts remain `51/51`, `12/12`, `12/12`, with Spanish
  aliases `26/27` and `69`.
- RingCentral package doctor remains `0 warnings, 0 failed` for the standard
  package/flow check.
- Spanish package question routing remains accent-insensitive and Q&A-first for
  safety prompts.
- No source or docs claim Spanish live acceptance until a dated manual or
  automated acceptance run is recorded.

Recommended verification commands for the implementation cycle:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_voice.py tests\unit\test_voice_assets.py tests\unit\test_cli.py tests\unit\test_controller.py tests\unit\test_controller_view_model.py tests\unit\test_controller_session.py
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py tests\unit\test_material_packages.py tests\unit\test_diagnostics.py
.\.venv\Scripts\ruff check --no-cache .
.\.venv\Scripts\mypy --no-incremental src tests
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language es --require-complete
.\.venv\Scripts\ai-presenter.exe doctor --profile profiles/ringcentral-video-openai.example.yaml --package ringcentral-video --flow meeting-control-map-demo --language es --require-localization
.\.venv\Scripts\ai-presenter.exe demo --profile profiles/ringcentral-video-openai.example.yaml --package ringcentral-video --flow meeting-control-map-demo --language es --dry-run
.\.venv\Scripts\ai-presenter.exe controller --profile profiles/ringcentral-video-openai.example.yaml --package ringcentral-video --flow meeting-control-map-demo --language es --dry-run
git diff --check
git status --short
```

## Handoff Prompt

You are the Cycle 128 implementation subagent for AiPresenter. Promote Spanish
from package-only to limited runtime presenter language, scoped to OpenAI-backed
speech support. Do not add local Spanish SAPI/Piper support, do not change
package YAML, and do not claim live RingCentral acceptance.

Start by adding failing tests around `PresenterVoiceSettings(language="es")`,
Spanish labels/aliases, Spanish localized narration rendering, OpenAI profile
acceptance, local profile rejection, `voices` output, doctor behavior, and
demo/controller dry-run behavior. Then update the runtime voice surface and only
the docs needed to describe the new limited support boundary.

Keep the result honest: Spanish may become runtime-selectable for the OpenAI
route, but it is not local-voice-ready and not live-accepted until later cycles
prove those surfaces.
