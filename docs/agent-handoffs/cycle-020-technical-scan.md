# Cycle 020 Technical Scan: Controller Disabled-Action Reasons

Date: 2026-05-16

## Scope

Scan target: minimal implementation path for human-readable disabled reasons for Start and Submit-like controller actions.

Safety boundary: no production-code edits in this scan. Future implementation should remain unit-testable and should not run live RingCentral or desktop automation.

## Relevant Functions And Classes

- `src/ai_presenter/runtime/controller_view_model.py`
  - `ControllerOperatorSnapshot`: pure input facts for controller UI state.
  - `ControllerButtonStates`: current boolean enablement surface for Start, Pause, End, Refresh, Scan, and Submit.
  - `ControllerOperatorViewModel`: current labels plus `buttons`.
  - `build_controller_operator_view_model()`: central place where target readiness, voice readiness, question text, run/stopping state, labels, and button enablement are derived.
  - `_target_ready()`, `_voice_ready()`, `_scan_label()`, `_question_label()`: helper predicates/labels that should be reused or mirrored for reason text.
- `src/ai_presenter/runtime/controller.py`
  - `run_controller().refresh_operator_view()`: builds `ControllerOperatorSnapshot`, renders the dense `operator_summary`, and applies `view_model.buttons`.
  - `run_controller().start()`: direct Start callback revalidates voice/profile, blocks unscanned running apps, forces fresh voice readiness, then starts the demo.
  - `run_controller().submit_question()`: direct Submit/Return callback blocks empty text, blocks unscanned running apps, forces fresh voice readiness, then answers/queues/starts.
  - `_ControllerVoiceReadinessCache`: passive UI refresh uses cached `get()`, Start/Submit use fresh `refresh()`.
  - `ControllerAppliedStatusState`, `ControllerStatusApplication`, `plan_controller_status_application()`: Cycle 019 status-application helpers; likely unaffected by this slice.
- `tests/unit/test_controller_view_model.py`
  - Best home for new disabled-reason tests because the view model is pure.
- `tests/unit/test_controller.py`
  - Keep for callback/status/cache helpers. Add tests here only if implementation introduces a controller-level summary/reason rendering helper.

## Current Button Enablement Logic

Current gates in `build_controller_operator_view_model()`:

- `target_ready`
  - material package: `material_package_id` and `material_flow_id` are both present.
  - running desktop app: a running app is selected and the selected app has been scanned.
- `voice_ready`
  - true when `voice_readiness is None` or `voice_readiness.status == "OK"`.
  - `None` means no local voice assets are required.
- `question_text_present`
  - true when `question_text.strip()` is non-empty.
- `can_start_new_action`
  - true when the controller is not running and not stopping.

Buttons:

- Start: `can_start_new_action and target_ready and voice_ready`
- Submit: `question_text_present and target_ready and voice_ready and not is_stopping`
- Pause: `is_running and not is_stopping`
- End: `is_running or is_stopping`
- Refresh: `not is_running and not is_stopping`
- Scan: running-app mode, has a running-app selection, and `can_start_new_action`

Important behavior to preserve: Submit can stay enabled while a demo is running, as long as the question has text, target is ready, voice is ready, and the controller is not stopping. That path queues safe interrupts or answers text-only.

## Suggested Data Model/API Changes

Recommended minimal slice: add reason text to the pure view model without changing existing button booleans.

```python
@dataclass(frozen=True)
class ControllerDisabledActionReasons:
    start: str = ""
    submit: str = ""
```

Then add `disabled_reasons: ControllerDisabledActionReasons` to `ControllerOperatorViewModel`.

Rationale:

- Keeps existing `view_model.buttons.start_enabled` and `view_model.buttons.submit_enabled` API stable.
- Avoids rewriting Tk wiring or tests that already assert booleans.
- Keeps disabled-reason derivation colocated with the predicates that already decide enablement.
- Lets `run_controller().refresh_operator_view()` append a compact reason row/string later without inspecting Tk widget states.

Suggested reason precedence:

- Start:
  - stopping: `Controller is ending.`
  - running: `Demo is already running.`
  - running-app mode with no selected app: `Select a running app, then scan it.`
  - running-app mode selected but unscanned: `Scan the selected running app first.`
  - material target missing: `Select a material package and flow.`
  - voice not ready: `Selected voice assets are not ready: {voice_readiness_label}`
  - enabled: empty string
- Submit:
  - stopping: `Controller is ending.`
  - empty or whitespace question: `Enter a question.`
  - running-app mode with no selected app: `Select a running app, then scan it before asking questions.`
  - running-app mode selected but unscanned: `Scan the selected running app before asking questions.`
  - material target missing: `Select a material package and flow.`
  - voice not ready: `Selected voice assets are not ready: {voice_readiness_label}`
  - enabled: empty string

Keep this helper pure, for example `_start_disabled_reason(snapshot, target_ready, voice_ready)` and `_submit_disabled_reason(...)`. Do not make reason derivation call voice asset discovery; use the readiness already present on the snapshot.

## UI Wiring Recommendation

Smallest UI change after the model exists:

