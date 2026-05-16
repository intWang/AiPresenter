# Cycle 006 Localized Q&A / Aliases Review

Date: 2026-05-16

Verdict: `approved_with_risks`

## Scope Reviewed

- Design: `docs/superpowers/specs/2026-05-16-localized-qa-aliases-design.md`
- Plan: `docs/superpowers/plans/2026-05-16-localized-qa-aliases.md`
- Implementation handoff: `docs/agent-handoffs/cycle-006-implementation.md`
- Changed localized Q&A / alias files:
  - `src/ai_presenter/packages/models.py`
  - `src/ai_presenter/runtime/questions.py`
  - `packages/ringcentral-video.yaml`
  - `tests/unit/test_questions.py`
  - `tests/unit/test_material_packages.py`
  - `docs/knowledge/ringcentral-video/source-index.md`

## Findings By Severity

### Critical

None.

### High

None.

### Medium

None.

### Low

- `tests/unit/test_questions.py` covers package-owned alias matching independent of the legacy table and localized Q&A answer selection, but it does not commit permanent regression coverage for two explicit design contracts: package-owned aliases taking precedence over legacy aliases, and longest package alias winning when multiple package aliases match the same question. I verified both behaviors with an ad hoc runtime probe, so this is a coverage risk rather than a functional blocker.

## Review Notes

- Model compatibility looks good. `QuestionAnswer.localized_questions`, `QuestionAnswer.localized_answers`, and `OperationEntrypoint.question_aliases` are optional via `default_factory=dict`, use the planned YAML aliases, and keep `CamelModel`'s `extra="forbid"` useful for catching misspelled fields.
- Matching behavior follows the design. Q&A matching scans English and localized question strings, localized answers are selected by `voice.language`, package-owned aliases are checked before the legacy `_ENTRYPOINT_ALIASES` fallback, and package aliases use longest-alias selection.
- Safety behavior is preserved. Share, Leave, and Invite still resolve as question targets but remain non-operable through the existing open-step and risky-word checks; the risky policy was not broadened.
- Encoding is acceptable. The reviewed Chinese strings are real UTF-8 CJK text. The only C1-control mojibake-style string found by probe is the intentional negative test input at `tests/unit/test_questions.py:101`.
- `docs/knowledge/ringcentral-video/source-index.md` records the new package-owned localized Q&A / `questionAliases` behavior and notes that legacy Python aliases remain as fallback.

## Verification Run

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py tests\unit\test_questions.py
```

Result: `32 passed in 5.07s`

```powershell
.\.venv\Scripts\python -m ruff check --no-cache src\ai_presenter\packages\models.py src\ai_presenter\runtime\questions.py tests\unit\test_questions.py tests\unit\test_material_packages.py
```

Result: `All checks passed!`

```powershell
.\.venv\Scripts\python -m mypy --no-incremental src\ai_presenter\packages\models.py src\ai_presenter\runtime\questions.py tests\unit\test_questions.py tests\unit\test_material_packages.py
```

Result: `Success: no issues found in 4 source files`

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests
```

Result: `372 passed, 1 warning in 16.91s`

Warning: known `pywinauto` warning, `Revert to STA COM threading mode`.

Additional read-only probes:

- UTF-8/codepoint probe found CJK text in the reviewed Python/YAML/test files, no replacement characters, and C1-control mojibake only in the intentional negative test literal.
- Runtime alias probe returned `demo.package.override` for a package-owned `聊天` alias even when a legacy RingCentral chat id was present, confirming package alias precedence.
- Runtime alias probe returned `demo.long` for `共享屏幕` when both `共享` and `共享屏幕` package aliases existed, confirming longest package alias wins.

## Recommended Next Cycle

- Add committed unit tests for package-owned alias precedence over legacy aliases and longest package alias wins.
- Continue migrating remaining legacy Chinese aliases from `_ENTRYPOINT_ALIASES` into package-owned `questionAliases`.
- Consider a small language-code normalization policy before adding regional variants such as `zh-CN`, so localized answers do not depend only on exact language-key matches.
