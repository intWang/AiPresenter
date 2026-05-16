# Cycle 144 Technical Scan

## Candidate

Add a narrow docs/test guard for RingCentral Video knowledge evidence language:
repo-tested, observed, checklist, acceptance-draft, and validation-target output
must stay distinct from dated live acceptance and runtime readiness. The current
docs mostly say this correctly; the gap is that only a few fragments are tested.

This scan is a handoff only. It does not implement the guard.

## Current State Observed

- `docs/knowledge/ringcentral-video/validation-checklist-index.md` already has
  the best compact contract:
  - line 7: checklist is procedure, not proof; dated proof belongs in
    `acceptance-runs.md`.
  - line 14: do not promote a route to `Accepted` from automated tests, dry
    runs, `doctor`, or read-only UIA observation alone.
  - lines 41-43: `Accepted`, `Observed`, and `Repo-tested` definitions separate
    dated live/manual evidence from UIA observation and local package/runtime
    tests.
- `docs/knowledge/ringcentral-video/evidence-index.md` defines the evidence
  levels at lines 26-28 and states at line 32 that no executable RingCentral
  Video route is fully `Accepted` for live operation yet.
- `docs/knowledge/ringcentral-video/evidence-index.md` also marks local records
  as non-live evidence:
  - line 38: repo baseline only; not live RingCentral evidence.
  - line 42: navigation evidence only; not live RingCentral evidence.
- `docs/knowledge/ringcentral-video/acceptance-runs.md` line 7 says checklist
  content is not acceptance evidence until a run is recorded there.
- `docs/knowledge/ringcentral-video/observation-log.md` lines 39-43 separate
  repository package shape from live app observation, and line 64 says a
  checklist is not a dated live pass record.
- `docs/knowledge/ringcentral-video/source-index.md` lines 9-11 separate
  official product scope, repository-local knowledge/tests, and live manual
  observation. Lines 33 and 40 say manual checklists/procedures are not proof
  until recorded in `acceptance-runs.md`.
- `docs/knowledge/ringcentral-video/runtime-safety-routing.md` line 7 says the
  guide does not replace dated acceptance evidence, and line 179 says to record
  a dated acceptance run before promoting live route evidence.
- `docs/runbooks/ringcentral-manual-acceptance.md` line 15 points operators to
  the validation checklist and repeats that runbook checkboxes are not
  acceptance evidence.
- `tests/unit/test_material_packages.py::test_ringcentral_validation_checklist_covers_package_routes`
  already checks route coverage, navigation references, blocked routes, and the
  phrase `runbook checkboxes are not acceptance evidence`, but it does not
  guard the `Accepted` / `Observed` / `Repo-tested` definitions or the
  current-no-live-accepted-route sentence.
- `tests/unit/test_material_packages.py::test_ringcentral_knowledge_docs_are_registered_in_navigation_indexes`
  already guards RingCentral knowledge-doc registration and dangling links.
- `tests/unit/test_validation_targets.py` parses real checklist/evidence docs
  and validates evidence levels, but it checks level names and integrity rather
  than level semantics.
- `src/ai_presenter/acceptance/validation_targets.py` already renders the CLI
  note `repo-derived planning list only; not live acceptance evidence.` No
  current CLI test asserts that note.
- `tests/unit/test_cli.py` has adjacent docs/output guards:
  - `test_entrypoints_language_marker_contract_is_documented` protects
    package-local display metadata from runtime/live-acceptance overclaims.
  - `test_validation_targets_lists_ringcentral_targets` verifies the validation
    target command finds the checklist.
  - `test_validation_targets_detail_outputs_draft_command` verifies draft
    command output, but does not assert the non-evidence note.
- Initial status for this scan had a pre-existing modified `.coverage`
  artifact. Do not stage, revert, or rely on it.

## Files To Touch In The Implementation Slice

### `tests/unit/test_material_packages.py`

Recommended narrow edit: extend
`test_ringcentral_validation_checklist_covers_package_routes` or add one
adjacent test named
`test_ringcentral_knowledge_docs_preserve_evidence_boundaries`.

Prefer the adjacent new test if the existing coverage test starts to feel like
a mixed-purpose bucket. Keep it as literal docs-contract assertions, not a new
parser.

Read these files in the test:

```python
knowledge_dir = Path("docs/knowledge/ringcentral-video")
checklist_text = (knowledge_dir / "validation-checklist-index.md").read_text(
    encoding="utf-8"
)
evidence_text = (knowledge_dir / "evidence-index.md").read_text(encoding="utf-8")
acceptance_text = (knowledge_dir / "acceptance-runs.md").read_text(encoding="utf-8")
source_text = (knowledge_dir / "source-index.md").read_text(encoding="utf-8")
runtime_text = (knowledge_dir / "runtime-safety-routing.md").read_text(
    encoding="utf-8"
)
```

Recommended positive assertions:

