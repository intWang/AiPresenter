# Cycle 128 Experience: Spanish OpenAI Runtime Promotion

Date: 2026-05-16

## Summary

Cycle 128 promoted Spanish from package-local language coverage to a limited
runtime presenter language. The durable lesson is that runtime promotion is not
the same thing as package localization, and provider readiness is not the same
thing as live product acceptance. Spanish can now be selected with
`--language es`, but only when the resolved speech provider is OpenAI.

The safe shape was narrow and explicit:

- Package Spanish was already complete in `packages/ringcentral-video.yaml`.
- Runtime Spanish was added in `src/ai_presenter/runtime/voice.py`.
- Spanish remains rejected for fake, Piper, `windows-sapi`, `windows-sapi-en`,
  and `windows-sapi-zh`.
- Durable docs now describe Spanish as OpenAI-only runtime support, not local
  SAPI/Piper support and not live RingCentral Video acceptance.

## What Changed

The runtime voice boundary is owned in `src/ai_presenter/runtime/voice.py`.
The current diff adds `es` to `PresenterLanguage`,
`PRESENTER_LANGUAGE_CHOICES`, `_LANGUAGE_LABELS`, and `_LANGUAGE_ALIASES`.
Aliases include `es`, `es-es`, `es-mx`, `spanish`, and `espanol`.
`render_presenter_text()` now treats Spanish like Japanese for authored
localized text, so friendly Spanish narration does not receive English prefixes
such as `Happy to help.`. `validate_profile_voice()` accepts Spanish only when
`resolve_speech_provider_name()` returns `openai`.

The tests in `tests/unit/test_voice.py` are the clearest contract for the new
surface. They cover Spanish alias normalization, public aliases, voice
instruction text, Spanish localized narration selection, concise first-sentence
behavior, OpenAI profile acceptance, and local provider rejection.

The CLI tests in `tests/unit/test_cli.py` moved the old invalid-language test
from `es` to `fr`, then added positive OpenAI dry-run coverage for `demo` and
`controller`, plus negative local-profile coverage for Spanish. The `voices`
tests now expect Spanish in the catalog and require OpenAI for targeted Spanish
support.

The diagnostics tests in `tests/unit/test_diagnostics.py` preserve the
package-localization/runtime-language distinction by moving the package-only
fixture from Spanish to German. That matters: once Spanish is a runtime
language, `doctor --require-localization --localization-language es` should not
fail merely because Spanish used to be package-only. Future package-local
languages still need that failure mode.

Durable docs were updated in `README.md`,
`docs/knowledge/language-lifecycle.md`,
`docs/knowledge/ai-presenter-maintenance.md`,
`docs/knowledge/ringcentral-video/runtime-safety-routing.md`, and
`docs/knowledge/ringcentral-video/source-index.md`. The important wording is
that Spanish is runtime-selectable only with OpenAI-backed speech. Do not let
future edits shorten that to generic Spanish runtime support.

## Boundary Lessons

Package localization answers whether a material package has authored content
for a language. Runtime language support answers whether the presenter can be
configured and validated with that language. Provider support answers whether a
specific profile can speak it. Live acceptance answers whether the full product
workflow has been proven in the target environment.

Cycle 128 only crossed the first three boundaries for the OpenAI route:

- Package localization: Spanish remains complete for RingCentral Video.
- Runtime language: `PresenterVoiceSettings(language="es")` now normalizes to
  `es`.
- Provider route: Spanish is accepted for OpenAI speech only.
- Local assets: no Spanish SAPI or Piper readiness exists yet.
- Live acceptance: no dated Spanish RingCentral Video acceptance run is claimed.

This distinction prevented two easy mistakes. First, adding Spanish to
`PRESENTER_LANGUAGE_CHOICES` alone would have exposed the controller and voices
catalog before provider validation was honest. Second, allowing fake or local
profiles to fall through would have turned Spanish into English-asset speech by
accident.

