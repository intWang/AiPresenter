# Cycle 104 Technical Scan: Notes/Recording Japanese questionAliases

## Baseline

Read-only scan only. No YAML, runtime code, or tests were changed.

Current verified state after Cycle 103:

- `questionAliases.ja`: `11/27` entrypoints, `30` aliases.
- Total package-owned aliases: `83`.
- `ai-presenter localization-report --package ringcentral-video --language ja` reports `51/51` demo steps, `12/12` Q&A questions, `12/12` Q&A answers, and `questionAliases.ja present on 11/27 entrypoints (30 aliases)`.
- `ai-presenter doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo` reports `83 package-owned aliases have no cross-entrypoint duplicates`, `qa alias overlap` OK for `71` Q&A prompts, existing `qa alias substring risk` INFO at `11`, and `0 warnings, 0 failed`.

Candidate entrypoints in `packages/ringcentral-video.yaml`:

- `ringcentral.video.more.recording`
  - Title: `Start recording`
  - Purpose: `Start recording the meeting.`
  - Existing aliases: `questionAliases.zh` only.
  - `openSteps: []`.
  - Presenter notes explicitly say it is state-changing and should be explained without clicking unless the user explicitly asks to start recording.
- `ringcentral.video.more.notes`
  - Title: `Notes and transcript`
  - Purpose: `Open the Notes and Transcript side panel.`
  - Existing aliases: `questionAliases.zh` only.
  - Two `openSteps`: click `More` occurrence `3`, then click `onconf.controls.NOTES` with `alternateTargets: Notes`, `controlType: menuitem`, `cleanup: sidePanel`.
  - Presenter notes say the panel exposes `Start notes` and `Also record this meeting`, and that starting notes or recording changes meeting state.

Existing Q&A already covers both areas:

- `Where are notes and transcript controls?`
  - `localizedQuestions.ja`: `ノートと文字起こしはどこにありますか`
  - Related entrypoint: `ringcentral.video.more.notes`
- `How do I handle meeting recording safely?`
  - `localizedQuestions.ja`: `会議を録画するにはどうすればいいですか`
  - Related entrypoint: `ringcentral.video.more.recording`
- Adjacent safety Q&A also covers captions/live transcription/translation and post-meeting recordings/transcripts/summaries.

## Candidate Patch Shape

Recommended alias-only slice: add Japanese aliases to Recording only.

```yaml
- id: ringcentral.video.more.recording
  questionAliases:
    # existing zh block unchanged
    ja:
    - Start recording の場所
    - 録画の入口
  openSteps: []
```

The snippet above only shows the intended placement and new `ja` block. Do not change existing aliases, `openSteps`, presenter notes, Q&A, locators, demo actions, or runtime code.

Optional but not recommended as a low-risk alias-only slice: add Notes aliases only if the main session explicitly accepts that matching them is currently operable.

```yaml
- id: ringcentral.video.more.notes
  questionAliases:
    # existing zh block unchanged
    ja:
    - Notes and Transcript パネルの場所
    - 文字起こしパネルの場所
  openSteps:
  # unchanged
```

Avoid broad aliases such as `録画`, `ノート`, or `文字起こし` in this cycle. They are easier to ask naturally, but they are also likely to increase the doctor substring-risk surface against existing safety Q&A. The safer wording above is location/control-label oriented and kept the simulated doctor overlap counts stable.

## Runtime Behavior

Question routing order matters:

1. `_match_qa()` runs first, including exact localized Q&A prompts and Q&A fragment/token matching.
2. `_match_entrypoint_alias()` then checks package-owned `questionAliases` before the legacy hard-coded alias table.
3. The final `QuestionResponse.can_operate` is computed by `_can_operate()`.

Recording behavior:

- Adding the recommended Recording aliases routes `Start recording の場所を教えて` and `録画の入口はどこですか` to `ringcentral.video.more.recording`.
- `can_operate` stays `False` because `recording.openSteps` is empty.
- Even if future open steps were added, the id/title/purpose include risky words such as `start`, `record`, and `recording`; tests should still assert final `can_operate is False`.
- The exact Japanese safety Q&A `会議を録画するにはどうすればいいですか` continues to match Q&A first and returns the localized safety answer, not the generic entrypoint answer.

Notes behavior:

