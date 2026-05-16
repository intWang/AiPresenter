# Cycle 129 Risk Scan: Spanish OpenAI Runtime Behavior

Date: 2026-05-16

Scope: risk scan only for proving Spanish OpenAI runtime behavior after the
Cycle 128 promotion. This file is the only intended edit for this task. Do not
edit source code, tests, package YAML, durable docs, stage files, or commit from
this scan.

## Executive Boundary

Spanish is now a limited runtime presenter language, but only for OpenAI-backed
speech profiles. The proof burden for Cycle 129 is not "Spanish exists in the
dropdown"; it is "Spanish can run through the OpenAI route without silently
opening local speech, fake speech, or package-only paths."

Safe current-state claims:

- Spanish package localization is complete for RingCentral Video.
- `PresenterVoiceSettings(language="es")` normalizes to `es`.
- OpenAI-backed speech profiles may use Spanish.
- Fake, Piper, `windows-sapi`, `windows-sapi-en`, and `windows-sapi-zh` profiles
  must still reject Spanish.
- No live RingCentral Spanish acceptance is proven unless a dated acceptance run
  records it in the runbook or evidence trail.

## Current Committed Shape

Inspected from HEAD:

- `src/ai_presenter/runtime/voice.py`
  - `PresenterLanguage` includes `es`.
  - `PRESENTER_LANGUAGE_CHOICES` includes `("Spanish", "es")`.
  - Spanish aliases include `es`, `es-es`, `es-mx`, `spanish`, and `espanol`.
  - `render_presenter_text()` treats Spanish like localized authored text, with
    no English tone prefixes.
  - `validate_profile_voice()` accepts Spanish only when
    `resolve_speech_provider_name()` returns `openai`.

- `src/ai_presenter/runtime/factory.py`
  - OpenAI speech is registered only when `profile.providers.speech == "openai"`.
  - Local SAPI/Piper routes are still English/Chinese-only.
  - Material demo runtime selects `providers.speech(resolve_speech_provider_name(...))`.

- `src/ai_presenter/runtime/controller.py` and
  `src/ai_presenter/runtime/controller_view_model.py`
  - Controller language choices are data-driven from `PRESENTER_LANGUAGE_CHOICES`.
  - Start and Submit both check voice readiness before initiating a demo path.
  - Unsupported profile voices are still rejected by `validate_profile_voice()`;
    local asset readiness is a separate check.

- `src/ai_presenter/runtime/diagnostics.py`
  - `doctor --require-localization --localization-language es` now reports
    Spanish as runtime-recognized.
  - Package-only language boundary coverage has moved to a fixture language such
    as `de`, which is correct and must be preserved.

- `docs/knowledge/language-lifecycle.md` and `README.md`
  - Docs say Spanish is OpenAI-backed runtime-selectable only.
  - Docs still say local SAPI/Piper Spanish and live RingCentral acceptance are
    future work.

## Regression Risks To Avoid

### Accidental Local Spanish Support

Risk: Spanish is accepted on fake, Piper, or Windows SAPI because it is present
in `PRESENTER_LANGUAGE_CHOICES`, because fake speech can synthesize bytes, or
because local provider routing falls through to an English/Chinese route.

Guardrail:

- Spanish must require `speech=openai`.
- `resolve_speech_provider_name()` must not map `es` to `piper`,
  `windows-sapi`, `windows-sapi-en`, or `windows-sapi-zh`.
- `voices --profile ringcentral-video-bind-speaker --language es` must fail
  with a profile voice compatibility error, not an asset warning.

### Real Network Calls In Tests

Risk: OpenAI behavior tests instantiate real `OpenAI(...)` clients or call
`client.responses.create()` / `client.audio.speech.create()` against the network.

Guardrail:

- Unit tests must inject fake OpenAI clients or monkeypatch the OpenAI factory.
- CLI dry-run tests must not construct providers.
- Runtime factory tests for Spanish OpenAI must inject a `ProviderRegistry` with
  fake speech and must not require `OPENAI_API_KEY`.
- Any test that sets `OPENAI_API_KEY` should still monkeypatch client creation or
  stop before provider construction.

### Controller Start/Submit Readiness Mismatch

Risk: Start blocks Spanish on a local profile but Submit can still answer and
start or queue a safe demo, or Start uses one readiness path while Submit uses
another.

Guardrail:

- For local profiles, Spanish must be rejected before either Start or Submit can
  start a runner thread or enqueue an interrupt demo.
- Voice readiness failures must disable both Start and Submit in the view model.
- OpenAI Spanish should show `assets: Not required`; local Spanish should not
  get that far because profile voice validation fails first.
- Running-state behavior remains intentional: Start is disabled while running,
  but Submit may remain enabled only when target and voice are valid.

### Docs Overstating Live Acceptance

Risk: Docs or handoffs turn package localization plus OpenAI runtime support into
claims that Spanish has been live-accepted in RingCentral Video.

Guardrail:

- Wording may say "runtime-selectable with OpenAI-backed speech profiles."
- Wording must not say "accepted", "validated live", "production ready", or
  "local Spanish voice ready" without dated evidence.
- Acceptance evidence belongs in the RingCentral runbook or knowledge evidence
  files, not only in unit-test output or handoffs.

### Package-Only Language Boundary Loss

Risk: Because Spanish moved from package-only to runtime-supported, tests stop
proving that package-local languages can pass localization while still failing
runtime language support.

