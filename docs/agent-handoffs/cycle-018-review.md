# Cycle 018 Review

Date: 2026-05-16
Role: review worker
Write scope: this file only

## Findings

### P1 - `--output` silently overwrites existing files, including `acceptance-runs.md`

- Location: `src/ai_presenter/cli.py:272`-`src/ai_presenter/cli.py:273`
- The command creates the parent directory and then calls `output.write_text(draft, encoding="utf-8")` with no existence check, no confirmation, and no refusal for evidence-log-looking paths. A safe temp-file probe showed that an existing file named `acceptance-runs.md` was replaced by the draft.
- This does not append to `acceptance-runs.md`, so it satisfies the narrow "no automatic append" rule, but it creates a more serious operator safety failure: a mistyped `--output docs\knowledge\ringcentral-video\acceptance-runs.md` can erase historical acceptance evidence.
- Suggested fix: fail if `--output` already exists unless an explicit force flag is added later. Given this is an evidence-adjacent helper, also consider refusing basename `acceptance-runs.md` or requiring a draft-specific filename.

### P2 - Current CLI file contains behavior changes outside the acceptance-draft scope

- Location: `src/ai_presenter/cli.py:114`-`src/ai_presenter/cli.py:151`, `src/ai_presenter/cli.py:159`-`src/ai_presenter/cli.py:196`, `src/ai_presenter/cli.py:281`-`src/ai_presenter/cli.py:340`, `src/ai_presenter/cli.py:364`-`src/ai_presenter/cli.py:390`
- The plan says existing `run`, `demo`, `controller`, `flows`, `entrypoints`, `voices`, and `doctor` behavior should remain unchanged. The current `cli.py` also adds voice options/validation to `demo`, `controller`, and `doctor`, plus a new `voices` command.
- In this multi-worker workspace I cannot attribute these changes to the acceptance-draft implementation. If they are from another accepted cycle, this is not an acceptance-draft defect. If they came from the acceptance-draft patch, they are out of scope and should be separated before merge.
- The new CLI tests cover these voice behaviors, so they appear intentional somewhere in the workspace; the risk is review/merge scope contamination rather than an observed test failure.

## Non-Blocking Observations

- Renderer purity looks good. `src/ai_presenter/acceptance/manual_record.py` imports dataclasses, collections, and package model types only; it does not import runtime, controller, desktop, diagnostics, pywinauto, or filesystem APIs.
- The draft avoids overclaiming acceptance: it uses "Draft only", says no live RingCentral action was performed, leaves `Pass/fail` blank, includes a proof-order reminder, and the renderer test asserts `"Accepted" not in draft`.
- Flow/entrypoint mismatch and unknown target errors are clear. CLI probes returned nonzero with `Entrypoint ringcentral.video.toolbar.chat is not used by selected flow vbg-blur-demo.` and `Unknown operation entrypoint: missing`.
- Tests are meaningful for the pure renderer and happy-path CLI behavior. Safety-critical gaps remain around overwrite behavior, CLI-level unknown entrypoint, CLI-level flow/entrypoint mismatch, and drift between `required_manual_acceptance_fields()` and the actual `acceptance-runs.md` template.

## Open Questions/Risks

- Should `acceptance-draft --output` ever be allowed to target `acceptance-runs.md`? The spec says not to append automatically and not to special-case it, but the overwrite behavior makes this filename uniquely risky.
- Is the broad voice-related CLI diff part of a separate completed cycle? If yes, keep it out of the acceptance-draft review gate. If no, it violates the "existing CLI behavior remains unchanged" acceptance criterion.
- The CLI module still imports runtime/controller modules at app import time because of existing commands. The new renderer is pure, but invoking the shared CLI entrypoint is not import-isolated from runtime modules.

## Verification Commands/Results

- `.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_acceptance_manual_record.py` -> `7 passed in 1.84s`
- `.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_cli.py` -> `39 passed in 7.17s`
- `.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests` -> `462 passed, 1 warning in 22.45s`; warning was existing pywinauto STA warning.
- `.\.venv\Scripts\python -m ruff check --no-cache .` -> `All checks passed!`
- `.\.venv\Scripts\python -m mypy --no-incremental src tests` -> `Success: no issues found in 77 source files`
- `git diff --check -- src\ai_presenter\acceptance\__init__.py src\ai_presenter\acceptance\manual_record.py src\ai_presenter\cli.py tests\unit\test_acceptance_manual_record.py tests\unit\test_cli.py docs\runbooks\ringcentral-manual-acceptance.md` -> exit 0, with CRLF normalization warnings only.
- Safe temp overwrite probe: existing temp `acceptance-runs.md` containing sentinel text was overwritten by `.\.venv\Scripts\ai-presenter acceptance-draft --package ringcentral-video --entrypoint ringcentral.video.main.add-coworkers --output <temp>\acceptance-runs.md`.

## Review Result

There is one blocking safety finding before I would ship the helper as an evidence-adjacent CLI: `--output` should not silently overwrite existing files. Apart from that, the renderer is pure, the generated wording is appropriately draft-only, and the focused/full verification suite is green.
