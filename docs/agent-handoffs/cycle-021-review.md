# Cycle 021 Review Handoff

## Result

Needs follow-up before acceptance if the safety requirement is interpreted as process-level import isolation.

## Findings

### P2 - `validation-targets` still imports runtime and Windows desktop modules at CLI startup

- Location: `src/ai_presenter/cli.py:12`
- Location: `src/ai_presenter/cli.py:16`
- Location: `src/ai_presenter/runtime/factory.py:9`
- Location: `src/ai_presenter/runtime/controller.py:11`

The new `validation-targets` command body is read-only and only loads the material package plus Markdown docs, but the shared Typer module imports `run_controller`, `run_desktop_profile`, and `run_material_demo` at module import time. Those imports pull in `ai_presenter.desktop.windows` via `runtime.factory` and `runtime.controller` before Typer dispatches to `validation-targets`.

That conflicts with the review focus item "no desktop/runtime/Windows automation imports" under the stricter interpretation. A direct import probe confirmed this:

```powershell
.\.venv\Scripts\python -c "import sys; import ai_presenter.cli; print('ai_presenter.desktop.windows' in sys.modules); print('ai_presenter.runtime.factory' in sys.modules); print('ai_presenter.runtime.controller' in sys.modules)"
```

Result:

```text
True
True
True
```

Recommended fix: lazy-import runtime/controller/factory dependencies inside the commands that execute runtime behavior, or split the offline discovery/listing commands into an import-light CLI surface. Keep `validation-targets` importing only package loading, acceptance discovery, and standard library modules on its execution path.

## Passing Checks

- Spec compliance, aside from the import isolation issue:
  - Default output excludes `Do Not Execute Yet` rows.
  - `--include-blocked` lists `ringcentral.video.more.recording` and `ringcentral.video.toolbar.leave` with `Do not execute` wording.
  - P0 output includes `p0-add-coworkers-modal` and `p0-controller-queued-chat-question`.
  - Add coworkers uses `--entrypoint ringcentral.video.main.add-coworkers`.
  - Group commands omit `--entrypoint`.
  - Output includes `Note: repo-derived planning list only; not live acceptance evidence.`
- Parser behavior:
  - Checklist and evidence parsing are header-based.
  - Unknown checklist ids raise clear errors with the route/group.
  - Duplicate generated target ids raise a clear error.
  - Backtick extraction is scoped to table id cells, not arbitrary prose.
- Safety/privacy:
  - The new discovery module imports only package models plus standard library helpers.
  - The command body does not load a profile, start the controller, run RingCentral, or write acceptance/evidence docs.
- Regression risk:
  - Existing CLI tests passed alongside the new tests.
- Tests:
  - Pure discovery tests and CLI tests cover P0 listing, target detail, unknown targets, unknown checklist references, blocked rows, duplicate ids, and draft command shape.

## Verification

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_validation_targets.py tests\unit\test_cli.py
```

Result:

```text
55 passed in 10.18s
```

```powershell
.\.venv\Scripts\python -m ruff check --no-cache src\ai_presenter\acceptance\validation_targets.py src\ai_presenter\cli.py tests\unit\test_validation_targets.py tests\unit\test_cli.py
```

Result:

```text
All checks passed!
```

Manual smoke:

```powershell
.\.venv\Scripts\ai-presenter validation-targets --package ringcentral-video --priority P0
.\.venv\Scripts\ai-presenter validation-targets --package ringcentral-video --target p0-add-coworkers-modal
.\.venv\Scripts\ai-presenter validation-targets --package ringcentral-video --include-blocked
```

Result:

- P0 smoke listed both required P0 targets and the non-evidence note.
- Target smoke showed Add coworkers cleanup, privacy boundary, and entrypoint draft command.
- Include-blocked smoke listed recording and leave/end rows with do-not-execute wording.

## Residual Risk

- `_parse_first_table()` currently gathers every pipe-starting line in the section rather than stopping at the end of the first contiguous table. Current docs are compatible, but a future second table in the same section could be accidentally parsed.
- Blocked targets still render an `acceptance-draft` command. This is draft-only and currently surrounded by do-not-execute wording, but operators may benefit from an explicit "blocked draft only" label in a later polish pass.

## Recommendation

Address the CLI import isolation issue before marking Cycle 021 accepted under the stated safety/privacy focus. No production code or tests were edited during this review.
