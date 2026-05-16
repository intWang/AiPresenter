# Cycle 150 Demand Analysis: Validation Targets Evidence None Fallback

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`

## User Value

When `validation-targets` is rendered without usable evidence input, the output
must say `Evidence: none` and still show the non-evidence safety note:
`repo-derived planning list only; not live acceptance evidence.`

This protects the operator from a subtle false-confidence failure. A missing
evidence file, omitted `evidence_path`, or omitted/blank `evidence_text` should
read as missing traceability state, not as a loaded evidence index and not as
live RingCentral acceptance. The command can still be useful as a
repo-derived planning catalog, but it must be explicit that evidence is absent.

## Current Context

- Cycle 149 identified a follow-up around `validation-targets` behavior when no
  evidence file is available.
- `render_validation_target_lines(...)` already renders
  `Evidence: none` when `catalog.evidence_path` is `None`.
- `discover_validation_targets(...)` accepts `evidence_text: str | None` and
  `evidence_path: Path | None`. If `evidence_text` is missing or blank, it
  currently falls back to empty evidence maps while preserving the provided
  `evidence_path` in the returned catalog.
- The existing unit coverage proves the normal evidence-backed path renders the
  checklist path, evidence path, non-evidence note, and draft command.
- Existing real-catalog tests assert that real package evidence has no unknown
  evidence levels; keep those live evidence fixtures intact.

## Minimal Scope

Prefer a test-only cycle first. Strengthen
`tests/unit/test_validation_targets.py` around renderer/catalog fallback
behavior before changing production code.

Add focused coverage for these missing-evidence cases:

- `discover_validation_targets(...)` called with `evidence_text=None` and
  `evidence_path=None`;
- `discover_validation_targets(...)` called with blank `evidence_text` and
  `evidence_path=None`;
- `discover_validation_targets(...)` called with missing or blank
  `evidence_text` while an `evidence_path` is passed, if this is the path that
  can mislead the renderer.

The rendered output should include:

- `Evidence: none`;
- `Note: repo-derived planning list only; not live acceptance evidence.`;
- target blocks whose entrypoint evidence is `unknown`, not `Accepted`,
  `Observed`, or another loaded evidence level.

If the tests show current production behavior already satisfies a case, leave
that code untouched. If a missing or blank `evidence_text` with a provided
`evidence_path` still renders the path, make the smallest production change in
`src/ai_presenter/acceptance/validation_targets.py` so the catalog records
`evidence_path=None` when evidence text is absent.

## Out Of Scope

- Do not change live evidence files, especially
  `docs/knowledge/ringcentral-video/evidence-index.md`.
- Do not edit `acceptance-runs.md` or create any live RingCentral acceptance
  record.
- Do not change package YAML, package metadata, generated artifacts, or runtime
  behavior unrelated to validation-target evidence fallback.
- Do not alter allowed evidence levels or evidence index integrity rules for
  loaded evidence text.
- Do not broaden the renderer into claiming validation, acceptance, or pass/fail
  results.
- Do not touch `package`, dependency files, tests outside the focused unit area,
  or `.coverage`.
- Do not revert unrelated work from other agents.

## Acceptance Criteria

- Missing `evidence_path` renders the top-level line exactly as
  `Evidence: none`.
- Missing or blank `evidence_text` does not allow a stale or merely configured
  evidence path to render as if evidence was loaded.
- The non-evidence note remains present in every missing-evidence renderer
  output.
- Target evidence details fall back to `unknown` for entrypoints when evidence
  text is absent.
- Existing evidence-backed rendering still shows the real evidence path and
  real evidence levels.
- Existing evidence integrity tests still reject missing, unknown, duplicate,
  unbackticked, and invalid evidence rows when evidence text is provided.
- The implementation is test-only unless a focused failing test proves
  `validation_targets.py` must normalize absent evidence.
- `.coverage` remains untouched and unstaged.

Suggested verification for the implementation cycle:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_validation_targets.py
git diff --check -- tests\unit\test_validation_targets.py src\ai_presenter\acceptance\validation_targets.py
git status --short
```

This demand-analysis subtask only needs document hygiene:

```powershell
rg -n "[ \t]+$" docs\agent-handoffs\cycle-150-demand-analysis.md
git diff --check -- docs\agent-handoffs\cycle-150-demand-analysis.md
```

## Implementation Handoff Prompt

You are working in `C:\Users\rcadmin\Documents\Repos\AiPresenter` on Cycle 150:
`validation-targets` `Evidence: none` fallback.

User value: when renderer/catalog calls lack usable evidence input, the output
must explicitly show `Evidence: none`, keep the note
`repo-derived planning list only; not live acceptance evidence.`, and continue
to render planning targets without implying live RingCentral acceptance.

Read these files first:

- `docs/agent-handoffs/cycle-149-experience.md`
- `docs/agent-handoffs/cycle-150-demand-analysis.md`
- `tests/unit/test_validation_targets.py`
- `src/ai_presenter/acceptance/validation_targets.py`

Implement test-first. Start in `tests/unit/test_validation_targets.py` and add
focused renderer/catalog coverage for absent evidence. Use existing helpers such
as `discover_catalog(...)`, `priority_checklist_with_target_id_rows(...)`, and
`render_validation_target_lines(...)` where they keep the test small.

Cover at least one direct renderer output where the catalog has no evidence
path:

```python
catalog = discover_validation_targets(
    load_ringcentral_package(),
    checklist_text=load_checklist_text(),
    checklist_path=Path("docs/knowledge/ringcentral-video/validation-checklist-index.md"),
    evidence_text=None,
    evidence_path=None,
)
text = "\n".join(render_validation_target_lines(catalog, target_id="rcv-add-coworkers-modal"))

assert "Evidence: none" in text
assert "Note: repo-derived planning list only; not live acceptance evidence." in text
assert "ringcentral.video.main.add-coworkers=unknown" in text
```

Also cover the misleading-input case if current behavior exposes it:
`evidence_text=None` or blank while `evidence_path` is provided. The expected
rendered output is still `Evidence: none`, because no evidence text was loaded.

Run the focused test before implementation and confirm it fails for any real
behavior gap. If it fails only for the provided-path case, make the smallest
change in `discover_validation_targets(...)`: when `evidence_text` is missing
or blank, return a `ValidationTargetCatalog` whose `evidence_path` is `None`.
Do not weaken `validate_entrypoint_evidence_index(...)`; provided evidence text
must still be validated strictly.

Keep the existing evidence-backed test behavior:

- normal catalog rendering still includes
  `Evidence: docs/knowledge/ringcentral-video/evidence-index.md`;
- real evidence levels such as `Observed` still render when evidence text is
  actually loaded;
- integrity tests continue to reject malformed evidence input.

Do not edit live evidence files, `acceptance-runs.md`, package YAML, dependency
files, generated artifacts, or `.coverage`. Do not claim or simulate live
RingCentral acceptance. Do not revert unrelated work from other agents.

Suggested focused verification:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_validation_targets.py
git diff --check -- tests\unit\test_validation_targets.py src\ai_presenter\acceptance\validation_targets.py
git status --short
```
