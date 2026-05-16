# Cycle 015 Review: Voice Asset Availability

Date: 2026-05-16

## Review Result

Approved. No scoped findings were reported by the independent reviewer.

## Review Scope

- Windows SAPI provider helper APIs.
- Piper provider helper APIs.
- Runtime `voice_assets` route mapping.
- `doctor` voice-asset diagnostics.
- `voices` matrix and targeted voice checks.
- Tests and documentation for Cycle 015.

## Reviewer Verdict

Verdict: APPROVED.

The reviewer confirmed:

- Provider helpers are read-only and do not download, synthesize, or automate RingCentral.
- SAPI matching follows the same case-insensitive substring behavior as runtime selection.
- Piper checks inspect module discoverability and local `.onnx` / `.onnx.json` files without
  executing Piper.
- `doctor --language/--tone` only adds strict `voice assets` diagnostics after configured voice
  compatibility passes.
- `voices --profile` reports asset status while matrix mode remains exit code 0.
- Targeted `voices --profile --language/--tone` exits nonzero when configured local assets are
  missing.
- Tests use fake or monkeypatched helpers rather than real SAPI, COM, Piper packages, or model files.

## Coordinator Verification

- Focused pytest:
  - `59 passed`
- Scoped ruff:
  - passed
- Scoped mypy:
  - passed, no issues in 10 source files
- Full suite:
  - `443 passed, 1 warning in 20.24s`
  - Warning is the known pywinauto STA COM threading warning.

## Real CLI Spot Checks

- `.venv\Scripts\ai-presenter voices`
  - Exit code 0.
  - Listed language and tone aliases with ASCII-safe Chinese alias output.
- `.venv\Scripts\ai-presenter voices --profile ringcentral-video-bind-speaker`
  - Exit code 0.
  - Reported English and Chinese routes with local SAPI asset status.
- `.venv\Scripts\ai-presenter voices --profile ringcentral-video --language zh-CN --tone friendly`
  - Exit code 1.
  - Reported fake speech provider incompatibility before any local asset check.
- `.venv\Scripts\ai-presenter doctor --profile ringcentral-video-bind-speaker --language zh-CN --tone friendly`
  - Exit code 0 on this machine.
  - Reported `[OK] voice assets: speech=windows-sapi-zh found installed SAPI voice matching Huihui`.

## Residual Risk

Actual SAPI voice names and Piper package/model installation still vary by machine. Cycle 015 keeps
that variability out of tests and reports it as explicit availability status for operators.
