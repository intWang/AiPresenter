# Cycle 118 Test Review: Spanish VBG Demo Narration Wedge

Date: 2026-05-16
Scope: review of the small Spanish `vbg-blur-demo` narration slice.

## Findings

No blocking issues found.

The implementation matches the selected Cycle 118 wedge:

- `packages/ringcentral-video.yaml` adds `localizedText.es` only to the four `vbg-blur-demo` narration steps.
- Spanish localization reporting moved to `vbg-blur-demo: 4/4` and total `4/51`.
- `meeting-basics-demo`, `meeting-controls-tour`, and `meeting-control-map-demo` remain at `0` Spanish localized narration steps.
- Spanish Q&A coverage remains `12/12` questions and `12/12` answers.
- Spanish aliases remain `1/27` entrypoints and `3` aliases.
- Spanish runtime support remains disabled: `voices` does not list Spanish, and Spanish dry-run demo rejects `es`.
- Diagnostics prompt/alias counts remain at `84` Q&A prompts and `90` package-owned aliases.
- No staged files were present when checked; `.coverage` remains modified but unstaged.

## Diff Review

Reviewed diffs for:

- `packages/ringcentral-video.yaml`
- `tests/unit/test_cli.py`
- `tests/unit/test_material_packages.py`

The package diff is limited to four Spanish narration strings under:

- `vbg-blur-demo:open-video-settings`
- `vbg-blur-demo:open-background-panel`
- `vbg-blur-demo:select-blur`
- `vbg-blur-demo:verify-meeting-video`

The tests assert the narrow contract rather than full Spanish support: Spanish report output is `4/51`, Spanish `--require-complete` still exits nonzero, and the other Spanish demo flows remain untranslated.

## Commands Run

```powershell
git status --short
git diff -- packages/ringcentral-video.yaml
git diff -- tests/unit/test_cli.py
git diff -- tests/unit/test_material_packages.py
rg -n "84|90 package-owned|qa prompts|Q&A prompts|question aliases|package-owned aliases" tests/unit/test_diagnostics.py tests/unit/test_cli.py src/ai_presenter/runtime/diagnostics.py
```

Summary: working tree had existing unstaged changes in `.coverage`, package YAML, and two test files, plus untracked handoff files. No staged files were present in the later cached diff check.

```powershell
.\.venv\Scripts\python.exe -m pytest -q -o addopts="" -p no:cacheprovider tests\unit\test_material_packages.py::test_ringcentral_localization_status_reports_spanish_vbg_demo_wedge tests\unit\test_material_packages.py::test_ringcentral_spanish_qas_and_vbg_demo_are_localized tests\unit\test_cli.py::test_localization_report_outputs_spanish_vbg_demo_wedge tests\unit\test_cli.py::test_localization_report_require_complete_fails_for_spanish_vbg_demo_wedge tests\unit\test_cli.py::test_demo_rejects_unknown_language_before_runtime tests\unit\test_cli.py::test_voices_lists_language_tone_choices tests\unit\test_cli.py::test_doctor_loads_profile_package_and_flow tests\unit\test_diagnostics.py::test_diagnostics_reports_question_aliases_ok_for_ringcentral_package tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_questions_ok_for_ringcentral_package tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_alias_overlap_ok_for_ringcentral_package
```

Output summary: `10 passed in 2.74s`.

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language es
```

Output summary: exit `0`; `vbg-blur-demo: 4/4`, other Spanish demo flows `0/3`, `0/22`, `0/22`; total `4/51`; Q&A `12/12`; aliases `1/27` with `3 aliases`.

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language es --require-complete
```

Output summary: exit `1`; same Spanish counts as above, ending with `Localization coverage incomplete for es.`

```powershell
.\.venv\Scripts\ai-presenter.exe voices
```

Output summary: exit `0`; language list includes English, Chinese, and Japanese only. Spanish is not listed.

```powershell
.\.venv\Scripts\ai-presenter.exe demo --profile ringcentral-video --package ringcentral-video --flow vbg-blur-demo --language es --dry-run
```

Output summary: exit `1`; rejected with `Unsupported presenter language: es`.

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language zh --require-complete
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ja --require-complete
```

Output summary: both exit `0`; Chinese and Japanese remain `51/51` demo steps, `12/12` Q&A questions, and `12/12` Q&A answers.

```powershell
@'
from pathlib import Path
import yaml
pkg = yaml.safe_load(Path('packages/ringcentral-video.yaml').read_text(encoding='utf-8'))
rows = []
for flow in pkg['demoFlows']:
    ids = [step['id'] for step in flow['steps'] if 'es' in step.get('narration', {}).get('localizedText', {})]
    rows.append((flow['id'], len(ids), ids))
for row in rows:
    print(row)
print('total', sum(count for _, count, _ in rows))
'@ | .\.venv\Scripts\python.exe -
```

Output summary: Spanish demo narration appears only on `vbg-blur-demo`, with four step IDs: `open-video-settings`, `open-background-panel`, `select-blur`, and `verify-meeting-video`; total `4`.

```powershell
git diff --name-only --cached
git status --short
```

Output summary: no staged files; `.coverage` is modified but unstaged.

## Residual Risks

- This review verifies package data, CLI reports, and focused unit coverage only. It does not claim live RingCentral Video acceptance.
- Spanish remains a report/demo-narration wedge, not a supported presenter runtime language.
- The existing `.coverage` modification was present in the working tree and remains out of scope for this review.
