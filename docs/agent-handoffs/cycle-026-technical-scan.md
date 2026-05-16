# Cycle 026 Technical Scan: Package Localization Status

Scope: review only for a small localization coverage reporting feature for material packages/RingCentral.

## Current State

- CLI patterns live in `src/ai_presenter/cli.py`. Package-only commands already exist: `flows`, `entrypoints`, `validation-targets`, and `acceptance-draft`.
- `validation-targets` and `acceptance-draft` are the closest patterns: CLI loads a material package, calls pure helper logic, catches `OSError`/`ValueError` as `typer.BadParameter`, and prints deterministic text with `typer.echo`.
- `src/ai_presenter/packages/models.py` already exposes the needed data:
  - `DemoStepNarration.localized_text`
  - `QuestionAnswer.localized_questions`
  - `QuestionAnswer.localized_answers`
  - `OperationEntrypoint.question_aliases`
  - read-only package indexes for entrypoints and flows
- Current `packages/ringcentral-video.yaml` coverage is complete for Chinese content:
  - Package: `ringcentral-video`, version 1
  - Entrypoints: 27
  - Demo flows: 4
  - Demo steps: 51
  - Q&A items: 8
  - Languages discovered from localized fields: `zh`
  - `zh` narration: 51/51 demo steps
  - `zh` Q&A questions: 8/8
  - `zh` Q&A answers: 8/8
  - `zh` entrypoint aliases: 15/27 entrypoints
- Tests already guard much of this in `tests/unit/test_material_packages.py`, especially `test_all_ringcentral_demo_flow_steps_have_chinese_localized_narration`.

## Recommended Small Implementation

Add a package-level reporting helper, then expose it through one CLI command.

Preferred new helper file:

- `src/ai_presenter/packages/localization_status.py`

Suggested API:

- `discover_localization_languages(package: MaterialPackage) -> tuple[str, ...]`
- `build_localization_status(package: MaterialPackage, languages: tuple[str, ...] | None = None) -> LocalizationStatusReport`
- `render_localization_status_lines(report: LocalizationStatusReport) -> list[str]`

Keep the dataclasses plain and package-only. Do not import controller, desktop automation, speech providers, diagnostics, or runtime factory code.

Preferred CLI command:

- `ai-presenter localization-status --package ringcentral-video`

Reason to prefer `localization-status` over `package-status`: the slice is narrow and avoids implying broader package health checks such as evidence, safety metadata, executable routes, or desktop acceptance.

Optional flags:

- `--language zh` to restrict to one language.
- `--include-complete` only if later detail output becomes noisy; for the first slice, always print summary lines.

## Suggested Output

Use stable plain text, similar to `validation-targets`:

```text
Package: ringcentral-video
Package version: 1
Languages: zh

Localization: zh
  demo narration: 51/51
  qa questions: 8/8
  qa answers: 8/8
  entrypoint aliases: 15/27
  flows:
    - vbg-blur-demo: 4/4
    - meeting-basics-demo: 3/3
    - meeting-controls-tour: 22/22
    - meeting-control-map-demo: 22/22
```

Exit code should be `0` for a report, even with partial coverage. This is a status command, not a policy gate. If a later CI gate is wanted, add a separate `--fail-under` or `--require-complete` option.

Avoid JSON in the first implementation unless a caller exists. If JSON is later needed, add `--format text|json` and test both. Keep the default human-readable.

## Exact Tests

Add pure helper tests in `tests/unit/test_material_packages.py`:

- RingCentral summary has `package_id == "ringcentral-video"`, `package_version == 1`, `languages == ("zh",)`.
- `zh` totals equal `51/51` demo narration, `8/8` Q&A questions, `8/8` Q&A answers, and `15/27` entrypoint aliases.
- Per-flow counts include `meeting-controls-tour: 22/22`.
- A small synthetic package with missing localized fields reports partial counts without raising.
- A language with no coverage can be requested explicitly and reports zeroes rather than disappearing.

Add CLI tests in `tests/unit/test_cli.py`:

- `CliRunner().invoke(app, ["localization-status", "--package", "ringcentral-video"])` exits `0`.
- Output contains `Package: ringcentral-video`, `Languages: zh`, `demo narration: 51/51`, and `meeting-controls-tour: 22/22`.
- Output does not contain `Loaded profile`.
- `--language zh` prints only the `zh` block.
- `--language ja` exits `0` and reports zero coverage, if explicit future-language reporting is supported.

Keep assertions substring-based. Do not assert the entire output blob; the existing CLI tests prefer stable key lines.

## README/Docs

Add one short README example near `flows`/`entrypoints` only after the command exists:

```powershell
.venv\Scripts\ai-presenter localization-status --package ringcentral-video
```

No runbook change is required for the first slice because this is package authoring/status, not manual acceptance evidence.

## Pitfalls

- Dirty workspace: many files are already modified or untracked, including `src/ai_presenter/cli.py`, `src/ai_presenter/packages/models.py`, `tests/unit/test_cli.py`, `tests/unit/test_material_packages.py`, `packages/ringcentral-video.yaml`, `README.md`, and `docs/agent-handoffs/`. Review by explicit paths and do not revert unrelated work.
- CLI import discipline: `tests/unit/test_cli.py::test_cli_import_does_not_load_desktop_runtime_modules` protects against importing `ai_presenter.desktop.windows`, `ai_presenter.runtime.factory`, and `ai_presenter.runtime.controller`. Keep the new helper under `ai_presenter.packages`.
- The current `cli.py` already imports some runtime modules for voice/diagnostics/controller labels. Do not add more runtime imports for this feature.
- Stable output: use counts and ids, not localized text content. Chinese strings can look like mojibake in some PowerShell output even when file content is valid UTF-8.
- Future languages: discover languages from all localized fields, but allow explicit `--language` values so a maintainer can see zero/partial coverage before content exists.
- Package ids: use `resolve_material_package()` and `load_material_package()` exactly like `flows` and `validation-targets`; print `package.app_id`, not the user input path.
- Do not make incomplete localization a validation error by default. Reporting and gating should remain separate.

## Smallest Path

Implement `src/ai_presenter/packages/localization_status.py`, add `localization-status` to `src/ai_presenter/cli.py`, then add focused tests in `tests/unit/test_material_packages.py` and `tests/unit/test_cli.py`. This avoids desktop/runtime imports, keeps behavior deterministic, and gives future package work an operator-visible coverage report without changing demo execution.