Guardrail:

- Keep a synthetic complete package for an unsupported language, currently `de`,
  and assert `[OK] localization` with `[FAIL] runtime language support`.
- Keep `--localization-language` separate from `--language`.
- Do not let package localization reports create runtime voice support.

## Must-Have Tests

Before claiming Cycle 129 behavior is proven, the test suite must include all of
these signals:

- Voice normalization: Spanish aliases normalize to `es`, `language_label("es")`
  returns `Spanish`, and an unrelated language such as `fr` still rejects.
- Voice rendering: Spanish localized narration uses `localizedText.es`, concise
  Spanish uses the first sentence, and non-concise Spanish gets no English tone
  prefix.
- Provider validation: Spanish passes for
  `profiles/ringcentral-video-openai.example.yaml` and fails for fake, Piper,
  `windows-sapi`, `windows-sapi-en`, and `windows-sapi-zh` with error text that
  names Spanish and OpenAI.
- CLI dry run: `demo` and `controller` accept `--language es` with the OpenAI
  profile and reject it with local profiles before runtime is called.
- Voices catalog: Spanish appears in the language catalog; targeted OpenAI
  Spanish is supported; targeted local Spanish is unsupported.
- Diagnostics: OpenAI Spanish reports `[OK] voice`, local Spanish reports
  `[FAIL] voice`, and `--require-localization --localization-language es`
  reports runtime language support OK.
- Package-only boundary: a complete unsupported fixture language still reports
  `[OK] localization` and `[FAIL] runtime language support`.
- Runtime factory: an existing-window or material demo test with Spanish OpenAI
  uses `localizedText.es`, resolves speech provider `openai`, and uses an
  injected registry so no real OpenAI client is constructed.
- Controller view model: missing local voice assets block both Start and Submit;
  a valid OpenAI Spanish voice has no local asset requirement; running-state
  Submit remains allowed only with valid target and voice.
- OpenAI provider unit tests: narration and speech calls use fake clients; blank
  text errors happen before API calls; missing API key errors are limited to
  explicit real-client construction tests.

## No-Go Conditions

Do not accept the Spanish OpenAI proof if any of these are true:

- Spanish succeeds with fake speech, Piper, generic SAPI, English SAPI, or
  Chinese SAPI.
- A unit or CLI test requires real network access, real OpenAI credentials, or a
  live RingCentral window unless it is explicitly marked manual/integration and
  excluded from the normal unit path.
- `demo --language es --dry-run` or `controller --language es --dry-run`
  constructs an OpenAI client.
- Controller Submit can start, queue, or run a Spanish demo on a profile where
  Start is blocked for the same voice/target.
- `doctor --require-localization --localization-language es` is treated as
  proof of provider readiness or live acceptance.
- The package-only language fixture is removed without a replacement.
- README, lifecycle docs, or runbooks imply live Spanish RingCentral acceptance
  without dated acceptance evidence.
- Spanish aliases or accent-folding become cross-language semantic matching,
  stemming, transliteration, or a provider compatibility mechanism.
- Packaging changes are mixed into the runtime proof. Root `packages/*.yaml`
  distribution is a separate boundary from Spanish runtime behavior.

## Suggested Verification Commands

Run from `C:\Users\rcadmin\Documents\Repos\AiPresenter`:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_voice.py tests\unit\test_cli.py tests\unit\test_diagnostics.py tests\unit\test_runtime_factory.py tests\unit\test_controller.py tests\unit\test_controller_view_model.py tests\unit\test_openai_provider.py tests\unit\test_voice_assets.py
.\.venv\Scripts\ai-presenter.exe voices
.\.venv\Scripts\ai-presenter.exe voices --profile profiles\ringcentral-video-openai.example.yaml --language es
.\.venv\Scripts\ai-presenter.exe voices --profile ringcentral-video-bind-speaker --language es
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language es --require-complete
.\.venv\Scripts\ai-presenter.exe demo --profile profiles\ringcentral-video-openai.example.yaml --package ringcentral-video --flow meeting-control-map-demo --language es --dry-run
.\.venv\Scripts\ai-presenter.exe controller --profile profiles\ringcentral-video-openai.example.yaml --package ringcentral-video --flow meeting-control-map-demo --language es --dry-run
.\.venv\Scripts\ai-presenter.exe demo --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo --language es --dry-run
git diff --check -- docs\agent-handoffs\cycle-129-risk-scan.md
git status --short
```

Expected results:

- Focused unit tests pass without real OpenAI network traffic.
- OpenAI profile Spanish dry runs pass.
- Local profile Spanish dry run fails before runtime with a compatibility error.
- Spanish localization remains complete.
- `git status --short` is reviewed carefully; this scan should contribute only
  this handoff file. Preserve any unrelated dirty files from other agents.

## Acceptance Language

Use this wording until live evidence exists:

- "Spanish is runtime-selectable with OpenAI-backed speech profiles."
- "Spanish local SAPI/Piper support is not implemented."
- "Spanish RingCentral Video package localization is complete."
- "Live RingCentral Spanish acceptance remains unproven until a dated acceptance
  run records provider, profile, flow, audio, and RingCentral evidence."

Avoid this wording:

- "Spanish is accepted."
- "Spanish works locally."
- "Spanish voice readiness is complete."
- "The package passed localization, so Spanish runtime behavior is proven."
