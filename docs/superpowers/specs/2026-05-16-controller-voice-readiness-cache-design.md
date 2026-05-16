# Controller Voice Readiness Cache Design

Date: 2026-05-16

## Goal

Reduce repeated controller voice asset checks when an operator toggles between previously selected language/tone choices.

## Context

The Tk controller refreshes its operator summary whenever voice controls or question text change. The summary uses `_ControllerVoiceReadinessCache.get()` so the UI does not repeatedly probe local voice assets for the same selected voice. The current cache stores only the last selected voice, so returning to a prior voice re-runs the checker.

## Design

Replace the single-entry cache with a dictionary scoped to one `_ControllerVoiceReadinessCache` instance.

The cache key is `(voice.language, voice.tone)`. `PresenterVoiceSettings` already normalizes aliases, so `zh-CN` and `zh` both use `zh`, and `warm` and `friendly` both use `friendly`.

`get(voice)` returns cached readiness when the key exists. It must treat cached `None` as a valid cached value, because `None` means no voice asset check is required.

`refresh(voice)` forces a recheck for exactly the selected key and overwrites that key. It must not return stale cached values. It also should not clear unrelated keys.

## Behavior Contract

- Voice readiness cache lifetime remains limited to the controller session.
- Start and Submit keep forcing `refresh()` before work.
- The operator summary can use cached `get()` results for UI responsiveness.
- Checker exceptions still become cached `FAIL` readiness values through `_check_controller_voice_readiness()`.
- Voice compatibility, voice asset discovery, package behavior, localization readiness, and RingCentral routes do not change.

## Tests

Add tests proving:

- `zh/friendly -> zh/coach -> zh-CN/friendly` calls the checker only twice.
- `refresh(zh-CN/friendly)` rechecks `zh/friendly` but leaves `zh/coach` cached.
- cached `None` readiness is reused instead of triggering repeated checks.

## Out Of Scope

- No global cache.
- No cache TTL.
- No provider routing changes.
- No live Tk visual changes.
- No wall-clock performance assertion.
