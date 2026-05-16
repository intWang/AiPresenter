# Cycle 037 Technical Scan: Controller Voice Readiness Cache

Date: 2026-05-16
Role: technical discovery
Scope: read-only technical scan. No implementation changes were made in this pass.

## Finding

`_ControllerVoiceReadinessCache` currently stores only one cached readiness result:

```python
_cached_key: tuple[str, str] | None = None
_cached_readiness: ControllerVoiceReadiness | None = None
```

This avoids repeated checks only for the most recently selected normalized voice. Toggling `zh/friendly -> zh/coach -> zh/friendly` rechecks `zh/friendly` even though the controller has already checked it.

## Recommended Implementation

Change `_ControllerVoiceReadinessCache` to store a dictionary:

```python
_cached_readiness_by_key: dict[tuple[str, str], ControllerVoiceReadiness | None] = field(default_factory=dict)
```

Then:

- `get(voice)` uses `(voice.language, voice.tone)` as the normalized key.
- `get()` returns the cached value when the key already exists, including cached `None`.
- On a miss, `get()` calls `_check_controller_voice_readiness()`, stores the result, and returns it.
- `refresh(voice)` bypasses only that key, recomputes it, stores it, and returns the fresh result.

## Start/Submit Safety

The existing call sites already force a refresh before work:

- `current_voice_readiness()` calls `voice_readiness_cache.refresh(current_voice())`.
- `start()` calls `current_voice_readiness()` immediately before starting.
- `submit_question()` calls `current_voice_readiness()` immediately before answering/submitting.

Do not change these call sites.

## Tests

Add focused tests in `tests/unit/test_controller.py`:

- `test_controller_voice_readiness_cache_reuses_prior_voice_after_switching_back`
- `test_controller_voice_readiness_refresh_invalidates_only_selected_voice`
- `test_controller_voice_readiness_cache_preserves_none_results`

Keep the existing alias-equivalent cache test.

## Risks

The UI summary can still become stale if voice assets are installed or removed while the controller window is open. That risk already exists for the last-selected voice. It remains acceptable because Start and Submit force a fresh readiness check.

The cache size is naturally tiny: current language/tone choices are bounded.
