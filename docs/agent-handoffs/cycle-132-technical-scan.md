# Cycle 132 Technical Scan: Spanish Entrypoint Copy Pilot And CLI Display

Date: 2026-05-16

## Scope

Investigated feasibility of three next slices after Cycle131:

- a tiny RingCentral package YAML pilot for Spanish `localizedTitles` and `localizedPurposes` on safe entrypoints;
- safety and Q&A precedence tests with localized copy present;
- CLI `entrypoints --language` display support.

This scan is documentation-only. No source, tests, packages, staging, or commits were changed by this agent.

## Current Baseline

Cycle131 already added optional `OperationEntrypoint.localizedTitles` and `localizedPurposes` maps in `src/ai_presenter/packages/models.py`, plus `title_for_language()` and `purpose_for_language()` helpers. Runtime entrypoint fallback answers use localized title/purpose for the active voice language when present, with the Cycle130 Spanish alias-label fallback preserved when no localized title exists.

Important boundaries already hold:

- `localizedTitles` and `localizedPurposes` are display-only.
- Entrypoint match candidates still use canonical English `id`, `title`, `area`, and `purpose`.
- Package-owned `questionAliases` remain the controlled localized matching surface.
- Q&A still runs before entrypoint fallback in `src/ai_presenter/runtime/questions.py`.
- Safety gating still uses canonical English `id/title/purpose` and `questionPolicy`, not localized copy.
- Localization reports include optional localized title/purpose counts, but `--require-complete` is still demo narration plus Q&A question/answer coverage.

The live RingCentral package currently has zero `localizedTitles.es` and zero `localizedPurposes.es`. Spanish package coverage is otherwise complete: `51/51` demo steps, `12/12` Q&A questions, `12/12` Q&A answers, and `questionAliases.es` on `26/27` entrypoints with `69` aliases. Spanish runtime remains OpenAI-backed only; local SAPI/Piper Spanish support and live acceptance remain outside this slice.

## Option 1: Tiny Package YAML Pilot For Safe Spanish Entrypoints

Recommendation: feasible and low risk if it is a tiny authored content pilot, not a broad translation pass.

Files likely touched by implementation:

- `packages/ringcentral-video.yaml`
- `tests/unit/test_material_packages.py`
- `tests/unit/test_questions.py`
- `tests/unit/test_cli.py` only if report count assertions are updated or paired with Option 3
- handoff docs for implementation

Suggested pilot entrypoints:

- Best first candidate: `ringcentral.video.toolbar.chat`.
  - It is a common user-facing surface.
  - It already has Spanish aliases.
  - It is operable, but opening the chat panel is already allowed and existing presenter notes warn against reading private chat text aloud.
  - Spanish localized purpose can preserve the privacy boundary, for example "Abre el panel de chat de la reunion sin leer mensajes privados."
- Good second candidate if the cycle wants one answer-only surface: `ringcentral.video.more.notes`.
  - It has `questionPolicy: answerOnly`, so no operation should be queued.
  - Purpose copy must preserve literal UI labels such as `Notes and Transcript`, `Start notes`, and recording consent boundaries.
  - Keep wording location/explanation-only. Do not imply reading transcripts or starting notes.
- Avoid in the first pilot: recording, leave, share, invite, mute/camera toggles, meeting information, and host/participant identity surfaces. They are valid future work, but they are safety-sensitive enough to deserve a separate content review.

Likely code shape:

- No runtime code required.
- Add only two new maps under one or two selected entrypoints:
  - `localizedTitles: { es: "..." }`
  - `localizedPurposes: { es: "..." }`
- Keep `title`, `purpose`, `questionAliases`, `questionPolicy`, `openSteps`, `presenterNotes`, and Q&A blocks unchanged.
- Do not add or reorder Spanish aliases as part of this slice.

Risks:

- Broad-translating all 27 entrypoints can accidentally alter safety-sensitive YAML around `questionPolicy`, `openSteps`, `presenterNotes`, or aliases.
- Spanish purpose text can make risky controls sound more actionable if it says "start", "send", "read", "record", "leave", or "share" where the English boundary is explanatory.
- Report expectations will move from `localizedTitles.es present on 0/27 entrypoints` and `localizedPurposes.es present on 0/27 entrypoints` to the pilot counts.
- YAML encoding must be handled deliberately. The current PowerShell view shows mojibake for non-ASCII package text, but tests load the file as UTF-8. Edit with UTF-8 and avoid unrelated rewrites.

Test strategy:

- Add a focused package assertion that the selected RingCentral entrypoint has the exact Spanish localized title and purpose.
- Assert `build_localization_status(package, language="es")` reports the expected pilot counts while keeping `required_localization_complete is True`.
- Add an answer rendering assertion for a Spanish alias prompt against the real package: localized title and purpose appear, and the old English `Title: Purpose` output does not.
- For `chat`, keep `can_operate is True` only because the existing safe open behavior already allows it.
- For `notes`, assert `can_operate is False` and no controller interrupt step is created.

Recommended verification commands:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_package_reports_complete_spanish_localization tests\unit\test_questions.py tests\unit\test_cli.py::test_localization_report_outputs_complete_spanish_package
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language es --require-complete
.\.venv\Scripts\ai-presenter.exe doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo --require-localization --localization-language es
git diff --check
```

## Option 2: Safety And Q&A Precedence Tests With Localized Copy

Recommendation: highly recommended before or alongside the YAML pilot. This is the strongest guard against localized display copy accidentally becoming routing input later.

Files likely touched by implementation:

- `tests/unit/test_questions.py`
- `tests/unit/test_controller.py` if interrupt behavior is asserted through `create_question_interrupt_step()` or controller submission
- possibly `tests/unit/test_material_packages.py` for match-candidate isolation

Likely code shape:

- Add tests against a small inline package where an entrypoint has Spanish localized title/purpose that overlaps an authored Spanish Q&A prompt.
- Add tests against the real RingCentral package after the pilot copy lands.
- Use `PresenterVoiceSettings(language="es")` for rendering tests and possibly `language="en"` for package-local Spanish prompt routing tests that intentionally avoid claiming runtime Spanish voice support.
- Continue monkeypatching `questions_module._ENTRYPOINT_ALIASES = {}` where the test is specifically proving package-owned alias/Q&A behavior without the legacy table.

Specific assertions to add:

- Q&A-first: a Spanish localized question with `localizedAnswers.es` returns the authored Q&A answer even when localized title/purpose copy contains similar words.
- No matching expansion: a Spanish phrase present only in `localizedTitles.es` or `localizedPurposes.es`, and absent from `questionAliases.es` and Q&A prompts, should still return no match.
- Safety answer-only: Spanish safety prompts for recording, notes/transcript, chat privacy, screen share, meeting information, reactions/raise hand, invite, leave, mute/camera state changes continue to return `can_operate is False` where they do today.
- Controller boundary: for any answer-only pilot such as Notes, `create_question_interrupt_step(package, response) is None`.
- Alias ordering unchanged: location prompts still route through `questionAliases.es`, not localized title/purpose tokens.

Risks:

- A test that uses `PresenterVoiceSettings(language="es")` can accidentally test runtime language support rather than package-local routing. Keep provider/profile checks separate.
- If the pilot chooses `chat`, `can_operate=True` is correct for location/open-panel prompts but unsafe for privacy prompts. Tests need both cases.
- Do not assert exact full localized answer text for tone variants unless the test owns tone rendering. Prefer high-signal substrings and `can_operate` boundaries for safety tests.

Recommended verification commands:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py::test_ringcentral_spanish_safety_questions_stay_qa_first_with_aliases tests\unit\test_questions.py::test_ringcentral_spanish_unaccented_safety_questions_stay_qa_first tests\unit\test_questions.py::test_localized_entrypoint_title_alone_does_not_create_a_match
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_controller.py::test_presenter_controller_starts_spanish_openai_question_demo_when_idle tests\unit\test_controller.py::test_controller_voice_readiness_rejects_incompatible_voice_before_asset_check
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_alias_overlap_ok_for_ringcentral_package tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_alias_substring_info_for_ringcentral_package
```

