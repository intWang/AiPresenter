# Cycle 029 Technical Scan: Stable Validation Target IDs

Date: 2026-05-16
Role: technical discovery
Scope: review-only. No production code was edited during this scan; this handoff is the only file added.

## Recommendation

Implement a small RingCentral knowledge-package slice: add explicit stable validation target IDs to
`docs/knowledge/ringcentral-video/validation-checklist-index.md` and teach
`validation-targets` to prefer those explicit IDs when the checklist provides them.

This is worth doing now because `validation-targets --target ...` is already useful for operator
and subagent handoffs, but current IDs are derived from human-facing labels such as
`P0 + Add coworkers modal`. As the checklist wording matures, label-derived IDs will become brittle
references in prompts, runbooks, tests, and acceptance drafts.

## Current State

- `src/ai_presenter/acceptance/validation_targets.py:15` defines the Priority Checklist required
  headers without `Target ID`.
- `src/ai_presenter/acceptance/validation_targets.py:176` parses the Priority Checklist and
  currently sets `ValidationTarget.id` with `_target_id(row["priority"], route_or_group)`.
- `src/ai_presenter/acceptance/validation_targets.py:214` parses blocked rows and currently sets
  blocked IDs with `blocked-{_slug(route_or_group)}`.
- `src/ai_presenter/acceptance/validation_targets.py:285` already allows markdown tables to contain
  extra columns because `_parse_first_table` maps only required headers into each row. That means
  adding a docs column is safe, but the parser needs an explicit optional-column path before it can
  use the new value.
- `src/ai_presenter/acceptance/validation_targets.py:373` already rejects duplicate final target
  IDs, so duplicate explicit IDs can reuse this validation once explicit IDs are assigned before
  `_validate_unique_target_ids`.
- `src/ai_presenter/cli.py:290` passes all discovery errors through `typer.BadParameter`, so blank
  or duplicate target ID failures will already surface cleanly in the CLI.
- `tests/unit/test_validation_targets.py:43` and `tests/unit/test_cli.py:636` currently assert the
  generated IDs, so they should be updated to assert explicit IDs once the docs table changes.
- `docs/knowledge/ringcentral-video/validation-checklist-index.md:16` has no stable target ID
  column in either `Priority Checklist` or `Do Not Execute Yet`.

## Minimal Code Changes

Modify only `src/ai_presenter/acceptance/validation_targets.py`.

1. Keep `Target ID` optional, not required.

Do not add it to `_REQUIRED_CHECKLIST_HEADERS` or `_REQUIRED_BLOCKED_HEADERS`; older or external
checklists without this column should continue to parse and fall back to generated IDs.

2. Extend `_parse_first_table` with optional headers.

Recommended shape:

```python
def _parse_first_table(
    section: str,
    required_headers: tuple[str, ...],
    section_name: str,
    optional_headers: tuple[str, ...] = (),
) -> list[dict[str, str]]:
    ...
    for required_header in required_headers:
        ...
        row[normalized] = cells[cell_index] if cell_index < len(cells) else ""
    for optional_header in optional_headers:
        normalized = _normalize_header(optional_header)
        if normalized not in header_index:
            continue
        cell_index = header_index[normalized]
        row[normalized] = cells[cell_index] if cell_index < len(cells) else ""
```

This preserves old behavior for existing callers while allowing a caller to distinguish:

- header absent: `"target id" not in row`, so use fallback generated ID;
- header present but blank cell: `row["target id"] == ""`, so reject as an authoring error.

3. Add one helper for explicit-or-generated IDs.

Recommended behavior:

```python
def _target_id_from_row(row: Mapping[str, str], fallback_id: str, route_or_group: str) -> str:
    if "target id" not in row:
        return fallback_id
    explicit_id = _strip_backticks(row["target id"]).strip()
    if not explicit_id:
        raise ValueError(f"blank validation target id for {route_or_group}")
    return explicit_id
```

Keep the explicit ID exactly as authored after trimming optional backticks and whitespace. Do not
slugify explicit IDs; this avoids silently changing operator-facing keys. Let the docs and tests use
lowercase ASCII hyphen IDs. A stricter regex can be added later if the project wants schema-like
validation.

4. Use the helper in both parser paths.

Priority rows:

```python
rows = _parse_first_table(
    section,
    _REQUIRED_CHECKLIST_HEADERS,
    "Priority Checklist",
    optional_headers=("Target ID",),
)
...
id=_target_id_from_row(
    row,
    _target_id(row["priority"], route_or_group),
    route_or_group,
)
```

