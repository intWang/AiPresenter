# Voice Profile Preflight Design

Date: 2026-05-16

## Context

Cycle 011 added `--language` and `--tone` flags to `demo` and `controller`. The flags validate syntax immediately, but profile compatibility is still mostly enforced inside runtime paths. Unsupported combinations, such as Chinese voice with the fake speech profile, should fail before desktop automation launches or the controller UI opens.

## Design

Add early profile/voice compatibility checks at the user-facing and runtime boundaries:

- `validate_profile_voice()` remains the single source of compatibility logic.
- Its error message includes profile id, configured speech provider, normalized voice label, and the existing required provider guidance.
- `demo` and `controller` CLI commands validate the loaded profile and selected voice before dry-run completion or runtime invocation.
- `run_material_demo()` validates before creating `WindowsDesktopDriver`, provider registry, launcher, or bound window.
- `run_existing_window_material_demo()` validates before creating `WindowsDesktopDriver` or a default provider registry.
- `run_controller()` validates its initial voice before constructing desktop/catalog/Tk state.
- The controller Start handler validates the current UI voice against the active profile before marking the session running or starting a worker thread.

## Behavior

- Supported combinations continue to work:
  - English with fake, OpenAI, Piper, Windows SAPI, or Windows SAPI English.
  - Chinese with OpenAI or the Windows SAPI Chinese route.
  - Chinese with Piper or Windows SAPI English remains valid when routing can fall back to `windows-sapi-zh`.
- Unsupported combinations fail before launch/bind side effects.
- CLI dry-runs become a stronger compatibility preflight: an invalid profile/voice combination fails during dry-run instead of reporting success.
- Regional language aliases still normalize to the existing English/Chinese families.

## Non-Goals

- No new voice providers or installed-voice detection.
- No `run` command voice flags.
- No change to package localization.
- No guarantee that a configured SAPI voice is installed on the host; this checks AiPresenter routing compatibility only.

## Acceptance Criteria

- `demo --profile ringcentral-video --language zh-CN --tone friendly --dry-run` fails with a profile/voice compatibility message.
- `controller --profile ringcentral-video --language zh-CN --tone friendly --dry-run` fails with the same compatibility class.
- `run_material_demo()` raises before `WindowsDesktopDriver()` when given an unsupported profile/voice.
- `run_existing_window_material_demo()` raises before `WindowsDesktopDriver()` when given an unsupported profile/voice.
- `run_controller()` raises before `WindowsDesktopDriver()` or Tk setup when given an unsupported initial voice.
- The controller Start handler blocks invalid UI voice choices before starting the demo thread.
- Existing supported voice routing tests still pass.

## Risks

- Existing smoke commands that combine fake speech with Chinese voice now fail by design.
- This may reveal local profile/provider mismatches earlier than before, which is good for correctness but can surprise users relying on dry-run as syntax-only validation.
- Error messages should stay stable enough for tests while preserving useful operator detail.