- In `refresh_operator_view()`, include reasons only when present, e.g. append ` | Actions: Start blocked: ...; Submit blocked: ...`.
- Avoid splitting the Tk layout in this slice unless the implementation owner explicitly chooses the Cycle 019 readability follow-up. A label-only summary addition is lower risk.
- Keep Start/Submit callbacks as the real guards. The question entry binds Return directly to `submit_question()`, so disabled button state is not the only path into Submit.

## Exact Tests To Add

Add to `tests/unit/test_controller_view_model.py`:

- `test_ready_material_package_has_no_start_reason_and_submit_needs_question`
  - Use the existing ready material package snapshot with empty `question_text`.
  - Assert Start enabled and `disabled_reasons.start == ""`.
  - Assert Submit disabled and `disabled_reasons.submit == "Enter a question."`.
- `test_missing_voice_assets_explain_start_and_submit_disabled`
  - Use material package, `question_text="chat"`, and `ControllerVoiceReadiness(status="FAIL", detail="...Huihui...")`.
  - Assert Start and Submit disabled.
  - Assert both reasons contain `Selected voice assets are not ready` and `Huihui`.
- `test_running_app_unscanned_explains_start_and_submit_scan_required`
  - Use running-app mode, selected app, no scan, and `question_text="chat"`.
  - Assert Start disabled with `Scan the selected running app first.`
  - Assert Submit disabled with `Scan the selected running app before asking questions.`
- `test_running_app_without_selection_explains_select_app_before_actions`
  - Use running-app mode, no selection, no scan, and `question_text="chat"`.
  - Assert Start/Submit disabled and reasons direct the operator to select and scan a running app.
- `test_running_state_explains_start_disabled_but_allows_submit`
  - Use material target, `is_running=True`, `is_stopping=False`, `question_text="chat"`.
  - Assert Start disabled with `Demo is already running.`
  - Assert Submit enabled and `disabled_reasons.submit == ""`.
- `test_ending_state_explains_start_and_submit_disabled`
  - Use material target, `is_running=True`, `is_stopping=True`, `question_text="chat"`.
  - Assert Start and Submit disabled with `Controller is ending.`

Optional only if summary rendering moves into a pure helper:

- `test_render_operator_summary_includes_disabled_action_reasons`
  - Construct a view model with both reasons and assert the rendered summary includes them.

No new `PresenterController` runner tests are needed for the minimal slice because runtime Start/Submit behavior and safety guards should stay unchanged.

## Files Likely Touched

- `src/ai_presenter/runtime/controller_view_model.py`
  - Add `ControllerDisabledActionReasons`.
  - Add `disabled_reasons` to `ControllerOperatorViewModel`.
  - Add pure reason helpers and wire them into `build_controller_operator_view_model()`.
- `src/ai_presenter/runtime/controller.py`
  - Read `view_model.disabled_reasons` in `refresh_operator_view()` and append concise action reason text.
  - No changes expected to `PresenterController`, `plan_controller_status_application()`, `_apply_button_state()`, or voice readiness cache behavior.
- `tests/unit/test_controller_view_model.py`
  - Add the tests above and update any existing direct `ControllerOperatorViewModel` assertions if the dataclass shape changes.
- `tests/unit/test_controller.py`
  - Probably unchanged. Touch only if a pure summary renderer or controller-level reason adapter is introduced.
- `docs/runbooks/ringcentral-manual-acceptance.md`
  - Optional. Update only if visible acceptance wording changes from the current summary-line behavior.

## Edge Cases

- Whitespace-only question text should use the same reason as empty text.
- `voice_readiness=None` means no local assets are required and must not produce a disabled reason.
- If multiple blockers exist, report the first actionable reason using the precedence above; the summary can still show separate scan and voice readiness labels.
- Running app stale scan clearing after Refresh or selection change must continue to block Start/Submit with scan-required reasons.
- Submit while running should remain allowed; do not copy Start's `can_start_new_action` gate to Submit.
- Submit while stopping must remain blocked even if the question and target are ready.
- Direct Return-key submission must keep callback guards and status/chat messages aligned with the disabled reason text.
- Passive 500 ms polling must continue using cached voice readiness; reason helpers must not perform expensive checks.
- Risky question routes remain answer-only via `QuestionSubmitResult.can_operate`; this slice should not make any blocked route executable.

## Verification Commands

Focused future implementation checks:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_controller_view_model.py tests\unit\test_controller.py
.\.venv\Scripts\python -m ruff check --no-cache src\ai_presenter\runtime\controller_view_model.py src\ai_presenter\runtime\controller.py tests\unit\test_controller_view_model.py tests\unit\test_controller.py
.\.venv\Scripts\python -m mypy --no-incremental src tests
git diff --check -- src\ai_presenter\runtime\controller_view_model.py src\ai_presenter\runtime\controller.py tests\unit\test_controller_view_model.py tests\unit\test_controller.py
```

For this scan-only handoff:

```powershell
git diff --check -- docs\agent-handoffs\cycle-020-technical-scan.md
git status --short -- docs\agent-handoffs\cycle-020-technical-scan.md
```

## Key Recommendation

Implement disabled-action reasons as pure view-model output, not as Tk-widget inspection and not as new controller state. Preserve the current `ControllerButtonStates` booleans, add a small `ControllerDisabledActionReasons` value to `ControllerOperatorViewModel`, and render those reasons from `refresh_operator_view()` only after the model owns the logic.
