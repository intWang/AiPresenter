# Cycle 104 Risk Scan: Japanese Notes/Transcript Or Recording Entry Discovery

## Risk Verdict

Partial proceed only: do not add Japanese `questionAliases.ja` for
`ringcentral.video.more.notes` in cycle 104. If this round must add an alias,
limit it to the smallest recording-only, location-only slice for
`ringcentral.video.more.recording`.

Why Notes/Transcript should wait:

- `ringcentral.video.more.notes` has executable `openSteps` that open More and
  the Notes side panel.
- The current question safety gate does not treat `notes`, `transcript`,
  `caption`, or Japanese equivalents as risky entrypoint terms.
- Current exact/fuzzy Notes questions can therefore return
  `entrypoint_id == "ringcentral.video.more.notes"` with `can_operate is True`.
  Adding Japanese aliases would make ordinary location questions capable of
  opening a panel that may contain Start notes, Also record this meeting, notes,
  transcript, or captions.
- That violates the required boundary for this candidate: do not start notes or
  transcript, do not read transcript/caption/notes content, and do not imply
  post-meeting artifacts exist.

Why a tiny Recording alias slice is acceptable:

- `ringcentral.video.more.recording` currently has `openSteps: []`.
- Its id/title/purpose include `recording` and `start`, so question routing stays
  `can_operate=False`.
- A read-only in-memory simulation of the recommended +2 aliases kept
  diagnostics stable: `questionAliases.ja` would move from `11/27` entrypoints
  and `30` aliases to `12/27` and `32`; package-owned aliases would move from
  `83` to `85`; `qa alias overlap` stayed OK for `71` Q&A prompts; `qa alias
  substring risk` stayed at the existing INFO-level `11` prompts.

If the implementation owner wants the safest optimization instead of aliases,
skip aliases entirely and harden Notes/Transcript question handling first:
make Notes/Transcript/caption/transcript questions answer-only, then add
Japanese Q&A location variants that explain where the surface is without
opening it.

## Safe Alias Candidates

Only these two aliases are recommended, and only for
`ringcentral.video.more.recording`:

- `Start recording の場所`
- `録画ボタンの場所`

Constraints for this slice:

- Do not add any Japanese aliases to `ringcentral.video.more.notes`.
- Do not add `openSteps`, locators, cleanup behavior, operation handlers, or
  route execution for Recording.
- Do not pair these aliases with wording that says AiPresenter starts, stops,
  pauses, opens, reads, downloads, or summarizes recordings.
- Keep existing recording safety Q&A ahead of aliases. Exact questions about
  how to record should continue to return the localized consent/permission
  safety answer, not a runnable entrypoint.

Deferred Notes/Transcript alias examples that look tempting but are not safe in
this cycle:

- `Notes and Transcript パネルの場所`
- `ノートと文字起こしパネルの場所`
- `ノートの場所`
- `文字起こしの場所`
- `字幕の場所`
- `トランスクリプトの場所`

These can be reconsidered only after `ringcentral.video.more.notes` is made
non-operable for questions, or after a dedicated answer-only Q&A path is added
and tested.

## Forbidden Alias Patterns

Do not add bare or action-like Recording aliases:

- `録画`
- `レコーディング`
- `記録`
- `録音`
- `録画開始`
- `録画の開始`
- `録画する`
- `録画して`
- `録画を開始して`
- `録画を止めて`
- `録画を停止して`
- `Start recording`
- `Start recording をクリック`
- `録画の仕方`
- `会議を録画するには`
- `今すぐ録画`

Do not add aliases that imply consent, role, policy, or status is known:

- `同意なしで録画`
- `参加者に知らせず録画`
- `ホストとして録画`
- `録画中ですか`
- `録画されていますか`
- `録画状態`
- `録画を確認`
- `録画を許可`

Do not add aliases that imply post-meeting artifacts exist or can be opened:

- `会議後の録画`
- `録画ファイル`
- `録画を見る`
- `録画を開く`
- `録画を再生`
- `録画をダウンロード`
- `録画の内容`
- `録画を要約`

Do not add Notes/Transcript/caption/content aliases in this cycle:

- `Notes`
- `Notes and Transcript`
- `ノート`
- `会議メモ`
- `メモ`
- `文字起こし`
- `トランスクリプト`
- `字幕`
- `キャプション`
- `ライブ文字起こし`
- `翻訳字幕`
- `Start notes`
- `Also record this meeting`
- `議事録`
- `要約`
- `インサイト`

Do not add aliases that ask AiPresenter to read, summarize, copy, save, edit, or
promise private content:

- `文字起こしを読んで`
- `字幕を読んで`
- `ノートを読んで`
- `メモを要約して`
- `議事録を作って`
- `会議後の要約`
- `内容をコピー`
- `内容を保存`
- `録画や文字起こしはありますか`

Avoid broad substrings such as `録画`, `文字起こし`, `字幕`, and `ノート`. They either
look executable, overlap privacy Q&A, or expand the doctor substring-risk
surface without adding a safe location-only benefit.

## Required Tests

If the implementation takes the recording-only alias slice, add or update these
positive assertions:

- `ringcentral.video.more.recording.question_aliases["ja"]` is exactly
  `["Start recording の場所", "録画ボタンの場所"]`.
- `ringcentral.video.more.notes` still has no Japanese `questionAliases.ja`.
- Japanese alias coverage moves exactly to `12/27` entrypoints and `32` aliases.
- Doctor question-alias count moves exactly to `85 package-owned aliases have no
  cross-entrypoint duplicates`.
- `qa alias overlap` remains OK for `71` Q&A question prompts.
- `qa alias substring risk` remains INFO with the existing `11` prompt summary.