```python
assert (
    "Do not promote a route to `Accepted` from automated tests, dry runs, "
    "`doctor`, or read-only UIA observation alone."
) in checklist_text
assert "`Accepted` requires a dated manual/live record in `acceptance-runs.md`." in checklist_text
assert (
    "`Observed` can come from sanitized UIA/window metadata, but does not "
    "prove click or cleanup."
) in checklist_text
assert (
    "`Repo-tested` means package shape or runtime code was tested locally, "
    "not that RingCentral accepted the route live."
) in checklist_text

assert (
    "| `Accepted` | Automated tests plus dated live/manual acceptance for the "
    "current RingCentral build and route. |"
) in evidence_text
assert (
    "| `Observed` | Dated observation exists, but no click/cleanup acceptance "
    "exists for the route. |"
) in evidence_text
assert (
    "| `Repo-tested` | Package schema/tests cover the route; no current live "
    "acceptance exists. |"
) in evidence_text
assert (
    "no executable RingCentral Video route is fully `Accepted` for live "
    "operation yet"
) in evidence_text
assert "Repo baseline only; not live RingCentral evidence." in evidence_text
assert "Navigation evidence only; not live RingCentral evidence." in evidence_text

assert (
    "A checklist in a runbook is not acceptance evidence until a run is "
    "recorded here."
) in acceptance_text
assert (
    "Live manual observations are required before a locator or flow is treated "
    "as current-build evidence."
) in source_text
assert (
    "does not replace the package YAML, privacy matrix, locator matrix, or "
    "dated acceptance evidence."
) in runtime_text
assert "Before promoting any live route evidence, record a dated acceptance run first." in runtime_text
```

Recommended negative assertions:

```python
for doc_text in (checklist_text, evidence_text, source_text, runtime_text):
    normalized = " ".join(doc_text.split()).casefold()
    assert "repo-tested means accepted" not in normalized
    assert "observed means accepted" not in normalized
    assert "checklist is acceptance evidence" not in normalized
    assert "doctor proves live acceptance" not in normalized
    assert "dry run proves live acceptance" not in normalized
```

Keep the negative list small. The goal is to catch obvious regressions, not ban
every possible rephrasing.

### `tests/unit/test_cli.py`

Recommended narrow edit: add one assertion to
`test_validation_targets_lists_ringcentral_targets` and one to
`test_validation_targets_detail_outputs_draft_command`:

```python
assert "repo-derived planning list only; not live acceptance evidence" in result.stdout
```

This guards the CLI presentation boundary without touching
`src/ai_presenter/acceptance/validation_targets.py`.

### `tests/unit/test_acceptance_manual_record.py`

No required edit. It already guards the acceptance-draft boundary:

- `Draft only`
- `not acceptance evidence`
- `No live RingCentral action has been performed by this helper.`
- no `Accepted` string in the draft

Only touch this file if the implementation also changes draft wording, which
this candidate does not require.

### `tests/unit/test_validation_targets.py`

No required edit. It already validates evidence-level integrity, unknown
entrypoint rejection, duplicate target rejection, blocked target behavior, and
acceptance-draft command construction. Do not add semantic phrase assertions
here unless the parser/renderer behavior changes.

## Files Not To Touch

- `src/ai_presenter/**`
- `packages/ringcentral-video.yaml`
- `profiles/*.yaml`
- `README.md`
- `docs/knowledge/language-lifecycle.md`
- RingCentral runtime, package, voice, localization, or question-matching tests
- `.coverage`

If any source, package, or profile edit seems necessary, pause and rescope. This
candidate is a docs/test guard only.

## Verification Commands

Focused docs guard:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_validation_checklist_covers_package_routes tests\unit\test_material_packages.py::test_ringcentral_knowledge_docs_are_registered_in_navigation_indexes
```

If a new adjacent test is added, include it explicitly:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_knowledge_docs_preserve_evidence_boundaries
```

CLI validation-target boundary:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_cli.py::test_validation_targets_lists_ringcentral_targets tests\unit\test_cli.py::test_validation_targets_detail_outputs_draft_command tests\unit\test_validation_targets.py::test_discover_validation_targets_reads_priority_checklist_rows tests\unit\test_validation_targets.py::test_render_validation_target_lines_keeps_normal_draft_command
```

Acceptance-draft boundary sentinel:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_acceptance_manual_record.py::test_manual_acceptance_draft_prefills_entrypoint_context_without_claiming_acceptance tests\unit\test_cli.py::test_acceptance_draft_outputs_entrypoint_template
```

Manual CLI smoke, if the implementation touches CLI tests:

```powershell
.\.venv\Scripts\ai-presenter.exe validation-targets --package ringcentral-video --priority P0
.\.venv\Scripts\ai-presenter.exe validation-targets --package ringcentral-video --target rcv-add-coworkers-modal
```

Expected smoke traits:

- Output includes `Note: repo-derived planning list only; not live acceptance evidence.`
- P0 listing includes `rcv-add-coworkers-modal` and
  `rcv-controller-chat-question`.
- Target detail includes `ringcentral.video.main.add-coworkers`.
- Target detail includes an `acceptance-draft` command, but the note still says
  planning output is not live acceptance evidence.

Final hygiene:

```powershell
.\.venv\Scripts\ruff.exe check --no-cache tests\unit\test_material_packages.py tests\unit\test_cli.py
git diff --check -- tests\unit\test_material_packages.py tests\unit\test_cli.py docs\agent-handoffs\cycle-144-technical-scan.md
git status --short
```

## No-Go Claims

- Do not claim `Repo-tested` means live RingCentral acceptance.
- Do not claim `Observed` means click, cleanup, or runtime readiness.
- Do not claim a checklist, runbook checkbox, validation target, or
  acceptance-draft output is acceptance evidence.
- Do not claim automated tests, dry runs, `doctor`, or CLI inspection promote a
  route to `Accepted`.
- Do not claim any executable RingCentral Video route is ready for unattended
  live operation without a dated acceptance run.
- Do not broaden this slice into runtime behavior, package YAML, voice,
  localization, or question-routing changes.
