# Controller Voice Readiness Cache Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Cache controller voice readiness by normalized voice key instead of only the last selected voice.

**Architecture:** Keep caching local to `_ControllerVoiceReadinessCache`. `refresh_operator_view()` uses cached `get()` results for UI responsiveness, while Start and Submit continue using forced `refresh()` before work.

**Tech Stack:** Python dataclasses, pytest, ruff, mypy.

---

### Task 1: Add Failing Tests

**Files:**
- Modify: `tests/unit/test_controller.py`

- [ ] **Step 1: Add switch-back cache test**

Add near the existing `_ControllerVoiceReadinessCache` tests:

```python
def test_controller_voice_readiness_cache_reuses_prior_voice_after_switching_back() -> None:
    profile, _package = _controller_inputs()
    calls: list[PresenterVoiceSettings] = []

    def checker(
        _profile: object,
        voice: PresenterVoiceSettings,
    ) -> VoiceAssetAvailability | None:
        calls.append(voice)
        return VoiceAssetAvailability(
            status="OK",
            route="windows-sapi-zh",
            detail=f"ready for {voice.language}/{voice.tone}",
        )

    cache = _ControllerVoiceReadinessCache(profile=profile, checker=checker)

    first = cache.get(PresenterVoiceSettings(language="zh", tone="friendly"))
    second = cache.get(PresenterVoiceSettings(language="zh", tone="coach"))
    third = cache.get(PresenterVoiceSettings(language="zh-CN", tone="friendly"))

    assert first == third
    assert second is not None
    assert calls == [
        PresenterVoiceSettings(language="zh", tone="friendly"),
        PresenterVoiceSettings(language="zh", tone="coach"),
    ]
```

- [ ] **Step 2: Add selected-key refresh test**

Add:

```python
def test_controller_voice_readiness_refresh_invalidates_only_selected_voice() -> None:
    profile, _package = _controller_inputs()
    calls: list[PresenterVoiceSettings] = []

    def checker(
        _profile: object,
        voice: PresenterVoiceSettings,
    ) -> VoiceAssetAvailability | None:
        calls.append(voice)
        return VoiceAssetAvailability(
            status="OK",
            route="windows-sapi-zh",
            detail=f"ready call {len(calls)} for {voice.language}/{voice.tone}",
        )

    cache = _ControllerVoiceReadinessCache(profile=profile, checker=checker)

    first = cache.get(PresenterVoiceSettings(language="zh", tone="friendly"))
    coach = cache.get(PresenterVoiceSettings(language="zh", tone="coach"))
    refreshed = cache.refresh(PresenterVoiceSettings(language="zh-CN", tone="friendly"))
    reused_coach = cache.get(PresenterVoiceSettings(language="zh", tone="coach"))

    assert refreshed != first
    assert reused_coach == coach
    assert calls == [
        PresenterVoiceSettings(language="zh", tone="friendly"),
        PresenterVoiceSettings(language="zh", tone="coach"),
        PresenterVoiceSettings(language="zh", tone="friendly"),
    ]
```

- [ ] **Step 3: Add cached None test**

Add:

```python
def test_controller_voice_readiness_cache_preserves_none_results() -> None:
    profile, _package = _controller_inputs()
    calls: list[PresenterVoiceSettings] = []

    def checker(
        _profile: object,
        voice: PresenterVoiceSettings,
    ) -> VoiceAssetAvailability | None:
        calls.append(voice)
        return None

    cache = _ControllerVoiceReadinessCache(profile=profile, checker=checker)

    assert cache.get(PresenterVoiceSettings(language="en")) is None
    assert cache.get(PresenterVoiceSettings(language="en-US")) is None

    assert calls == [PresenterVoiceSettings(language="en")]
```

- [ ] **Step 4: Run RED tests**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_controller.py::test_controller_voice_readiness_cache_reuses_prior_voice_after_switching_back tests\unit\test_controller.py::test_controller_voice_readiness_refresh_invalidates_only_selected_voice tests\unit\test_controller.py::test_controller_voice_readiness_cache_preserves_none_results
```

Expected: the switch-back test fails because the cache only remembers the last selected key. The `None` test may already pass only when the same key is selected consecutively; keep it as a guard.

### Task 2: Implement Multi-Key Cache

**Files:**
- Modify: `src/ai_presenter/runtime/controller.py`

- [ ] **Step 1: Replace single-entry fields**

Change `_ControllerVoiceReadinessCache` fields from:

```python
_cached_key: tuple[str, str] | None = None
_cached_readiness: ControllerVoiceReadiness | None = None
```

to:

```python
_cached_readiness_by_key: dict[tuple[str, str], ControllerVoiceReadiness | None] = field(
    default_factory=dict
)
```

- [ ] **Step 2: Add private helper**

Add:

```python
    def _key(self, voice: PresenterVoiceSettings) -> tuple[str, str]:
        return (voice.language, voice.tone)
```

- [ ] **Step 3: Update `get()`**

Implement:

```python
    def get(self, voice: PresenterVoiceSettings) -> ControllerVoiceReadiness | None:
        key = self._key(voice)
        if key in self._cached_readiness_by_key:
            return self._cached_readiness_by_key[key]
        readiness = _check_controller_voice_readiness(
            self.profile,
            voice,
            checker=self.checker,
        )
        self._cached_readiness_by_key[key] = readiness
        return readiness
```

- [ ] **Step 4: Update `refresh()`**

Implement:

```python
    def refresh(self, voice: PresenterVoiceSettings) -> ControllerVoiceReadiness | None:
        key = self._key(voice)
        readiness = _check_controller_voice_readiness(
            self.profile,
            voice,
            checker=self.checker,
        )
        self._cached_readiness_by_key[key] = readiness
        return readiness
```

- [ ] **Step 5: Run GREEN tests**

Run the RED command again.

Expected: selected tests pass.

### Task 3: Verify, Review, Commit

**Files:**
- Cycle 037 code, tests, and docs

- [ ] **Step 1: Run focused verification**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_controller.py tests\unit\test_controller_view_model.py tests\unit\test_voice.py tests\unit\test_voice_assets.py
.\.venv\Scripts\ruff check --no-cache src\ai_presenter\runtime\controller.py tests\unit\test_controller.py
.\.venv\Scripts\mypy --no-incremental src\ai_presenter\runtime\controller.py tests\unit\test_controller.py
```

- [ ] **Step 2: Request review**

Ask a review subagent to inspect cache key normalization, `refresh()` force behavior, cached `None`, stale-cache risk, and Start/Submit safety.

- [ ] **Step 3: Run full verification**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests
.\.venv\Scripts\ruff check --no-cache .
.\.venv\Scripts\mypy --no-incremental src tests
git diff --check
```

- [ ] **Step 4: Commit**

Stage only Cycle 037 files and commit:

```powershell
git commit -m "perf: cache controller voice readiness"
```
