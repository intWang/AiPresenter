# Cycle 061 Risk Scan: `explain-report-issue` JA Narration

Date: 2026-05-16

## Scope

Review the risk of adding Japanese `localizedText.ja` narration to the `meeting-controls-tour` step `explain-report-issue` in `packages/ringcentral-video.yaml`.

Only this handoff document was edited. The scan read the minimum relevant context:

- `packages/ringcentral-video.yaml`
- `tests/unit/test_material_packages.py`
- `docs/agent-handoffs/cycle-060-technical-scan.md`
- targeted RingCentral safety/knowledge references found by search

## Risk List

1. **Diagnosis overclaim risk**
   - The Report issue dialog is an escalation/support surface, not proof of a root cause.
   - A Japanese script that says or implies the presenter can identify the cause from this dialog would conflict with existing Network quality guidance and Q&A safety language.

2. **Accidental issue submission risk**
   - The dialog covers Audio, Video, Screen sharing, Meeting join, Notes and transcript, and Other.
   - Picking a category, filling fields, or using wording that sounds like "I will send/submit this" could change the workflow from a safe tour into filing a report.

3. **Private notes/transcript content risk**
   - The dialog includes Notes and transcript as a problem category.
   - The narration must mention the category only as a label and must not imply reading notes, transcript text, summaries, recordings, or report contents.

4. **Blocking dialog cleanup risk**
   - The entrypoint presenter notes say this foreground dialog blocks every other meeting control until closed.
   - Escape was previously unreliable for this dialog; cleanup needs the dialog X/modal close path.
   - If the Japanese narration is too long or vague, the runner may keep the blocking dialog visible longer than necessary and make the next step fail.

5. **Top-bar coordinate drift risk**
   - `ringcentral.video.top.report-issue` is a coordinate route (`xFromRight=168`, `y=21`) with low live-confidence evidence in the knowledge files.
   - Adding localized narration does not change the action, but any validation that exercises the step can still fail because of window size, DPI, layout, or locale differences.

6. **Localization wording regression risk**
   - Existing tests already expect Japanese text for this step to include `Report`, a "do not decide/assume the cause" concept, and a close action, while excluding a send/submit term.
   - A literal translation that omits those safety ideas may pass basic CJK coverage but fail the behavioral intent.

## Mitigations

- Keep the change narration-only: add only `narration.localizedText.ja` under `explain-report-issue`; do not change ids, action, placement, `actionOffsetMs`, cleanup, entrypoints, aliases, tests, or YAML structure unless the implementation task explicitly asks.
- Preserve the product label `Report` so the spoken Japanese matches the visible UI and current test intent.
- Phrase the Japanese narration as capability/location guidance, not diagnosis. Include the idea that the presenter will not decide the cause without observed values.
- State that the dialog is closed before continuing. Prefer wording equivalent to "I close it before moving on" rather than "Escape" because the entrypoint notes say Escape was unreliable.
- Avoid Japanese words equivalent to "submit/send/file now" unless explicitly negated and covered by tests; safest is to avoid them entirely.
- Mention `notes` and `transcript` only as issue categories. Do not mention reading, summarizing, inspecting, or using their content.
- Keep the narration compact enough for `placement: during` and `actionOffsetMs: 450`; the dialog should be visible while named and then cleaned up promptly.

## Must Verify

- YAML shape:
  - `localizedText.ja` is added under `packages/ringcentral-video.yaml` -> `meeting-controls-tour` -> `explain-report-issue` -> `narration`.
  - Existing Chinese `localizedText.zh`, `placement: during`, and `actionOffsetMs: 450` remain unchanged.

- Text safety:
  - Includes `Report`.
  - Mentions audio/video/screen sharing/joining/notes/transcript/other issues as categories or equivalent.
  - Explicitly avoids deciding/assuming the cause without observed values.
  - Explicitly says the blocking dialog is closed before continuing.
  - Does not say the presenter submits, sends, files, diagnoses, reads notes, reads transcript, or inspects private report contents.

- Focused tests after implementation:

```powershell
pytest tests/unit/test_material_packages.py::test_meeting_controls_tour_has_japanese_report_issue_narration -q
pytest tests/unit/test_material_packages.py::test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage -q
pytest tests/unit/test_cli.py::test_localization_report_outputs_japanese_demo_and_qa_coverage tests/unit/test_cli.py::test_localization_report_require_complete_fails_for_japanese_demo_gap -q
pytest tests/unit/test_diagnostics.py::test_diagnostics_require_localization_reports_japanese_qa_complete_but_demo_missing -q
```

- Report smoke checks after implementation:

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ja
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ja --require-complete
```

- If a live/manual demo is run, use a disposable meeting and verify:
  - Report issue opens the expected foreground troubleshooting dialog.
  - No issue category is selected.
  - No notes/transcript/report contents are read or captured.
  - The dialog closes via X/modal cleanup.
  - Meeting controls are usable afterward.

## Recommendation

Proceed, but keep it as a narrow narration-only slice. The step is higher risk than the first four top-bar narration strings because it opens a blocking support dialog, but the risk is manageable if the Japanese text preserves the existing English safety posture: identify the Report surface, avoid root-cause claims, avoid submission, avoid private notes/transcript content, and close the dialog before continuing.
