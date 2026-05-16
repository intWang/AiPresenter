# Cycle 129 Test Review: Spanish OpenAI Runtime Proof

Date: 2026-05-16
Cycle: 129
Scope: review of the current uncommitted Cycle129 diff and handoff evidence.
This review only writes `docs/agent-handoffs/cycle-129-test-review.md`.

## Scope Reviewed

- Controller readiness compatibility before local asset checks.
- Spanish no-match fallback behavior.
- Runtime factory Spanish OpenAI provider routing and injected registry proof.
- Controller Spanish question path and voice forwarding.
- Local Spanish rejection in controller/operator readiness.
- No real OpenAI or RingCentral calls in the focused evidence tests.
- Handoff/document wording for local Spanish and live-acceptance overclaims.

Reviewed uncommitted files:

- `src/ai_presenter/runtime/controller.py`
- `src/ai_presenter/runtime/questions.py`
- `tests/unit/test_controller.py`
- `tests/unit/test_controller_view_model.py`
- `tests/unit/test_questions.py`
- `tests/unit/test_runtime_factory.py`
- `docs/agent-handoffs/cycle-129-demand-analysis.md`
- `docs/agent-handoffs/cycle-129-experience.md`
- `docs/agent-handoffs/cycle-129-implementation.md`
- `docs/agent-handoffs/cycle-129-risk-scan.md`
- `docs/agent-handoffs/cycle-129-technical-scan.md`

## Commands And Results

```powershell
git status --short
```

Result: dirty Cycle129 source/test/handoff files plus modified `.coverage`.
No staging was changed.

```powershell
git diff --stat
```

Result: 356 inserted lines across controller/questions source and focused unit
tests, plus modified `.coverage`.

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_runtime_factory.py::test_existing_window_material_demo_routes_openai_spanish_and_uses_localized_text tests\unit\test_runtime_factory.py::test_existing_window_material_demo_uses_injected_openai_registry_for_spanish tests\unit\test_controller.py::test_controller_voice_readiness_rejects_incompatible_voice_before_asset_check tests\unit\test_controller.py::test_presenter_controller_starts_spanish_openai_question_demo_when_idle tests\unit\test_controller_view_model.py::test_incompatible_spanish_local_voice_explains_start_and_submit_disabled tests\unit\test_controller_view_model.py::test_spanish_openai_view_model_is_startable_without_local_assets tests\unit\test_questions.py::test_spanish_no_match_fallback_is_localized_and_not_operable
```

Result: `7 passed in 3.39s`.

```powershell
git diff --check
```

Result: exit 0. Git reported LF-to-CRLF working-copy warnings for the modified
source/test files; no whitespace errors were reported.

```powershell
rg`/`Select-String` scans for live-acceptance and real-provider wording
```

Result: Cycle129 handoffs consistently frame Spanish as OpenAI-backed runtime
support only and preserve the no-live-acceptance boundary. Matches for
"accepted" and similar words were in guardrails or "avoid this wording" sections,
not overclaims.

## Findings By Severity

### Critical

None found.

### Important

None found.

### Minor

- Spanish fallback copy is intentionally ASCII-only: `No encontre un control que
  coincida en el contexto activo de la app.` This is covered and not a runtime
  blocker, but it remains copy-polish debt if final Spanish localization quality
  matters.
- `.coverage` is modified in the working tree. Treat it as generated output and
  leave it unstaged unless the cycle owner explicitly wants regenerated coverage
  data committed.

## Requirement Notes

- Controller readiness now validates `validate_profile_voice(profile, voice)`
  before local asset checks. The focused test proves incompatible Spanish local
  voice settings return `FAIL` and do not call the asset checker.
- Spanish no-match fallback is covered and does not fall back to English.
- Runtime factory evidence includes the stronger injected-registry test:
  `OpenAISpeechProvider` construction is patched to fail, an injected `openai`
  speech provider is used, and Spanish `localizedText.es` reaches the timeline.
- Controller Spanish question coverage proves `PresenterVoiceSettings(language="es")`
  is forwarded into the safe `question-answer-demo` runner path.
- Local Spanish rejection is reflected in operator Start and Submit disabled
  reasons; OpenAI Spanish is modeled as startable with local assets not required.
- Focused tests do not make real OpenAI or RingCentral calls. They use fake
  providers, fake runners, fake desktop classes, and existing fake handles.
- Handoffs avoid claiming Spanish local SAPI/Piper support, live OpenAI audio
  synthesis, or live RingCentral acceptance.

## Residual Risks

- I did not rerun the full CLI/doctor smoke matrix in this review pass. The
  remaining merge-readiness evidence should still include `voices`,
  `localization-report`, `doctor`, `demo --dry-run`, and `controller --dry-run`
  commands for the OpenAI profile plus the negative local-profile check.
- The focused controller question test proves voice forwarding and safe demo
  startup, not that entrypoint-generated answer text is fully Spanish.
- No live OpenAI synthesis, audio quality, or real RingCentral UI behavior is
  proven by this cycle.

## Go / No-Go

Go for the focused Cycle129 test evidence reviewed here.

No-go for broader claims such as Spanish local SAPI/Piper readiness, real OpenAI
audio acceptance, production readiness, or live RingCentral Spanish acceptance.
Those still require separate dated acceptance evidence.
