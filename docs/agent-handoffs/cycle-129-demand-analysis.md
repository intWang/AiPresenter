# Cycle 129 Demand Analysis: Spanish OpenAI Readiness Proof

Date: 2026-05-16
Cycle: 129
Scope: demand analysis only. This handoff is the only intended edit. Do not
modify source, package YAML, durable docs, tests, profiles, generated artifacts,
staging, or commits in this analysis slice.

## Question

What should the next optimization cycle do after Cycle 128 promoted Spanish as
an OpenAI-only runtime presenter language?

Recommendation: prove the Spanish OpenAI path end to end before expanding it.
The next cycle should turn the new boundary into executable evidence across
runtime factory, CLI, doctor, voices, controller readiness, and dry-run demo
surfaces. It should not claim local SAPI/Piper support, real OpenAI audio
synthesis, or live RingCentral Video acceptance.

## User Need

Users now have a Spanish package that is complete and runtime-selectable on the
OpenAI speech route, but they still need confidence that this path is coherent
as a product workflow:

- Selecting `--language es` with the OpenAI profile should use Spanish package
  narration, resolve speech through `openai`, and avoid real provider calls in
  dry-run or injected-registry tests.
- Local profiles should fail early and readably, so users do not accidentally
  run Spanish through fake speech, English Piper assets, or English/Chinese
  Windows SAPI voices.
- Diagnostics should distinguish package localization, runtime language
  recognition, profile voice compatibility, provider environment readiness, and
  live acceptance.
- Controller readiness should mirror CLI behavior: OpenAI Spanish can proceed
  when environment prerequisites are satisfied; local Spanish stays blocked.
- Documentation and handoffs should preserve the precise claim:
  Spanish is OpenAI-backed runtime support, not local voice readiness and not
  live RingCentral acceptance.

The user-visible value is trust. Cycle 128 made Spanish selectable; Cycle 129
should prove that selection uses the right text, the right provider route, and
the right failure boundaries.

## Candidate Improvements

1. Runtime factory evidence

   Add focused coverage that an existing-window RingCentral material demo with
   `PresenterVoiceSettings(language="es")` and the OpenAI profile rewrites demo
   narration from `localizedText.es`, resolves speech through `openai`, and can
   run with injected fake providers rather than constructing real OpenAI
   clients.

2. CLI and diagnostics smoke proof

   Run and record the exact Cycle128 Spanish smoke matrix: `voices`,
   `localization-report`, `doctor`, `demo --dry-run`, and
   `controller --dry-run` for the OpenAI profile, plus a negative local-profile
   check. Clarify any doctor behavior that depends on missing OpenAI
   environment variables.

3. Controller readiness parity

   Review controller and view-model readiness coverage so Spanish on local
   profiles is blocked before Start or question submit, while Spanish on the
   OpenAI profile follows the same readiness path as other supported runtime
   languages. Keep this focused on validation and messaging, not UI redesign.

4. Error wording polish

   If current output is ambiguous, improve Spanish local-profile errors so they
   name `Spanish / <Tone>`, the incompatible speech provider, and the OpenAI
   requirement. Avoid broad CLI copy churn.

5. Evidence handoff

   Produce an implementation or test-review handoff with command results and
   residual risks. Durable docs should only change if source behavior changes or
   existing docs are inaccurate.

## Recommended Scope

Choose a proof-first scope:

- Add or confirm `tests/unit/test_runtime_factory.py` coverage for OpenAI
  Spanish material demo narration and provider routing.
- Add focused controller/view-model tests only where the current suite does not
  already prove Spanish OpenAI readiness versus local-profile rejection.
- Run the Spanish OpenAI verification matrix and record exact outcomes in a
  Cycle129 implementation or test-review handoff.
- Fix narrow gaps discovered by that evidence, limited to runtime validation,
  provider routing, dry-run behavior, or readiness messages.
- Keep Spanish package counts stable: `51/51` demo steps, `12/12` Q&A
  questions, `12/12` Q&A answers, and `questionAliases.es` on `26/27`
  entrypoints with `69` aliases.