Blocked rows:

```python
rows = _parse_first_table(
    section,
    _REQUIRED_BLOCKED_HEADERS,
    "Do Not Execute Yet",
    optional_headers=("Target ID",),
)
...
id=_target_id_from_row(
    row,
    f"blocked-{_slug(route_or_group)}",
    route_or_group,
)
```

The existing `_validate_unique_target_ids` should then catch duplicate explicit IDs across priority
and blocked targets when `--include-blocked` is used.

## Minimal Docs Changes

Modify `docs/knowledge/ringcentral-video/validation-checklist-index.md`.

Add `Target ID` as the second column in both tables:

```markdown
| Priority | Target ID | Route Or Group | Entrypoints | Current State | Validate | Cleanup | Privacy Boundary | Record Result |
```

```markdown
| Route | Target ID | Entrypoint | Reason |
```

Suggested IDs:

| Current generated ID | Suggested stable ID |
| --- | --- |
| `p0-add-coworkers-modal` | `rcv-add-coworkers-modal` |
| `p0-controller-queued-chat-question` | `rcv-controller-chat-question` |
| `p1-app-shell-launch` | `rcv-app-shell-launch` |
| `p1-top-bar-coordinate-routes` | `rcv-top-bar-coordinate-routes` |
| `p1-common-toolbar-panels-and-pickers` | `rcv-common-toolbar-panels` |
| `p1-more-occurrence-routes` | `rcv-more-occurrence-routes` |
| `p1-notes-and-transcript` | `rcv-notes-transcript` |
| `p2-media-controls` | `rcv-media-controls` |
| `p2-reactions-and-raise-hand` | `rcv-reactions-raise-hand` |
| `p2-settings-and-background` | `rcv-settings-background` |
| `p3-overview-and-explain-only-context` | `rcv-overview-context` |
| `blocked-recording` | `rcv-blocked-recording` |
| `blocked-leave-or-end-meeting` | `rcv-blocked-leave` |

Do not include priority in the stable IDs. Priorities can change as evidence improves, while the
operator target should remain stable.

## Minimal Test Changes

Modify `tests/unit/test_validation_targets.py`.

- Update real RingCentral checklist tests to use the new explicit IDs:
  - `target_by_id(catalog, "rcv-add-coworkers-modal")`
  - `target_by_id(catalog, "rcv-controller-chat-question")`
  - blocked targets `rcv-blocked-recording` and `rcv-blocked-leave`
- Rename or revise `test_discover_validation_targets_rejects_duplicate_generated_ids` so it
  explicitly covers duplicate final IDs. Use two rows with the same `Target ID`, and expect:

```text
duplicate validation target id: rcv-add-coworkers-modal
```

- Add a blank explicit ID test. It should prove that when the `Target ID` column exists, blank cells
  do not fall back to generated slugs:

```python
with pytest.raises(ValueError, match="blank validation target id for Add coworkers modal"):
    discover_catalog(checklist_text=checklist_text_with_blank_target_id)
```

- Add a fallback compatibility test using a synthetic checklist without a `Target ID` column. It
  should still discover the generated legacy ID, for example `p0-add-coworkers-modal`.
- Keep the unknown package ID test unchanged except for the surrounding table shape if the fixture
  gains a `Target ID` column.

Modify `tests/unit/test_cli.py`.

- Update `test_validation_targets_lists_ringcentral_targets` to assert explicit P0 IDs:

```text
rcv-add-coworkers-modal
rcv-controller-chat-question
```

- Update `test_validation_targets_detail_outputs_draft_command` to call:

```text
--target rcv-add-coworkers-modal
```

- Update missing-target available ID assertions to show the explicit ID list.
- If desired, add one CLI-level regression that a temporary checklist without `Target ID` still
  accepts `--target p0-add-coworkers-modal`. The helper-level fallback test is enough for the
  minimum slice, but a CLI test gives extra confidence in the custom `--checklist` path.

## Duplicate And Blank ID Behavior

Recommended contract:

- If the table has no `Target ID` header, generate the ID exactly as today. This preserves custom
  checklist compatibility.
- If the table has a `Target ID` header and the row value is blank or only backticks/whitespace,
  raise `ValueError("blank validation target id for <route>")`.
- If two rows resolve to the same final ID, whether explicit or fallback, keep raising
  `ValueError("duplicate validation target id: <id>")`.
- Duplicate detection should occur after optional blocked rows are added, so a blocked ID cannot
  collide with a priority ID when `include_blocked=True`.
