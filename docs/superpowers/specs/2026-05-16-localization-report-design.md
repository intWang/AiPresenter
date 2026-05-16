# Localization Report Design

Date: 2026-05-16
Cycle: 026

## Goal

Add a read-only operator command that reports material-package localization coverage without requiring ad hoc scripts or YAML inspection.

## User Value

Recent cycles made RingCentral Chinese coverage complete across demo narration, Q&A, and adaptive invite behavior. Operators and maintainers now need a lightweight way to see that state before a demo or review. The report should show coverage counts, not dump localized text.

## Scope

In scope:

- Add a pure package helper for localization coverage.
- Add a CLI command:

```powershell
.\.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language zh
```

- Report demo narration coverage by flow.
- Report Q&A localized question/answer coverage.
- Report entrypoint alias presence and alias count.
- Add focused tests for helper and CLI behavior.
- Add a short README example.

Out of scope:

- Runtime/demo execution changes.
- `doctor` gating or nonzero exit for partial coverage.
- JSON/Markdown export.
- New languages or changes to voice language normalization.
- Package copy changes.
- Live RingCentralVideo acceptance.

## Output

The default output is stable plain text:

```text
Package: ringcentral-video
Package version: 1
Language: zh

Demo flows:
- vbg-blur-demo: 4/4 narration localized

Q&A:
- localized questions: 8/8
- localized answers: 8/8

Entrypoint aliases:
- questionAliases.zh present on 15/27 entrypoints (49 aliases)

Localization report: 51/51 demo steps, 8/8 Q&A questions, 8/8 Q&A answers localized for zh.
```

If coverage is partial, the command still exits 0 and prints missing IDs:

```text
- onboarding-demo: 2/3 narration localized
  missing: explain-share
```

Alias coverage is informational. Some entrypoints may not need aliases, so the report must not label 15/27 as failure.

## Architecture

Create `src/ai_presenter/packages/localization_status.py` with package-only dataclasses and rendering functions. It may import `MaterialPackage` from package models, but it must not import desktop automation, runtime factory, controller, speech providers, or diagnostics.

Expose the helper from `src/ai_presenter/cli.py` through a Typer command named `localization-report`. The command uses existing `resolve_material_package()` and `load_material_package()`.

## Acceptance Criteria

- `localization-report --package ringcentral-video` exits 0 and prints RingCentral counts.
- `--language zh` reports only `zh` coverage.
- Explicit unsupported-in-content languages such as `ja` exit 0 and report zero coverage.
- Helper tests cover full RingCentral counts and a synthetic partial package.
- CLI import still does not load desktop runtime modules.
- README includes a short command example near `flows` and `entrypoints`.
