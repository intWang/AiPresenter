# Cycle 005 Controller View-Model Review

Date: 2026-05-16

## Verdict

approved_with_risks

## Findings

### Blocking

None.

### High

None.

### Medium

None.

### Low

- `tests/unit/test_controller_view_model.py`: The scenario tests cover the important button-state and label policies, but they do not assert `run_label`. Because `src/ai_presenter/runtime/controller_view_model.py` carries `run_status` through as `run_label`, this is low risk, but the next view-model expansion should add an assertion so run status remains part of the explicit contract.
- `src/ai_presenter/runtime/controller.py`: `refresh_operator_view()` closes over button variables declared later, but the observed call order is safe. The first immediate call path is `refresh_running_windows()` after widget creation, and the `question.trace_add()` registration happens before `submit_button` creation without any intervening `question.set()`. Future Tk wiring should keep this late-bound dependency in mind.

## Review Notes

- The pure view-model satisfies the design slice: source mode, target, flow, voice, scan status, run status, question outcome, and Start/Pause/End/Refresh/Scan/Submit states are represented in immutable dataclasses and built from plain facts plus `PresenterVoiceSettings`.
- Running-app readiness follows the intended scan policy: no selection is not ready, selected-but-unscanned is not ready and enables Scan, and scanned selection is ready and can enable Start/Submit.
- The tests are meaningful scenario tests rather than private-helper mirrors. They exercise material package mode, running-app scan-required mode, scanned mode, running mode, ending mode, voice labels, question labels, and the main button policy.
- Tk wiring is acceptable. `refresh_operator_view()` is defined before the widgets it touches, but it is not invoked until after the referenced buttons exist. Callback registrations on the source menu, running-app menu, question entry, and buttons do not appear to synchronously call it before widget creation.
- Preserving `controller.render_voice_label()` as a wrapper around the new pure function is acceptable compatibility. It keeps existing imports/tests stable while moving the actual formatting policy into the view-model module.
- The manual runbook checks are sufficient for this cycle and privacy-safe. They ask for generic controller state observations and harmless-app safe/risky-control checks; they do not require capturing credentials, private meeting content, or logs containing sensitive data.

## Verification

- `.\.venv\Scripts\python -m ruff check --no-cache src\ai_presenter\runtime\controller.py src\ai_presenter\runtime\controller_view_model.py tests\unit\test_controller_view_model.py`
  - Result: `All checks passed!`
- `.\.venv\Scripts\python -m mypy --no-incremental src\ai_presenter\runtime\controller.py src\ai_presenter\runtime\controller_view_model.py tests\unit\test_controller_view_model.py`
  - Result: `Success: no issues found in 3 source files`
- `.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_controller.py tests\unit\test_controller_view_model.py`
  - Result: `22 passed in 5.21s`

## Recommended Next Cycle

Run the manual RingCentral controller acceptance checklist, then add a small Tk smoke harness or controller-shell adapter test if the project wants automated protection around button enablement and callback ordering. Also add an explicit `run_label` assertion the next time `tests/unit/test_controller_view_model.py` is touched.