## Option 3: CLI `entrypoints --language` Display Support

Recommendation: feasible and small. It should be display-only and should not normalize against runtime presenter voice support.

Files likely touched by implementation:

- `src/ai_presenter/cli.py`
- `tests/unit/test_cli.py`
- possibly no package YAML unless paired with Option 1

Current state:

- `ai-presenter entrypoints --package ringcentral-video --area "Meeting toolbar"` prints only canonical English titles.
- The command has no `--language` option.
- `localization-report --language` already accepts package-local language strings without requiring presenter runtime support.

Likely code shape:

- Add an optional `language: str | None = typer.Option(None, "--language", help="Optional package-local language for localized entrypoint display.")` to `entrypoints()`.
- Default behavior remains exactly unchanged.
- If language is provided, display `entrypoint.title_for_language(language)` instead of `entrypoint.title`.
- Consider including localized purpose only if the command gains a verbose mode later. For this slice, title display is enough and keeps output stable.
- Do not call `resolve_voice_settings()` or `normalize_presenter_language()` for this CLI flag. The flag is package-local display, not runtime voice selection. This preserves the language lifecycle boundary for future package-only languages.

Risk:

- Calling runtime voice normalization would reject a package-only language even though entrypoint display is just package metadata.
- Changing default output would churn existing tests and operator workflows.
- Showing localized purpose by default could make the command noisy and create translation expectations beyond the tiny pilot.

Test strategy:

- Existing `test_entrypoints_lists_material_package_entrypoints_by_area` should keep default English output unchanged.
- Add an inline temp package CLI test with `localizedTitles.es` and `localizedPurposes.es` to prove `entrypoints --language es` displays the localized title.
- Include a package-only language such as `de` in that inline package to assert the command accepts package metadata without runtime language support.
- If paired with the RingCentral pilot, add a real-package assertion that the selected pilot entrypoint displays Spanish while unrelated entrypoints fall back to English.

Recommended verification commands:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_cli.py::test_entrypoints_lists_material_package_entrypoints_by_area tests\unit\test_cli.py::test_localization_report_outputs_complete_spanish_package
.\.venv\Scripts\ai-presenter.exe entrypoints --package ringcentral-video --area "Meeting toolbar"
.\.venv\Scripts\ai-presenter.exe entrypoints --package ringcentral-video --area "Meeting toolbar" --language es
```

## Recommended Slice Order

1. Add safety/Q&A precedence tests first, using inline data where needed.
2. Add the tiny YAML pilot for one safe Spanish entrypoint, preferably Chat.
3. Add `entrypoints --language` display support, or include it after the pilot if the team wants a visible manual check.

This order keeps the new authored Spanish copy behind tests before it lands in the package, then exposes it through a read-only CLI surface.

## No-Go Conditions

- Do not add localized title/purpose to entrypoint matching, alias indexes, diagnostics matching, controller routing, safety gating, or interrupt creation.
- Do not broad-translate all RingCentral entrypoints in this slice.
- Do not change `questionAliases.es` counts unless the cycle explicitly scopes alias work.
- Do not change `questionPolicy`, `openSteps`, `presenterNotes`, `relatedEntrypointIds`, or Q&A safety answers while adding localized display copy.
- Do not make localized title/purpose required for `--require-complete`.
- Do not claim Spanish local SAPI/Piper readiness, live RingCentral acceptance, or full Spanish localization from this content/display work.
- Do not stage `.coverage` or unrelated workspace changes.

## Final Recommendation

Proceed with a small, display-only Spanish pilot. The safest product value is: one or two curated entrypoint fallback answers become fully Spanish, Q&A safety still wins, the matcher stays untouched, and operators can inspect localized labels with `entrypoints --language es` without implying runtime voice or live-demo readiness.
