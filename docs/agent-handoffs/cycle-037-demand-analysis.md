# Cycle 037 Demand Analysis: Controller Voice Readiness Cache

Date: 2026-05-16
Role: demand discovery
Scope: read-only demand analysis. No implementation changes were made in this pass.

## Recommended Slice

Cache controller voice readiness by normalized `(language, tone)` key instead of only the last selected voice.

## User Value

The controller already surfaces voice asset readiness and blocks unsafe Start/Submit paths. The current cache is one-slot, so it avoids repeated checks only while the same voice remains selected. When an operator compares `Chinese / Friendly`, `Chinese / Coach`, then returns to `Chinese / Friendly`, the controller repeats local voice asset discovery.

This slice makes language/tone toggling feel smoother in the live controller while preserving the safety rule that Start and Submit force a fresh readiness check before work begins.

## Minimum Scope

- Replace the single cached key/readiness pair in `_ControllerVoiceReadinessCache` with a per-controller-session dictionary.
- Key by canonical `PresenterVoiceSettings.language` and `PresenterVoiceSettings.tone`.
- Preserve alias reuse, such as `zh-CN` and `zh` sharing the same `zh` cache key.
- Preserve `refresh(voice)` as a forced recheck for only the selected key.
- Do not add module-level, profile-level, disk, or LRU caching.

## Must Preserve

- Start and Submit still recheck readiness before triggering work.
- Voice compatibility remains separate from asset readiness.
- `None` readiness remains a valid cached result.
- Checker exceptions still become `FAIL` readiness values.
- Existing summary labels, disabled reasons, running-app scan behavior, localization behavior, and package routes do not change.

## Suggested Tests

- Returning to a previously selected normalized key reuses cached readiness.
- Alias-equivalent voices share a cache entry.
- `refresh(voice)` recomputes only that normalized key while leaving other cached voice keys reusable.
- `None` readiness is cached and not treated as a missing cache entry.

## Out Of Scope

- No provider routing changes.
- No SAPI/Piper discovery changes.
- No controller layout changes.
- No package YAML or RingCentral route changes.
- No wall-clock performance assertion.
