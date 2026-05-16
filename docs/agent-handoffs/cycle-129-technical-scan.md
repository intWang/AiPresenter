# Cycle 129 Technical Scan Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add focused evidence that Spanish OpenAI presenter behavior is wired end to end after Cycle128 without making real OpenAI or RingCentral calls.

**Architecture:** Keep source behavior unchanged unless a test exposes a real gap. Add evidence around the existing boundaries: `voice.py` normalizes and validates Spanish, `factory.py` resolves the OpenAI speech route and applies `localizedText.es`, `controller.py` and `session.py` forward Spanish voice settings into question demos, and `controller_view_model.py` renders honest Spanish/OpenAI readiness state. Prefer fake registries, fake runners, fake windows, and temporary material packages over live providers or live desktop automation.

**Tech Stack:** Python, pytest, Pydantic material package models, AiPresenter provider registry, Typer CLI tests, Windows desktop abstractions mocked with fakes.

---

## Scan Summary

Cycle128 already promoted Spanish to a limited runtime presenter language for OpenAI-backed speech. Existing committed coverage now verifies:

- `src/ai_presenter/runtime/voice.py`: Spanish aliases, labels, `render_narration_text()` using `localizedText.es`, and `validate_profile_voice()` accepting Spanish only when `resolve_speech_provider_name()` returns `openai`.
- `tests/unit/test_cli.py`: `demo` and `controller` dry-runs accept Spanish with `profiles/ringcentral-video-openai.example.yaml` and reject Spanish local profiles before runtime.
- `tests/unit/test_diagnostics.py`: Spanish OpenAI voice is OK; Spanish local voice is not.

Current uncommitted work by another agent is present in:

- `src/ai_presenter/runtime/controller.py`
- `tests/unit/test_runtime_factory.py`
- `tests/unit/test_controller.py`
- `tests/unit/test_controller_view_model.py`
- `docs/agent-handoffs/cycle-129-demand-analysis.md`
- `docs/agent-handoffs/cycle-129-risk-scan.md`
- `.coverage`

Do not revert or rewrite those changes. They already add useful evidence, and this scan treats them as in-flight baseline work.

