# Cycle 026 Demand Analysis: Localization Coverage Reporting

Date: 2026-05-16
Scope: Review only. No code changes recommended in this handoff.

## Recommendation

Use Cycle 026 for a small read-only CLI command that reports package localization coverage:

```powershell
.\.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language zh
```

Prefer a new command over extending `flows` or `doctor`. `flows` is currently a simple flow list,
while the requested operator view spans demo-flow narration, Q&A localized questions/answers, and
entrypoint question aliases. `doctor` is a pre-demo readiness check with pass/fail diagnostics, not
a package-maintainer coverage inventory.

## Evidence From Current Workspace

- The Typer CLI already has read-only package commands: `flows`, `entrypoints`,
  `validation-targets`, `acceptance-draft`, `voices`, and `doctor`.
- `src/ai_presenter/packages/models.py` exposes all data needed for a report:
  `DemoStep.narration.localized_text`, `QuestionAnswer.localized_questions`,
  `QuestionAnswer.localized_answers`, and `OperationEntrypoint.question_aliases`.
- Current RingCentral package state is complete for Chinese demo/Q&A coverage:
  - `vbg-blur-demo`: 4/4 steps have `localizedText.zh`.
  - `meeting-basics-demo`: 3/3 steps have `localizedText.zh`.
  - `meeting-controls-tour`: 22/22 steps have `localizedText.zh`.
  - `meeting-control-map-demo`: 22/22 steps have `localizedText.zh`.
  - Q&A: 8/8 have `localizedQuestions.zh` and `localizedAnswers.zh`.
  - Entrypoint aliases: 15/27 entrypoints have `questionAliases.zh`, with 49 Chinese alias records.
- `tests/unit/test_material_packages.py` now guards all RingCentral demo-flow Chinese narration and
  Q&A coverage, but those checks are developer-facing and do not give operators an easy CLI view.
- `README.md` already asks operators to run `flows`, `voices`, and `doctor` before demos, so adding
  one package inspection command fits the existing workflow.

## User And Operator Value

Maintainers can answer "is this package ready for Chinese operation?" without ad hoc scripts or
reading YAML. The command also gives a stable review artifact after future flow or Q&A edits, so a
new English-only demo step is visible before someone tries a Chinese run.

This should be a report, not a gate, in the first slice. Existing tests already enforce RingCentral
Chinese narration coverage; the operator need is visibility.

## Acceptance Criteria

- Add a read-only CLI command, recommended name `localization-report`.
- Required option: `--package`, using the existing package resolver.
- Optional option: `--language`, defaulting to `zh` for the current supported localization family.
- The command prints:
  - Package id and requested language.
  - Per-flow localized narration counts, with missing step ids when any are missing.
  - Q&A localized question and answer counts, with missing question text or indexes when any are
    missing.
  - Entrypoint alias counts, clearly labeled as "aliases present", not a required 100% coverage
    target.
  - A compact summary line.
- Exit code stays zero for partial coverage in this slice unless package loading itself fails.
- Add focused CLI tests with a temporary package that proves:
  - Complete coverage renders expected counts.
  - Missing localized narration lists the affected `flow:step`.
  - Missing Q&A question/answer localization is visible.
  - Alias coverage is reported without failing when some entrypoints have no aliases.
- Document the command briefly in `README.md`.

## Suggested Output Shape

```text
Package: ringcentral-video
Language: zh

Demo flows:
- vbg-blur-demo: 4/4 narration localized
- meeting-basics-demo: 3/3 narration localized
- meeting-controls-tour: 22/22 narration localized
- meeting-control-map-demo: 22/22 narration localized

Q&A:
- localized questions: 8/8
- localized answers: 8/8

Entrypoint aliases:
- questionAliases.zh present on 15/27 entrypoints (49 aliases)

Localization report: 51/51 demo steps, 8/8 Q&A questions, 8/8 Q&A answers localized for zh.
```

For partial coverage:

```text
- onboarding-demo: 2/3 narration localized
  missing: explain-share
Q&A:
- localized questions: 7/8
  missing questions: #4 Can the presenter read meeting messages or participant names?
```

## Risks

- Alias coverage is not the same as required localization coverage. Some entrypoints may not need
  aliases, so the report should avoid marking 15/27 as a failure.
- A hardcoded `zh` default is fine for Cycle 026, but future languages should use an explicit
  supported-language list when package policy expands.
- Console rendering of Chinese can still show mojibake in legacy PowerShell. The report can mostly
  avoid printing Chinese text; when it prints missing English source question text, it remains
  readable.
- Counting nonblank strings is not translation quality review. The report should be framed as
  coverage visibility, not proof that localized copy is correct.
- Putting the logic directly inside `cli.py` could bloat the CLI. A tiny helper module is reasonable
  if the implementation starts to exceed simple formatting.

## Out Of Scope

- Do not modify package localization copy.
- Do not add new languages or change `PresenterVoiceSettings` language normalization.
- Do not change runtime fallback behavior, provider routing, controller behavior, or demo execution.
- Do not make `doctor` fail on localization gaps in this slice.
- Do not add JSON/Markdown export, thresholds, or CI gating until maintainers ask for automation.
- Do not run live RingCentralVideo acceptance.

## Alternatives Considered

- **Extend `flows`:** Small, but it only naturally covers demo flows and would hide Q&A/alias status.
- **Extend `doctor`:** Useful later for strict pre-demo checks, but too pass/fail-oriented for an
  operator coverage inventory.
- **Docs-only report:** Lowest risk, but it goes stale as soon as package content changes.
- **Test helper only:** Good for developers, but Cycle 025 already added the important guard. Cycle
  026 should make the same information visible to operators.

## Suggested Verification

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_cli.py tests\unit\test_material_packages.py
```

If the implementation extracts a helper module, also run ruff and mypy on the touched files:

```powershell
.\.venv\Scripts\python -m ruff check --no-cache src\ai_presenter tests\unit\test_cli.py
.\.venv\Scripts\python -m mypy --no-incremental src tests
```