## OpenAI-Only Spanish Boundary

Treat Spanish like Japanese for provider readiness unless a later cycle builds
real local assets. OpenAI can be the Spanish route because the profile-level
speech provider is generic and does not require local voice discovery. Local
routes are different:

- `profiles/ringcentral-video.yaml` uses fake speech and must reject Spanish.
- `profiles/ringcentral-video-piper-speaker.yaml` defaults Piper to an English
  model and must reject Spanish.
- `profiles/ringcentral-video-bind-speaker.yaml` resolves to
  `windows-sapi-en` and must reject Spanish.
- Any `windows-sapi` or `windows-sapi-zh` route must reject Spanish until a
  named Spanish SAPI route and asset check exist.

The expected error should name `Spanish / Professional`, the incompatible
speech provider, and the OpenAI requirement. This keeps CLI, doctor, controller,
and voices output aligned.

## Verification Expectations

Before treating the promotion as ready, future agents should expect these
checks to pass from `C:\Users\rcadmin\Documents\Repos\AiPresenter`:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_voice.py tests\unit\test_voice_assets.py tests\unit\test_cli.py tests\unit\test_controller.py tests\unit\test_controller_view_model.py tests\unit\test_controller_session.py
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py tests\unit\test_material_packages.py tests\unit\test_diagnostics.py
.\.venv\Scripts\ruff check --no-cache .
.\.venv\Scripts\mypy --no-incremental src tests
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language es --require-complete
.\.venv\Scripts\ai-presenter.exe voices --profile profiles/ringcentral-video-openai.example.yaml --language es
.\.venv\Scripts\ai-presenter.exe doctor --profile profiles/ringcentral-video-openai.example.yaml --package ringcentral-video --flow meeting-control-map-demo --language es --require-localization
.\.venv\Scripts\ai-presenter.exe demo --profile profiles/ringcentral-video-openai.example.yaml --package ringcentral-video --flow meeting-control-map-demo --language es --dry-run
.\.venv\Scripts\ai-presenter.exe controller --profile profiles/ringcentral-video-openai.example.yaml --package ringcentral-video --flow meeting-control-map-demo --language es --dry-run
.\.venv\Scripts\ai-presenter.exe doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo --language es
git diff --check
git status --short
```

Expected outcomes: Spanish localization remains `51/51` demo steps, `12/12`
Q&A questions, and `12/12` Q&A answers; Spanish aliases remain `26/27`
entrypoints with `69` aliases; OpenAI Spanish voice checks pass; local Spanish
voice checks fail with profile compatibility errors; no docs claim local voice
readiness or live RingCentral acceptance.

OpenAI doctor checks may still require provider environment variables when the
full provider environment path is exercised. Dry-run `demo` and `controller`
commands should not need real OpenAI calls.

## Next Optimization Cycle

The next cycle should optimize the new boundary instead of broadening it by
accident. Recommended focus:

- Add or confirm `tests/unit/test_runtime_factory.py` coverage that an OpenAI
  Spanish material demo uses `localizedText.es`, resolves speech through
  `openai`, and does not instantiate real OpenAI clients.
- Run the full focused verification matrix above and record exact results,
  especially any provider-environment behavior in doctor.
- Review controller voice-readiness copy and view-model tests so Start and
  Submit stay blocked for Spanish on local profiles but remain available for
  OpenAI profiles.
- Keep `docs/knowledge/language-lifecycle.md` as the durable source of truth
  for language state; leave older handoffs as dated records.
- Do not add Spanish SAPI or Piper support unless the cycle also owns a named
  local route, asset availability checks, profile behavior, tests, and docs.
- Do not claim live Spanish RingCentral Video acceptance until a dated manual or
  automated acceptance run records the actual flow, profile, provider, and
  environment.

The high-value next move is evidence, not expansion: prove that the OpenAI-only
Spanish runtime path behaves end to end, and keep unsupported local routes
visibly unsupported.
