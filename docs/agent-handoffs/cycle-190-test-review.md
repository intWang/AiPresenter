# Cycle 190 Test Review

Date: 2026-05-17

## RED Verification

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests\unit\test_cli.py::test_validation_targets_lists_ringcentral_targets
```

Result before implementation: failed because the P0 `validation-targets` output did not include
an evidence reminder.

## Focused Verification

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests\unit\test_validation_targets.py tests\unit\test_cli.py -k validation_targets tests\unit\test_material_packages.py::test_ringcentral_knowledge_docs_preserve_evidence_boundaries
```

Result: `35 passed, 76 deselected`.

```powershell
.\.venv\Scripts\ai-presenter.exe validation-targets --package ringcentral-video --target rcv-add-coworkers-modal
```

Result: output included the evidence reminder once, before the `draft:` command.

```powershell
.\.venv\Scripts\ai-presenter.exe validation-targets --package ringcentral-video --include-blocked --target rcv-recording
```

Result: output did not include the evidence reminder and did not include `draft:` or
`acceptance-draft`.

```powershell
.\.venv\Scripts\ai-presenter.exe validation-targets --package ringcentral-video --priority P1
.\.venv\Scripts\ai-presenter.exe validation-targets --package ringcentral-video --priority P2
```

Result: P1 output included the evidence reminder once. P2 output omitted the reminder.

## Independent Review

An independent review found no blocking findings.

- The reminder gate is limited to RingCentralVideo selected unblocked P0/P1 targets.
- Blocked targets still omit `draft:` commands.
- Reminder wording stays procedural and does not claim live acceptance or proof.
- Tests cover blocked-only suppression, P0/P1 inclusion, P2 suppression, non-RingCentral
  suppression, and CLI blocked no-draft output.

Additional reviewer verification:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_validation_targets.py tests\unit\test_cli.py tests\unit\test_material_packages.py
```

Result: `210 passed`.

Reviewer CLI spot checks: P0 reminder count `1`, P1 reminder count `1`, P2 reminder count `0`,
blocked-only reminder count `0`, blocked-only `acceptance-draft` count `0`.

## Required Before Commit

Run full repository verification and cached-diff checks:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m mypy src tests
git diff --cached --check
git diff --cached -- .coverage
git diff --cached --stat
git diff --cached --name-only
```
