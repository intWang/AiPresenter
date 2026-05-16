# Cycle 012 Demand Analysis: Voice Profile Preflight

Date: 2026-05-16

## User-Facing Need

Operators can choose voice settings from the CLI and controller, but unsupported combinations should fail before RingCentral is launched or bound. The failure needs to explain which profile/provider cannot support the selected voice.

## Workflows

- `demo --profile ringcentral-video-bind-speaker --language zh-CN --tone friendly` validates and proceeds because the profile can route Chinese to Windows SAPI Chinese.
- `demo --profile ringcentral-video --language zh-CN --tone friendly` fails before desktop automation because the fake speech profile cannot provide Chinese output.
- `controller --profile ringcentral-video --language zh-CN --tone friendly` fails before opening the controller UI.
- The controller Start button blocks invalid UI-selected voice/profile combinations before launching the demo thread.

## Acceptance Criteria

- Compatibility uses `PresenterVoiceSettings` and `validate_profile_voice`; no duplicate compatibility matrix.
- Unsupported combinations fail before `WindowsDesktopDriver`, `ProfileRunner.launch_and_bind`, RingCentral binding, or demo actions.
- Error messages include profile id, configured speech provider, normalized voice label, and required provider guidance.
- Supported fallback routes remain valid.
- Dry-run becomes a compatibility preflight for `demo` and `controller`.
- Focused and full test suites pass.

## Risks

- Fake-provider Chinese dry-runs now fail by design.
- This validates configured routing support, not installed SAPI voices, Piper downloads, virtual mic devices, or OpenAI credentials.
- Avoid adding `run` command voice flags in this cycle.

## Documentation Suggestions

- Add a README compatibility note beside the voice-flag examples.
- Add runbook examples for one passing and one failing preflight.
- Note that regional aliases normalize to English/Chinese families.
