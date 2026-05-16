# Cycle 113 Technical Scan: RingCentral Video New-Language Wedge

Date: 2026-05-16
Scope: technical scan only. This handoff recommends a minimal content/test slice and does not implement it.

## Goal

Add the smallest safe new-language wedge for the RingCentral Video material package without changing runtime language support, package schema, production code, profiles, docs indexes, or git history.

## Current State

The package localization model already supports arbitrary language keys in YAML:

| Surface | Model field | Current pattern |
| --- | --- | --- |
| Demo narration | `narration.localizedText.<language>` | `zh` and `ja` are counted by `build_localization_status()` and selected by `render_narration_text()` only when the runtime voice language can be selected. |
| Q&A prompts | `qa[].localizedQuestions.<language>` | `zh` and `ja` localized prompts are indexed as Q&A match candidates. |
| Q&A answers | `qa[].localizedAnswers.<language>` | `answer_question()` returns the localized answer only when `PresenterVoiceSettings.language` matches. |
| Entrypoint aliases | `operationEntrypoints[].questionAliases.<language>` | Aliases are package-owned, counted by the localization report, and participate in entrypoint matching. |

Important boundary: `src/ai_presenter/runtime/voice.py` currently supports only `en`, `zh`, and `ja` presenter voices. Do not add a new runtime voice language in this wedge. That would touch CLI voice choices, profile compatibility, provider validation, voice assets, labels, and likely more tests. The safe wedge is package/report readiness only.

Current localization counts:

```text
zh: 51/51 demo steps, 12/12 Q&A questions, 12/12 Q&A answers, 15/27 entrypoints with aliases, 49 aliases
ja: 51/51 demo steps, 12/12 Q&A questions, 12/12 Q&A answers, 13/27 entrypoints with aliases, 34 aliases
ko: 0/51 demo steps, 0/12 Q&A questions, 0/12 Q&A answers, 0/27 entrypoints with aliases, 0 aliases
```

`localization-report --language ko --require-complete` currently exits `1` and prints `Localization coverage incomplete for ko.`

## Recommendation

Use `ko` as the new language code.

Why `ko`:

- It is a normal BCP-47-style primary language subtag, like the existing `zh` and `ja` package keys.
- It exercises non-Latin content and new-language reporting without implying a regional variant.
- It should remain report-only until runtime voice support is explicitly designed.

Smallest safe implementation: add one Korean Q&A seed and one Korean alias seed around the existing background privacy Q&A. Do not add demo narration in the first slice.

Start with `packages/ringcentral-video.yaml` only:

1. Add `localizedQuestions.ko` and `localizedAnswers.ko` to Q&A item #1, `How do I protect my real background?`.
2. Add `questionAliases.ko` to `ringcentral.video.settings.background`.
3. Do not add `localizedText.ko` yet. If a second wedge is desired, localize all four `vbg-blur-demo` steps together so the report moves from `0/51` to `4/51` without creating a half-localized short flow.

Suggested Korean seed content:

```yaml
localizedQuestions:
  ko:
    - 실제 배경을 어떻게 보호하나요?
    - 회의에서 방 배경을 숨기려면 어떻게 하나요?
localizedAnswers:
  ko: Settings를 열고 Background를 선택한 다음 Blur 또는 가상 배경을 선택합니다. Blur는 방의 세부 정보를 가리면서 사람은 보이게 하므로 가장 안전한 기본 privacy 옵션입니다.
```

For `ringcentral.video.settings.background`:

```yaml
questionAliases:
  ko:
    - 배경 설정
    - 가상 배경
    - 배경 흐림
```

Keep the English product labels `Settings`, `Background`, and `Blur` in the Korean answer because existing `zh`/`ja` patterns preserve UI labels while localizing the guidance.

## Tests To Write Red First

Add these in `tests/unit/test_material_packages.py`, near the existing localization status tests and package-owned alias tests.

```python
def has_hangul(text: str) -> bool:
    return any("\uac00" <= character <= "\ud7af" for character in text)
```

If the file already has enough small text helpers, keep this local to the new tests instead.

First red test:

```python
def test_ringcentral_korean_seed_qa_and_aliases_are_present() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    item = next(qa for qa in package.qa if qa.question == "How do I protect my real background?")
    questions = item.localized_questions.get("ko", [])
    answer = item.localized_answers.get("ko", "")
    aliases = package.entrypoint_by_id(
        "ringcentral.video.settings.background"
    ).question_aliases.get("ko", [])

    assert len(questions) >= 2
    assert all(has_hangul(question) for question in questions)
    assert has_hangul(answer)
    assert "Settings" in answer
    assert "Background" in answer
    assert "Blur" in answer
    assert {"배경 설정", "가상 배경", "배경 흐림"} <= set(aliases)
```

Second red test:

```python
def test_ringcentral_localization_status_reports_korean_seed_coverage() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    report = build_localization_status(package, language="ko")

    assert report.package_id == "ringcentral-video"
    assert report.language == "ko"
    assert report.demo_localized_steps == 0
    assert report.demo_total_steps == 51
    assert report.qa_localized_questions == 1
    assert report.qa_localized_answers == 1
    assert report.qa_total == 12
    assert report.entrypoints_with_aliases == 1
    assert report.entrypoint_total == 27
    assert report.alias_total == 3
    assert report.required_localization_complete is False
```