This is intentionally an evidence cycle, not a language expansion cycle.

## Out Of Scope

- Do not add Spanish Windows SAPI support, voice discovery, or a
  `windows-sapi-es` route.
- Do not add Spanish Piper model downloads, profile routing, or asset checks.
- Do not claim live OpenAI audio synthesis unless a real provider call is
  intentionally scoped, run, and recorded.
- Do not claim live RingCentral Video acceptance or update acceptance evidence
  without a dated manual or automated run in the target environment.
- Do not change package YAML, Spanish copy, Q&A, aliases, locators, demo flows,
  safety policy, or RingCentral UI labels.
- Do not broaden Latin-diacritic matching, add fuzzy language detection, or
  infer runtime support from package query routing.
- Do not modify durable docs unless implementation finds an actual mismatch.
- Do not stage generated artifacts such as `.coverage`.

## Acceptance Criteria

Cycle129 is successful when the implementation/test-review evidence shows:

- `demo --profile profiles/ringcentral-video-openai.example.yaml --package
  ringcentral-video --flow meeting-control-map-demo --language es --dry-run`
  exits `0` and reports `Loaded voice: Spanish / Professional`.
- `controller --profile profiles/ringcentral-video-openai.example.yaml
  --package ringcentral-video --flow meeting-control-map-demo --language es
  --dry-run` exits `0` and reports Spanish voice selection.
- `voices --profile profiles/ringcentral-video-openai.example.yaml --language
  es` reports the selected Spanish voice as supported via `openai`.
- The equivalent Spanish local-profile command for
  `ringcentral-video-bind-speaker` exits nonzero before runtime launch and
  names the incompatible local speech route plus the OpenAI requirement.
- Doctor output keeps package localization, runtime language support, voice
  compatibility, and provider environment readiness separate.
- Runtime factory tests prove Spanish OpenAI material demos use
  `localizedText.es` and resolve speech through `openai` without real OpenAI
  client construction.
- Controller readiness tests, if touched, prove local Spanish is blocked while
  OpenAI Spanish follows the supported readiness path.
- Existing English, Chinese, and Japanese behavior remains unchanged.
- No source, docs, or handoff text claims Spanish local SAPI/Piper readiness or
  live RingCentral Video acceptance.
- `git diff --check` passes and `git status --short` shows only the intended
  Cycle129 files plus any pre-existing unrelated local artifacts left unstaged.

Recommended verification commands for the next cycle:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_voice.py tests\unit\test_voice_assets.py tests\unit\test_cli.py tests\unit\test_controller.py tests\unit\test_controller_view_model.py tests\unit\test_controller_session.py
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_runtime_factory.py tests\unit\test_questions.py tests\unit\test_material_packages.py tests\unit\test_diagnostics.py
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language es --require-complete
.\.venv\Scripts\ai-presenter.exe voices --profile profiles/ringcentral-video-openai.example.yaml --language es
.\.venv\Scripts\ai-presenter.exe doctor --profile profiles/ringcentral-video-openai.example.yaml --package ringcentral-video --flow meeting-control-map-demo --language es --require-localization
.\.venv\Scripts\ai-presenter.exe demo --profile profiles/ringcentral-video-openai.example.yaml --package ringcentral-video --flow meeting-control-map-demo --language es --dry-run
.\.venv\Scripts\ai-presenter.exe controller --profile profiles/ringcentral-video-openai.example.yaml --package ringcentral-video --flow meeting-control-map-demo --language es --dry-run
.\.venv\Scripts\ai-presenter.exe doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo --language es
git diff --check
git status --short
```

## Handoff Prompt

You are the Cycle129 implementation or test-evidence agent for AiPresenter.
Prove Spanish OpenAI end-to-end readiness after Cycle128. Focus on runtime
factory coverage, CLI/doctor/voices/controller dry-run evidence, and explicit
negative local-profile behavior. Do not add Spanish SAPI/Piper support, do not
change package YAML, and do not claim live RingCentral Video acceptance.