Focused verification run during this scan:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_runtime_factory.py::test_existing_window_material_demo_routes_openai_spanish_and_uses_localized_text tests\unit\test_controller.py::test_controller_voice_readiness_rejects_incompatible_voice_before_asset_check tests\unit\test_controller_view_model.py::test_incompatible_spanish_local_voice_explains_start_and_submit_disabled
```

Observed result: `3 passed in 2.78s`.

## Existing In-Flight Evidence To Preserve

`tests/unit/test_runtime_factory.py::test_existing_window_material_demo_routes_openai_spanish_and_uses_localized_text`

- Uses `profiles/ringcentral-video-openai.example.yaml`.
- Sets `profile.providers.narration = "fake"` so no OpenAI narration provider is needed.
- Deletes `OPENAI_API_KEY`.
- Monkeypatches `factory_module.OpenAISpeechProvider` with `FakeOpenAISpeechProvider`.
- Verifies `run_existing_window_material_demo()` routes Spanish to that provider and trims concise `localizedText.es` to the first sentence.
- Limitation: because the test still lets `create_provider_registry()` run, it proves construction is monkeypatched, not that callers can supply a registry to avoid OpenAI provider construction entirely.

`tests/unit/test_controller.py::test_controller_voice_readiness_rejects_incompatible_voice_before_asset_check`

- Verifies `_check_controller_voice_readiness()` rejects Spanish on the bind-speaker local profile before invoking the asset checker.
- This guards against conflating asset availability with provider compatibility.
- Depends on the in-flight `src/ai_presenter/runtime/controller.py::_check_controller_voice_readiness()` change that calls `validate_profile_voice()` before the asset checker and returns a `ControllerVoiceReadiness(status="FAIL", label="FAIL", detail=str(exc))` result for incompatible voices.

`tests/unit/test_controller_view_model.py::test_incompatible_spanish_local_voice_explains_start_and_submit_disabled`

- Verifies the operator view model labels `Spanish / Professional` and disables Start/Submit when readiness says the local route cannot use Spanish.
- This covers the operator-facing boundary for local-provider rejection.

## Remaining Evidence Gap

Add one stricter OpenAI Spanish end-to-end test using an injected registry. The test should prove:

- `run_existing_window_material_demo()` can execute a Spanish OpenAI flow without constructing `OpenAISpeechProvider`.
- The selected speech provider name is `openai`.
- `localizedText.es` is applied before the timeline receives the step.
- No fake RingCentral launch or real desktop bind occurs because an existing fake `WindowHandle` is supplied.

Add one controller/session question test if there is no existing equivalent after the in-flight work lands. The test should prove:

- `PresenterController.submit_question()` forwards `PresenterVoiceSettings(language="es")`.
- Spanish localized Q&A answers or entrypoint aliases are used for text answers.
- Safe question demos use the temporary `question-answer-demo` flow without real runtime execution.

## File Structure

Modify only these implementation-test files in the implementation cycle:

- `tests/unit/test_runtime_factory.py`
  - Add or refine OpenAI Spanish existing-window evidence around `run_existing_window_material_demo()`, `_run_material_demo_on_handle()`, and `_apply_voice_to_adjusted_step()`.

- `tests/unit/test_controller.py`
  - Add controller/session evidence around `PresenterController.submit_question()`, `ControllerSession.set_voice()`, and `create_question_interrupt_step()`.
  - Preserve the current in-flight `_check_controller_voice_readiness()` test.

- `tests/unit/test_controller_view_model.py`
  - Keep the current in-flight local Spanish failure evidence.
  - Add an OpenAI-positive view-model case only if reviewers want explicit `Spanish / Professional | assets: Not required` evidence.

Preserve this in-flight source change if present, because the current controller test relies on it:

- `src/ai_presenter/runtime/controller.py::_check_controller_voice_readiness`
  - It should call `validate_profile_voice(profile, voice)` before `check_voice_asset_availability()`.
  - It should convert incompatible profile/voice combinations into `ControllerVoiceReadiness(status="FAIL", label="FAIL", detail=str(exc))`.
  - It should not call the asset checker for provider-incompatible Spanish local voices.

Do not otherwise modify for this Cycle129 evidence unless tests expose an actual behavioral defect:

- `src/ai_presenter/runtime/factory.py`
- `src/ai_presenter/runtime/session.py`
- `src/ai_presenter/runtime/controller_view_model.py`
- `src/ai_presenter/runtime/voice.py`
- `packages/ringcentral-video.yaml`
- `profiles/*.yaml`
- durable docs under `docs/knowledge/`

## Task 1: Harden Runtime Factory OpenAI Spanish Evidence

**Files:**

- Modify: `tests/unit/test_runtime_factory.py`
- Exercise: `src/ai_presenter/runtime/factory.py::run_existing_window_material_demo`
- Exercise: `src/ai_presenter/runtime/factory.py::_run_material_demo_on_handle`
- Exercise: `src/ai_presenter/runtime/factory.py::_apply_voice_to_adjusted_step`
- Exercise: `src/ai_presenter/runtime/voice.py::render_narration_text`
- Exercise: `src/ai_presenter/runtime/voice.py::resolve_speech_provider_name`

- [ ] **Step 1: Preserve the in-flight test**

Keep `test_existing_window_material_demo_routes_openai_spanish_and_uses_localized_text()` if it is still present. Do not replace it wholesale; it already verifies the default registry path with `OpenAISpeechProvider` monkeypatched.

- [ ] **Step 2: Add an injected-registry test**

Add a new test next to the existing localized Chinese and OpenAI Spanish runtime-factory tests:

```python
def test_existing_window_material_demo_uses_injected_openai_registry_for_spanish(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    profile = load_profile(Path("profiles/ringcentral-video-openai.example.yaml"))
    assert isinstance(profile, DesktopAppProfile)
    profile.providers.narration = "fake"
    handle = WindowHandle("Demo", 123, "DemoWindow", "Demo App")
    run_texts: list[str] = []
    captured_speech_provider_classes: list[str] = []
    package = MaterialPackage.model_validate(
        {
            "appId": "temp.demo.123",
            "appName": "Demo App",
            "version": 1,
            "profileIds": ["ringcentral-video-openai"],
            "operationEntrypoints": [
                {
                    "id": "temp.demo.123.overview",
                    "title": "Overview",
                    "area": "Demo App",
                    "purpose": "Introduce the app.",
                    "openSteps": [],
                }
            ],
            "demoFlows": [
                {
                    "id": "temp-demo",
                    "title": "Temporary demo",
                    "goal": "Introduce a running app.",
                    "steps": [
                        {
                            "id": "overview",
                            "title": "Overview",
                            "action": {
                                "entrypointId": "temp.demo.123.overview",
                                "operation": "explain",
                            },
                            "narration": {
                                "text": "Open settings. Then review options.",
                                "localizedText": {
                                    "es": (
                                        "Abra configuracion. Revise las opciones "
                                        "antes de continuar."
                                    )
                                },
                                "placement": "before",
                            },
                        }
                    ],
                }
            ],
            "manualControls": [],
        }
    )

    class FakeDesktop:
        pass

    class InjectedOpenAISpeechProvider:
        pass

    class FakeTimelineRunner:
        def __init__(self, **kwargs: object) -> None:
            captured_speech_provider_classes.append(
                kwargs["speech_provider"].__class__.__name__
            )

        def run_step(self, step: object) -> StepRunResult:
            narration = getattr(step, "narration")
            run_texts.append(getattr(narration, "text"))
            return StepRunResult(step_id=getattr(step, "id"), skipped=False)

    def fail_provider_construction(*_args: object, **_kwargs: object) -> object:
        raise AssertionError("OpenAISpeechProvider should not be constructed")

    registry = create_fake_provider_registry()
    registry.register_speech("openai", InjectedOpenAISpeechProvider())

    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setattr(factory_module, "WindowsDesktopDriver", FakeDesktop)
    monkeypatch.setattr(factory_module, "OpenAISpeechProvider", fail_provider_construction)
    monkeypatch.setattr(factory_module, "SynchronizedTimelineRunner", FakeTimelineRunner)

    run_existing_window_material_demo(
        profile,
        package,
        "temp-demo",
        handle=handle,
        registry=registry,
        voice=PresenterVoiceSettings(language="es", tone="concise"),
    )

    assert captured_speech_provider_classes == ["InjectedOpenAISpeechProvider"]
    assert run_texts == ["Abra configuracion."]
```

- [ ] **Step 3: Run the new test red/green**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_runtime_factory.py::test_existing_window_material_demo_uses_injected_openai_registry_for_spanish
```

Expected: `1 passed`. If it fails because `create_fake_provider_registry` is not imported, add it to the existing imports from `ai_presenter.runtime.factory`.

## Task 2: Add Controller Question Spanish OpenAI Evidence

**Files:**

- Modify: `tests/unit/test_controller.py`
- Exercise: `src/ai_presenter/runtime/controller.py::PresenterController.submit_question`
- Exercise: `src/ai_presenter/runtime/session.py::create_question_interrupt_step`
- Exercise: `src/ai_presenter/runtime/questions.py::answer_question`
- Exercise: `src/ai_presenter/runtime/voice.py::validate_profile_voice`

- [ ] **Step 1: Add a Spanish OpenAI controller question test**

Add near `test_presenter_controller_starts_safe_question_demo_when_idle()`:

```python
def test_presenter_controller_starts_spanish_openai_question_demo_when_idle() -> None:
    profile = load_profile(Path("profiles/ringcentral-video-openai.example.yaml"))
    assert isinstance(profile, DesktopAppProfile)
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    control = DemoControl()
    calls: list[tuple[str, str, str, DemoControl, PresenterVoiceSettings | None]] = []

    def runner(
        captured_profile: DesktopAppProfile,
        captured_package: MaterialPackage,
        captured_flow_id: str,
        *,
        control: DemoControl,
        voice: PresenterVoiceSettings | None = None,
    ) -> None:
        calls.append(
            (
                captured_profile.id,
                captured_package.app_id,
                captured_flow_id,
                control,
                voice,
            )
        )

    controller = PresenterController(
        profile=profile,
        material_package=package,
        flow_id="meeting-control-map-demo",
        control=control,
        runner=runner,
        voice=PresenterVoiceSettings(language="es"),
    )

    result = controller.submit_question("panel de participantes")
    controller.join(timeout=1)

    assert result.demonstration_status == "started"
    assert result.entrypoint_id == "ringcentral.video.toolbar.participants"
    assert result.can_operate is True
    assert "Participants" in result.answer_text
    assert calls == [
        (
            "ringcentral-video-openai",
            "ringcentral-video",
            "question-answer-demo",
            control,
            PresenterVoiceSettings(language="es"),
        )
    ]
```

This test avoids live RingCentral and OpenAI because the injected `runner` captures the call and returns immediately.

- [ ] **Step 2: Add direct session evidence if desired**

If reviewers ask for explicit session coverage, add a small test near session/controller question tests:

```python
def test_controller_session_accepts_spanish_openai_voice_for_material_target() -> None:
    profile = load_profile(Path("profiles/ringcentral-video-openai.example.yaml"))
    assert isinstance(profile, DesktopAppProfile)
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    session = controller_module.ControllerSession()

    session.set_voice(PresenterVoiceSettings(language="es"))
    session.select_target(
        controller_module.MaterialPackageTarget(
            profile=profile,
            package=package,
            flow_id="meeting-control-map-demo",
        )
    )
    response = session.answer_question("panel de participantes")
    interrupt = session.create_interrupt_step(response)

    assert response.entrypoint_id == "ringcentral.video.toolbar.participants"
    assert response.can_operate is True
    assert interrupt is not None
    assert interrupt.id == "question-ringcentral.video.toolbar.participants"
```

Import `ControllerSession` and `MaterialPackageTarget` directly if the file already prefers explicit imports. The current file imports many controller symbols directly, so direct imports are cleaner than using `controller_module`.

- [ ] **Step 3: Run focused controller tests**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_controller.py::test_presenter_controller_starts_spanish_openai_question_demo_when_idle tests\unit\test_controller.py::test_controller_voice_readiness_rejects_incompatible_voice_before_asset_check
```

Expected: both pass. If the Spanish question matches a different safe entrypoint, adjust the prompt to one of the known `questionAliases.es` values in `packages/ringcentral-video.yaml`, such as `panel de participantes`.

## Task 3: Add OpenAI-Positive Controller View-Model Evidence

**Files:**

- Modify: `tests/unit/test_controller_view_model.py`
- Exercise: `src/ai_presenter/runtime/controller_view_model.py::build_controller_operator_view_model`
- Exercise: `src/ai_presenter/runtime/controller_view_model.py::render_voice_label`

- [ ] **Step 1: Keep the local Spanish failure test**

Preserve `test_incompatible_spanish_local_voice_explains_start_and_submit_disabled()` if it is still present. It is useful operator-facing evidence for the non-OpenAI boundary.

- [ ] **Step 2: Add an OpenAI-ready Spanish view-model test**

Add near the existing ready/not-applicable voice readiness tests:

```python
def test_spanish_openai_view_model_is_startable_without_local_assets() -> None:
    view_model = build_controller_operator_view_model(
        ControllerOperatorSnapshot(
            source_mode="material_package",
            material_package_id="ringcentral-video",
            material_flow_id="meeting-control-map-demo",
            running_app_label="",
            has_running_app_selection=False,
            has_scanned_running_app=False,
            scanned_package_id="",
            scanned_flow_id="",
            voice=PresenterVoiceSettings(language="es"),
            voice_readiness=None,
            run_status="Ready",
            is_running=False,
            is_stopping=False,
            question_text="panel de participantes",
            last_question_outcome="",
        )
    )

    assert view_model.voice_label == "Spanish / Professional"
    assert view_model.voice_readiness_label == "Not required"
    assert view_model.buttons.start_enabled is True
    assert view_model.buttons.submit_enabled is True
    assert view_model.disabled_reasons.start == ""
    assert view_model.disabled_reasons.submit == ""
```

- [ ] **Step 3: Run focused view-model tests**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_controller_view_model.py::test_spanish_openai_view_model_is_startable_without_local_assets tests\unit\test_controller_view_model.py::test_incompatible_spanish_local_voice_explains_start_and_submit_disabled
```

Expected: both pass.

## Task 4: Optional CLI Smoke Evidence Without Live Providers

**Files:**

- Usually no source or test change.
- Exercise: `src/ai_presenter/cli.py::demo`
- Exercise: `src/ai_presenter/cli.py::controller`
- Exercise: `src/ai_presenter/cli.py::voices`

- [ ] **Step 1: Run dry-run and catalog smoke commands**

Run:

```powershell
.\.venv\Scripts\ai-presenter.exe demo --profile profiles/ringcentral-video-openai.example.yaml --package ringcentral-video --flow meeting-control-map-demo --language es --dry-run
.\.venv\Scripts\ai-presenter.exe controller --profile profiles/ringcentral-video-openai.example.yaml --package ringcentral-video --flow meeting-control-map-demo --language es --dry-run
.\.venv\Scripts\ai-presenter.exe voices --profile profiles/ringcentral-video-openai.example.yaml --language es
.\.venv\Scripts\ai-presenter.exe voices --profile profiles/ringcentral-video-bind-speaker.yaml --language es
```

Expected:

- OpenAI `demo --dry-run` exits `0` and reports `Spanish / Professional`.
- OpenAI `controller --dry-run` exits `0` and reports `Spanish / Professional`.
- OpenAI `voices` exits `0` and reports selected voice supported via `openai`.
- Bind-speaker `voices` exits nonzero and reports Spanish requires `openai`.

Do not run live `demo` or live `controller` from this evidence cycle.

## Task 5: Final Verification Bundle

Run the focused tests that cover the whole Spanish/OpenAI no-live-call boundary:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_voice.py::test_voice_validation_allows_spanish_openai_profile tests\unit\test_voice.py::test_voice_validation_rejects_spanish_non_openai_profiles tests\unit\test_voice.py::test_render_narration_text_prefers_localized_spanish_script_without_prefix tests\unit\test_runtime_factory.py::test_existing_window_material_demo_routes_openai_spanish_and_uses_localized_text tests\unit\test_runtime_factory.py::test_existing_window_material_demo_uses_injected_openai_registry_for_spanish tests\unit\test_controller.py::test_presenter_controller_starts_spanish_openai_question_demo_when_idle tests\unit\test_controller.py::test_controller_voice_readiness_rejects_incompatible_voice_before_asset_check tests\unit\test_controller_view_model.py::test_incompatible_spanish_local_voice_explains_start_and_submit_disabled tests\unit\test_controller_view_model.py::test_spanish_openai_view_model_is_startable_without_local_assets tests\unit\test_cli.py::test_demo_openai_profile_accepts_spanish_dry_run tests\unit\test_cli.py::test_controller_openai_profile_accepts_spanish_dry_run tests\unit\test_cli.py::test_voices_targeted_openai_spanish_profile_is_supported tests\unit\test_diagnostics.py::test_diagnostics_reports_spanish_openai_voice_supported tests\unit\test_diagnostics.py::test_diagnostics_reports_spanish_local_voice_unsupported
```

Then run:

```powershell
git diff --check
git status --short
```

Expected:

- Focused pytest bundle passes.
- `git diff --check` exits `0`, aside from any pre-existing line-ending warnings already present in the working tree.
- `git status --short` shows only intentional test edits plus pre-existing `.coverage`; no source, package YAML, profile YAML, or durable docs should be modified.

## Risks And Guardrails

- Do not instantiate real `OpenAISpeechProvider` in tests that claim no OpenAI calls. Use an injected `ProviderRegistry` and make provider construction raise if accidentally called.
- Do not call `run_material_demo()` for no-live-call evidence; it creates a `WindowsDesktopDriver` and launches/binds through the profile runner. Use `run_existing_window_material_demo()` with a fake `WindowHandle`.
- Do not use the fake/local RingCentral profiles as Spanish success evidence. Spanish is intentionally OpenAI-only after Cycle128.
- Do not use `voice_readiness=None` to imply local assets exist. In the view model, `None` means no local asset preflight is required, which is correct for OpenAI.
- Do not edit `packages/ringcentral-video.yaml` for this evidence. Spanish `localizedText.es`, Q&A, and aliases already exist.
- Do not add live acceptance claims. These tests prove code paths and provider boundaries, not real OpenAI audio quality or live RingCentral behavior.
- Be careful with the current uncommitted tests in the worktree. Merge around them, and do not revert them unless the owning agent or user explicitly asks.

## Suggested Commit Scope

Commit only the test evidence after it passes:

```powershell
git add tests\unit\test_runtime_factory.py tests\unit\test_controller.py tests\unit\test_controller_view_model.py
git commit -m "test: cover Spanish OpenAI runtime path"
```

Leave `.coverage` unstaged unless the cycle owner explicitly wants regenerated coverage data committed.