- Do not auto-prefix, slugify, lowercase, or otherwise transform explicit IDs beyond trimming
  optional backticks and whitespace.

## Fallback Compatibility

The fallback path should remain a permanent behavior, not only a migration aid. It keeps
`validation-targets --checklist <temp-file>` useful for older scans, external packages, and
subagent-generated scratch checklists.

The key implementation detail is preserving absence-vs-blank:

- missing header: no `"target id"` key in the parsed row, fallback allowed;
- present header with empty cell: `"target id"` key exists with an empty value, fallback rejected.

## Out Of Scope

- Do not change package entrypoint IDs or demo flow IDs.
- Do not change `acceptance_draft_command`; it should keep using the human checklist label for
  `--checklist-target`.
- Do not write or promote evidence in `acceptance-runs.md`.
- Do not add JSON output or a checklist schema command in this cycle.
- Do not introduce live RingCentral interactions.

## Verification To Run

Focused RED/GREEN during implementation:

```powershell
.\.venv\Scripts\python -m pytest tests\unit\test_validation_targets.py::test_discover_validation_targets_reads_priority_checklist_rows --no-cov
.\.venv\Scripts\python -m pytest tests\unit\test_validation_targets.py::test_discover_validation_targets_rejects_duplicate_validation_target_ids tests\unit\test_validation_targets.py::test_discover_validation_targets_rejects_blank_explicit_target_id tests\unit\test_validation_targets.py::test_discover_validation_targets_falls_back_to_generated_ids_without_target_id_header --no-cov
```

Affected tests:

```powershell
.\.venv\Scripts\python -m pytest tests\unit\test_validation_targets.py tests\unit\test_cli.py::test_validation_targets_lists_ringcentral_targets tests\unit\test_cli.py::test_validation_targets_detail_outputs_draft_command tests\unit\test_cli.py::test_validation_targets_rejects_unknown_target_with_available_ids tests\unit\test_cli.py::test_validation_targets_include_blocked_lists_do_not_execute_routes --no-cov
```

Manual CLI smoke:

```powershell
.\.venv\Scripts\ai-presenter validation-targets --package ringcentral-video --priority P0
.\.venv\Scripts\ai-presenter validation-targets --package ringcentral-video --target rcv-add-coworkers-modal
.\.venv\Scripts\ai-presenter validation-targets --package ringcentral-video --include-blocked
```

Static checks:

```powershell
.\.venv\Scripts\python -m ruff check src\ai_presenter\acceptance\validation_targets.py tests\unit\test_validation_targets.py tests\unit\test_cli.py
.\.venv\Scripts\python -m mypy src\ai_presenter\acceptance\validation_targets.py tests\unit\test_validation_targets.py tests\unit\test_cli.py
git diff --check
```

Full verification before closing an implementation cycle:

```powershell
.\.venv\Scripts\python -m pytest
.\.venv\Scripts\python -m mypy src tests
.\.venv\Scripts\python -m ruff check src tests
```

## Commands Run During This Scan

```powershell
Get-Content -Raw src\ai_presenter\acceptance\validation_targets.py
Get-Content -Raw tests\unit\test_validation_targets.py
Get-Content -Raw tests\unit\test_cli.py
Get-Content -Raw docs\knowledge\ringcentral-video\validation-checklist-index.md
rg -n "validation-targets|discover_validation_targets|render_validation_target_lines|_target_id|_parse_priority_checklist|Target ID|Priority Checklist|include-blocked" src tests docs\knowledge\ringcentral-video docs\agent-handoffs
Get-Content -Raw src\ai_presenter\cli.py
Get-Content -Raw docs\agent-handoffs\cycle-028-demand-analysis.md
Get-Content -Raw docs\agent-handoffs\cycle-028-technical-scan.md
.\.venv\Scripts\python -m pytest tests\unit\test_validation_targets.py tests\unit\test_cli.py::test_validation_targets_lists_ringcentral_targets tests\unit\test_cli.py::test_validation_targets_detail_outputs_draft_command tests\unit\test_cli.py::test_validation_targets_rejects_unknown_target_with_available_ids tests\unit\test_cli.py::test_validation_targets_include_blocked_lists_do_not_execute_routes --no-cov
.\.venv\Scripts\ai-presenter validation-targets --package ringcentral-video --priority P0
.\.venv\Scripts\ai-presenter validation-targets --package ringcentral-video --include-blocked
git status --short
```

Focused verification result during scan:

```text
13 passed in 4.10s
```

