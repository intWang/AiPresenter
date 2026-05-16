# Cycle 025 Technical Scan: RingCentral Localization Coverage Guard

Date: 2026-05-16
Scope: Review only. No production code changes.

## Current State

- `packages/ringcentral-video.yaml` has 27 entrypoints, 4 demo flows, and 8 Q&A items.
- Programmatic coverage scan:
  - `vbg-blur-demo`: 4/4 steps have `narration.localizedText.zh`.
  - `meeting-basics-demo`: 3/3 steps have `narration.localizedText.zh`.
  - `meeting-controls-tour`: 0/22 steps have `narration.localizedText.zh`.
  - `meeting-control-map-demo`: 22/22 steps have `narration.localizedText.zh`.
  - Q&A: 8/8 items have `localizedQuestions.zh` and `localizedAnswers.zh`.
  - Aliases: 15/27 entrypoints have package-owned `questionAliases.zh`; 49 indexed Chinese aliases total.
- `src/ai_presenter/packages/models.py` already supports localized narration, localized Q&A, and package-owned aliases.
- `src/ai_presenter/runtime/voice.py` already prefers localized narration via `render_narration_text()`. Localized tone behavior is intentionally narrow: only `concise` truncates to the first sentence.
- `src/ai_presenter/runtime/questions.py` already prefers package-owned aliases before the legacy `_ENTRYPOINT_ALIASES` table, and localized Q&A answers bypass tone transformation.

## Smallest Cycle 025 Implementation Path

Do a package-content slice plus one sustainable coverage guard. No runtime change is needed.

1. Add or replace a single generalized test in `tests/unit/test_material_packages.py`:
   - Load `packages/ringcentral-video.yaml`.
   - For every RingCentral demo flow, assert every step has nonblank `step.narration.localized_text["zh"]`.
   - Assert each Chinese script contains at least one CJK character.
   - Keep the current ASCII assertion for `step.narration.text`.
   - This can supersede the narrower short-flow and control-map-only coverage assertions, avoiding duplicate test drift.
2. Add `narration.localizedText.zh` to all 22 `meeting-controls-tour` steps in `packages/ringcentral-video.yaml`.
3. Add one focused render assertion in `tests/unit/test_voice.py` or keep it in `tests/unit/test_material_packages.py`:
   - Pick a newly localized `meeting-controls-tour` step.
   - Assert `render_narration_text(..., PresenterVoiceSettings(language="zh"))` returns the authored `zh` script.
   - Assert `tone="concise"` returns only the first localized sentence for one multi-sentence step if the new copy has multiple sentences.

Recommended verification:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py tests\unit\test_voice.py tests\unit\test_questions.py
.\.venv\Scripts\python -m ruff check --no-cache src\ai_presenter\packages src\ai_presenter\runtime tests\unit\test_material_packages.py tests\unit\test_voice.py tests\unit\test_questions.py
git diff --check -- packages\ringcentral-video.yaml tests\unit\test_material_packages.py tests\unit\test_voice.py
```

## Pitfalls

- Duplicate tests: current tests separately cover short flows and `meeting-control-map-demo`; adding another narrow `meeting-controls-tour` test would create three places to update. Prefer one all-flow guard.
- Dirty multi-cycle workspace: many package, runtime, provider, CLI, test, and docs files are already modified or untracked. Review final diffs by explicit file path, not broad git status.
- UTF-8/mojibake: package files contain valid Chinese, but PowerShell output can display mojibake unless `PYTHONIOENCODING=utf-8` is set. Judge file content and test assertions, not legacy console rendering.
- Long-tour overlap: `meeting-controls-tour` largely duplicates `meeting-control-map-demo`, but it is still a public flow and includes an explicit `explain-invite` step while the control-map flow uses a final summary instead. Localize it or retire/alias it; leaving it half-supported keeps Chinese fallback quality inconsistent.
- Future languages: `PresenterLanguage` is currently `en | zh`; a hardcoded `zh` guard is appropriate for Cycle 025, but future languages should move toward a declared required-language list rather than copying tests per language.
- Runtime fallback: do not rely on `_render_chinese()` for this flow. It is keyword replacement over English, not translation.

## Recommendation

Make Cycle 025 a no-runtime package hardening pass: fully localize `meeting-controls-tour` in YAML and replace the fragmented coverage assertions with a single all-flow Chinese narration guard. Defer model/runtime changes until there is a concrete requirement for more languages or per-tone localized copy.