- Adding Notes aliases routes short Japanese location prompts to `ringcentral.video.more.notes`.
- `can_operate` is currently `True` for that entrypoint because it has executable `openSteps` and its id/title/purpose do not contain any `_RISKY_ENTRYPOINT_WORDS`.
- This is not a new behavior in general: existing English `Where are Notes and transcript` and existing Japanese Q&A for notes already resolve to the same entrypoint and can be operable.
- The difference is blast radius: package-owned `questionAliases.ja` would make more short Japanese phrases eligible to open the Notes and Transcript side panel.
- Because the panel can expose notes/transcript content plus `Start notes` and `Also record this meeting`, Notes should be deferred unless the implementation intentionally accepts `can_operate=True` or first changes runtime policy to make this entrypoint explain-only for questions.

## Test Plan

For the recommended Recording-only slice:

- Update `tests/unit/test_material_packages.py::test_ringcentral_package_owns_japanese_aliases_for_meeting_control_routes` with exact Recording alias expectations.
- Update `tests/unit/test_material_packages.py::test_meeting_control_map_has_japanese_recording_narration`: replace `assert "ja" not in recording_entrypoint.question_aliases` with the exact two-alias assertion; keep `open_steps == []` and presenter-note assertions.
- Update localization count assertions in material package and CLI tests from `11/27` and `30 aliases` to `12/27` and `32 aliases`.
- Update doctor/diagnostics alias-count assertions from `83 package-owned aliases` to `85 package-owned aliases`.
- Extend `tests/unit/test_questions.py::test_ringcentral_japanese_meeting_control_questions_match_package_aliases_without_legacy_table` or add a focused test proving `Start recording の場所` and `録画の入口` route through package-owned aliases with `_ENTRYPOINT_ALIASES` empty and return `can_operate is False`.
- Keep/extend a safety Q&A test proving `会議を録画するにはどうすればいいですか` remains Q&A-first, returns the Japanese safety answer, and does not return the generic `Start recording:` entrypoint answer.
- Re-run the focused set plus:
  - `.\.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language ja`
  - `.\.venv\Scripts\ai-presenter doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo`

If Notes is included despite the operability concern:

- Also update `test_meeting_control_map_has_japanese_notes_narration`: replace `assert "ja" not in notes_entrypoint.question_aliases` with exact alias assertions while preserving the current `More` occurrence `3`, `onconf.controls.NOTES`, `alternateTargets: Notes`, and `cleanup: sidePanel` assertions.
- Add Japanese package-owned alias route tests for `Notes and Transcript パネルの場所` and `文字起こしパネルの場所`.
- Make the expected behavior explicit in tests: either assert `can_operate is True` and document that this opens the panel, or add runtime gating first and assert `can_operate is False`.

## Expected Counts

Recommended Recording-only patch:

- `questionAliases.ja`: `11/27`, `30 aliases` -> `12/27`, `32 aliases`.
- Total package-owned aliases: `83` -> `85`.
- Doctor `question aliases`: `85 package-owned aliases have no cross-entrypoint duplicates`.
- Doctor `qa alias overlap`: remains OK for `71` Q&A prompts.
- Doctor `qa alias substring risk`: expected to remain INFO at `11` prompts with the conservative aliases above.

Notes-only simulation, not recommended as low-risk alias-only:

- `questionAliases.ja`: `12/27`, `32 aliases`.
- Total package-owned aliases: `85`.
- Diagnostics counts stayed clean in simulation, but Notes aliases route to an operable entrypoint.

Both Recording and Notes with two aliases each:

- `questionAliases.ja`: `13/27`, `34 aliases`.
- Total package-owned aliases: `87`.
- Doctor `question aliases`: `87 package-owned aliases have no cross-entrypoint duplicates`.
- Doctor `qa alias overlap`: remains OK for `71` Q&A prompts in simulation.
- Doctor `qa alias substring risk`: expected to remain INFO at `11` prompts with the conservative aliases above.

## Risks

- Notes is the main technical risk. Alias-only expansion would not change `_can_operate()`; it would make additional Japanese prompts operable and able to open the Notes and Transcript side panel.
- The Notes route itself still has locator uncertainty documented elsewhere: current YAML uses `More` occurrence `3` and `onconf.controls.NOTES`, while presenter notes mention older/direct Notes layouts.
- Recording is safer for alias-only because it has no `openSteps` and is also blocked by risky words, but the generic entrypoint answer is terse. The existing Japanese Q&A remains the better answer for "how do I record" questions.
- Broad aliases can affect doctor substring-risk counts. Keep aliases location/control-label specific and avoid exact or substring collisions with safety Q&A unless tests intentionally lock the new diagnostics count.
- Future copy edits to id/title/purpose could weaken the risky-word protection. Runtime tests should assert final `QuestionResponse.can_operate`, not only the current wording.
