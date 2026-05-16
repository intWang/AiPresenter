# Cycle 012 Technical Scan: Voice Profile Preflight

Date: 2026-05-16

## Existing Seams

- `validate_profile_voice()` in `runtime.voice` is pure and already centralizes compatibility decisions.
- `run_material_demo()` and `run_existing_window_material_demo()` accept `voice`, but currently validate inside `_run_material_demo_on_handle()` after some setup.
- `ControllerSession.set_voice()` and `select_target()` already validate material targets.
- `run_controller()` can validate before importing/creating Tk state.
- `demo` and `controller` CLI commands already resolve `PresenterVoiceSettings` from free-form strings.

## Recommended Changes

- Enrich `validate_profile_voice()` errors with profile/provider/voice context.
- Add CLI compatibility validation after profile load/type check and before dry-run return.
- Add runtime validation before `WindowsDesktopDriver()` and provider registry creation.
- Keep the inner `_run_material_demo_on_handle()` validation as a defensive guard.
- Add controller startup validation before Tk setup and Start-handler validation before demo thread start.

## Test Strategy

- CLI tests proving unsupported dry-run fails and does not call monkeypatched runtime runners.
- Runtime factory tests proving invalid voice fails before desktop/provider setup.
- Controller test proving invalid initial voice fails before desktop/Tk setup.
- Voice test proving enriched error content.
- Existing supported routing tests remain unchanged and green.

## Risks

- Earlier failures can change dry-run behavior for unsupported profile/voice combinations.
- Error strings become more visible; keep existing required-provider phrases as substrings for compatibility.
