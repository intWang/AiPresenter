# Cycle 037 Summary: Controller Voice Readiness Cache

Date: 2026-05-16
Cycle: 037
Commit target: `perf: cache controller voice readiness`

## Outcome

Cycle 037 changed `_ControllerVoiceReadinessCache` from a single-entry cache to a per-controller-session dictionary keyed by normalized `(language, tone)`.

The controller operator summary can now reuse prior readiness checks when an operator toggles between language/tone choices and returns to an already checked voice. Start and Submit still force a fresh readiness check before work begins.

## Files Changed

- `src/ai_presenter/runtime/controller.py`
- `tests/unit/test_controller.py`
- `docs/agent-handoffs/cycle-037-demand-analysis.md`
- `docs/agent-handoffs/cycle-037-technical-scan.md`
- `docs/agent-handoffs/cycle-037-review.md`
- `docs/agent-handoffs/cycle-037-summary.md`
- `docs/superpowers/specs/2026-05-16-controller-voice-readiness-cache-design.md`
- `docs/superpowers/plans/2026-05-16-controller-voice-readiness-cache.md`

## Behavior

- `get()` returns cached readiness by `(voice.language, voice.tone)`.
- `get()` treats cached `None` as a valid cached result.
- `refresh()` rechecks only the selected key and overwrites that entry.
- `zh-CN` shares the `zh` key through existing `PresenterVoiceSettings` normalization.
- The cache remains private instance state with `init=False`.
- No provider routing, voice asset detection, UI layout, package, localization, or RingCentral route behavior changed.

## TDD And Review

Red phase:

- `test_controller_voice_readiness_cache_reuses_prior_voice_after_switching_back` failed because the one-slot cache rechecked `zh/friendly` after selecting `zh/coach`.
- `test_controller_voice_readiness_refresh_invalidates_only_selected_voice` failed because refreshing `zh/friendly` displaced the cached `zh/coach` result.
- `test_controller_voice_readiness_cache_preserves_none_results` passed under the old same-key behavior and remains as a guard.

Green phase:

- Replaced `_cached_key` / `_cached_readiness` with `_cached_readiness_by_key`.
- Updated `get()` and `refresh()` to use normalized key lookup and selected-key overwrite.

Review:

- Reviewer found no critical or important issues.
- Reviewer suggested `init=False` for the private dict field; applied and rechecked.

## Verification

Focused verification:

- `.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_controller.py tests\unit\test_controller_view_model.py tests\unit\test_voice.py tests\unit\test_voice_assets.py`
  - `82 passed`
- `.\.venv\Scripts\ruff check --no-cache src\ai_presenter\runtime\controller.py tests\unit\test_controller.py`
  - `All checks passed!`
- `.\.venv\Scripts\mypy --no-incremental src\ai_presenter\runtime\controller.py tests\unit\test_controller.py`
  - `Success: no issues found in 2 source files`

Full verification before summary:

- `.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests`
  - `555 passed, 1 warning`
- `.\.venv\Scripts\ruff check --no-cache .`
  - `All checks passed!`
- `.\.venv\Scripts\mypy --no-incremental src tests`
  - `Success: no issues found in 81 source files`
- `git diff --check`
  - Only LF-to-CRLF working-copy warnings were reported; no whitespace errors.

## Next Handoff Ideas

- Add a small tone-alias cache test for `warm` and `friendly` if voice alias behavior changes later.
- Consider a future visual smoke path for the controller summary after long-session toggling, without running live RingCentral automation.