Add route tests with the legacy `_ENTRYPOINT_ALIASES` monkeypatched to `{}`:

- `Start recording の場所はどこですか` routes to
  `ringcentral.video.more.recording` with `can_operate is False`.
- `録画ボタンの場所はどこですか` routes to
  `ringcentral.video.more.recording` with `can_operate is False`.
- Passing either response into `create_question_interrupt_step()` returns
  `None`, proving the location question cannot queue a recording action.

Required negative tests for Recording:

- `会議を録画するにはどうすればいいですか` keeps returning the Japanese safety answer
  with `can_operate is False` and consent/permission language.
- `録画して`, `録画を開始して`, `録画を止めて`, `録画を停止して`,
  `Start recording をクリックして`, and `今すぐ録画して` remain non-operable and
  do not queue a demo step.
- `参加者に知らせず録画して`, `同意なしで録画して`, and `ホストとして録画して`
  remain non-operable and do not imply role, permission, or participant consent.
- `録画中ですか`, `録画されていますか`, and `録画状態を確認して` do not claim live
  recording state without verified visible context.
- `会議後の録画や文字起こしはどこにありますか` remains answer-only with
  `entrypoint_id is None`, `can_operate is False`, and "may be available" /
  permission language.
- `録画を見る`, `録画を開いて`, `録画を再生して`, `録画をダウンロードして`, and
  `録画の内容を要約して` remain non-operable and do not open or summarize content.

Required negative tests for deferred Notes/Transcript:

- `ringcentral.video.more.notes` still has no Japanese `questionAliases.ja`.
- `Notes and Transcript パネルの場所`, `ノートと文字起こしパネルの場所`,
  `ノートの場所`, `文字起こしの場所`, `字幕の場所`, and `トランスクリプトの場所`
  must not be introduced as package-owned aliases in this cycle.
- Existing caption/transcription Q&A such as `字幕はどこにありますか` remains
  answer-only with `entrypoint_id is None` and `can_operate is False`.
- If a future implementation tries Notes/Transcript aliases, first add a
  failing-then-passing guard showing `ノートと文字起こしはどこにありますか` is
  non-operable. At the current baseline it is operable, so this is a hard
  precondition for any Notes alias slice.

## Verification Commands

Baseline commands used for this scan:

```powershell
.\.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language ja
.\.venv\Scripts\ai-presenter doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo
```

Focused verification after a recording-only alias implementation:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_meeting_control_map_has_japanese_recording_narration tests\unit\test_material_packages.py::test_meeting_control_map_has_japanese_notes_narration tests\unit\test_questions.py::test_ringcentral_japanese_privacy_sensitive_questions_match_localized_answers tests\unit\test_questions.py::test_ringcentral_post_meeting_artifact_questions_are_answer_only tests\unit\test_questions.py::test_ringcentral_localized_post_meeting_artifact_questions_are_answer_only tests\unit\test_questions.py::test_recording_answer_is_not_operable tests\unit\test_diagnostics.py::test_diagnostics_reports_question_aliases_ok_for_ringcentral_package tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_alias_overlap_ok_for_ringcentral_package tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_alias_substring_info_for_ringcentral_package tests\unit\test_cli.py::test_localization_report_outputs_japanese_demo_and_qa_coverage tests\unit\test_cli.py::test_doctor_loads_profile_package_and_flow
```

Add the new negative tests above to `tests\unit\test_questions.py` and include
their exact test ids in the focused command once named.

Post-implementation CLI checks:

```powershell
.\.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language ja
.\.venv\Scripts\ai-presenter doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo
```

Expected post-implementation strings for the recording-only +2 alias slice:

```text
questionAliases.ja present on 12/27 entrypoints (32 aliases)
[OK] question aliases: 85 package-owned aliases have no cross-entrypoint duplicates
[OK] qa alias overlap: 71 Q&A question prompts have no unsafe package-owned alias overlaps
[INFO] qa alias substring risk: 11 Q&A question prompts contain package-owned alias substrings outside related entrypoints
```

Stale-count and forbidden-surface search:

```powershell
rg -n "questionAliases\.ja present on 11/27|entrypoints_with_aliases == 11|alias_total == 30|83 package-owned aliases|ja\" not in recording_entrypoint.question_aliases" tests docs
rg -n "Notes and Transcript パネルの場所|ノートと文字起こしパネルの場所|文字起こしの場所|字幕の場所|トランスクリプトの場所|録画$|録画開始|録画して|録画を開始" packages tests docs
```

## Handoff Notes

This risk scan changed only this handoff document. It did not edit code, YAML,
or tests.

Read-only baseline observed during this scan:

- Japanese localization report: `51/51` demo steps, `12/12` Q&A questions,
  `12/12` Q&A answers, and `questionAliases.ja present on 11/27 entrypoints
  (30 aliases)`.
- Doctor: `11 ok, 1 info, 0 warnings, 0 failed`; `83 package-owned aliases have
  no cross-entrypoint duplicates`; `qa alias overlap` OK for `71` Q&A prompts;
  substring risk remains INFO at `11`.

In-memory simulations were run without writing YAML:

- Recording +2 aliases (`Start recording の場所`, `録画ボタンの場所`) kept
  `qa alias overlap` OK and substring risk unchanged at `11`.
- Notes +2 aliases kept diagnostics numerically clean, but route checks showed
  Notes location prompts can return `can_operate=True`. That is the blocker:
  doctor cleanliness alone is not enough for Notes/Transcript.

The best cycle-104 implementation choice is therefore either:

- add only the two Recording location aliases with strict negative tests; or
- defer aliases and harden Notes/Transcript question routing so location or Q&A
  prompts for notes, transcript, captions, and post-meeting artifacts are
  answer-only before any future alias expansion.