Add one CLI assertion in `tests/unit/test_cli.py` near existing `localization-report` tests:

```python
def test_localization_report_outputs_korean_seed_coverage() -> None:
    result = CliRunner().invoke(
        app,
        ["localization-report", "--package", "ringcentral-video", "--language", "ko"],
    )

    assert result.exit_code == 0
    assert "Language: ko" in result.stdout
    assert "Localization report: 0/51 demo steps, 1/12 Q&A questions, 1/12 Q&A answers localized for ko." in result.stdout
    assert "questionAliases.ko present on 1/27 entrypoints (3 aliases)" in result.stdout
    assert "Localization coverage incomplete" not in result.stdout
```

Do not add `tests/unit/test_questions.py` coverage yet. `PresenterVoiceSettings(language="ko")` is unsupported by design, and forcing it into question-answer runtime tests would silently expand the scope into voice support.

## Expected Report Output

Before implementation, `.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ko` reports:

```text
Language: ko
- vbg-blur-demo: 0/4 narration localized
- meeting-basics-demo: 0/3 narration localized
- meeting-controls-tour: 0/22 narration localized
- meeting-control-map-demo: 0/22 narration localized
- localized questions: 0/12
- localized answers: 0/12
- questionAliases.ko present on 0/27 entrypoints (0 aliases)
Localization report: 0/51 demo steps, 0/12 Q&A questions, 0/12 Q&A answers localized for ko.
```

After the seed wedge, expected key lines:

```text
Language: ko
- vbg-blur-demo: 0/4 narration localized
- meeting-basics-demo: 0/3 narration localized
- meeting-controls-tour: 0/22 narration localized
- meeting-control-map-demo: 0/22 narration localized
- localized questions: 1/12
- localized answers: 1/12
- questionAliases.ko present on 1/27 entrypoints (3 aliases)
Localization report: 0/51 demo steps, 1/12 Q&A questions, 1/12 Q&A answers localized for ko.
```

`--require-complete` should still fail after this wedge:

```text
Localization coverage incomplete for ko.
```

That failure is correct because the wedge is intentionally partial.

## Red/Green Strategy

Red:

1. Add the three tests above without touching YAML.
2. Run the focused tests with coverage disabled.
3. Expected failures:
   - Korean Q&A questions missing.
   - Korean Q&A answer missing.
   - Korean aliases missing.
   - Korean status still reports `0/12`, `0/12`, and `0 aliases`.

Green:

1. Add only the Korean Q&A seed and aliases to `packages/ringcentral-video.yaml`.
2. Run the focused tests again.
3. Run the CLI report to confirm the same count deltas.
4. Leave `--require-complete` failing for `ko`.

Do not update package schema, runtime voice choices, provider validation, profile YAML, docs indexes, or production code.

## Risks

- Adding `ko` to runtime voice support is a much larger feature. It would require `PresenterLanguage`, labels, aliases, voice provider compatibility, CLI `voices`, profile validation, and probably provider asset checks.
- Adding one Korean `localizedQuestions` entry makes it a Q&A match candidate internally, but no public runtime voice can request a Korean localized answer yet. That is acceptable for a package/report wedge, but it is why this cycle should avoid runtime question tests.
- `questionAliases.ko` can participate in entrypoint matching if lower-level code is called with a Korean voice in the future. Keep aliases narrow and tied to the same related surface as the seeded Q&A.
- Do not add one-off `localizedText.ko` to a single demo step unless the report is meant to show a partially localized flow. If demo narration is included, localize the whole `vbg-blur-demo` flow.
- CJK output can render poorly in legacy PowerShell depending on encoding. Do not "fix" existing Chinese or Japanese strings while adding Korean.
- `.coverage` is already modified in the worktree. Keep coverage disabled for focused pytest commands and do not stage `.coverage`.

## Verification Commands

Focused red/green tests:

```powershell
.\.venv\Scripts\python.exe -m pytest `
  tests\unit\test_material_packages.py::test_ringcentral_korean_seed_qa_and_aliases_are_present `
  tests\unit\test_material_packages.py::test_ringcentral_localization_status_reports_korean_seed_coverage `
  tests\unit\test_cli.py::test_localization_report_outputs_korean_seed_coverage `
  -q -o addopts=""
```

CLI report check:

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ko
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ko --require-complete
```

Expected second command: exit `1` with `Localization coverage incomplete for ko.`

Existing localization guard cluster:

```powershell
.\.venv\Scripts\python.exe -m pytest `
  tests\unit\test_material_packages.py::test_ringcentral_localization_status_reports_chinese_coverage `
  tests\unit\test_material_packages.py::test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage `
  tests\unit\test_material_packages.py::test_localization_status_reports_zero_for_explicit_uncovered_language `
  tests\unit\test_cli.py::test_localization_report_outputs_ringcentral_chinese_coverage `
  tests\unit\test_cli.py::test_localization_report_outputs_japanese_demo_and_qa_coverage `
  -q -o addopts=""
```

Whitespace and scope checks:

```powershell
git diff --check -- packages\ringcentral-video.yaml tests\unit\test_material_packages.py tests\unit\test_cli.py docs\agent-handoffs\cycle-113-technical-scan.md
git status --short
```

Before staging, confirm `.coverage` remains unstaged.
