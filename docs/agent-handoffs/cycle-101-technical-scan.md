# Cycle 101 Technical Scan: Japanese questionAliases expansion

Scope for the next implementation slice: add a small, low-risk set of Japanese `questionAliases.ja` entries to mature RingCentral Video controls in `packages/ringcentral-video.yaml`.

This scan intentionally writes only this handoff file. Do not modify YAML, code, tests, source-index docs, profiles, fixtures, coverage files, or git history during this scan. Other agents may be working in parallel; preserve unrelated local edits and do not revert their files. `.coverage` was already dirty during this scan and should be ignored.

## Baseline confirmed

Structured loader readout on 2026-05-16:

- `operationEntrypoints`: `27`
- `questionAliases.ja`: `3/27` entrypoints, `9` aliases
- Japanese demo and Q&A localization are already complete: `51/51` demo steps, `12/12` localized Q&A questions, `12/12` localized Q&A answers.

Current Japanese aliases:

| Entrypoint | Current aliases |
| --- | --- |
| `ringcentral.video.toolbar.audio` | `マイク`, `ミュート`, `音声` |
| `ringcentral.video.toolbar.participants` | `参加者`, `参加者一覧`, `参加者パネル` |
| `ringcentral.video.toolbar.chat` | `チャット`, `チャットパネル`, `メッセージ` |

## Recommended narrow implementation

Add `questionAliases.ja` to exactly these four entrypoints. All four are mature, already covered by demo/control-map narration, and open only a diagnostic popover or menu with an Escape cleanup path. They do not confirm a destructive action, send a meeting-visible signal, start sharing, start recording, leave the meeting, or change persistent settings.

| Entrypoint | Why this is low risk | Add these `ja` aliases |
| --- | --- | --- |
| `ringcentral.video.top.network-quality` | Observed top-bar diagnostic popover, `clickWindowRelative`, `cleanup: escape`; explains call health without changing meeting state. | `ネットワーク品質`, `接続品質`, `通話が不安定` |
| `ringcentral.video.top.views` | Observed top-bar layout menu, `clickWindowRelative`, `cleanup: escape`; opening the menu is display-only and does not change audio/video/share/member state. | `表示レイアウト`, `表示切り替え`, `ギャラリービュー` |
| `ringcentral.video.toolbar.audio-menu` | Existing toolbar caret route, `clickWindowControl` on first `More`, `cleanup: escape`; opens device options but does not select a device. | `音声メニュー`, `マイクメニュー`, `スピーカーメニュー` |
| `ringcentral.video.toolbar.video-menu` | Existing toolbar caret route, `clickWindowControl` on second `More`, `cleanup: escape`; opens camera options but does not switch camera or open settings by itself. | `カメラメニュー`, `ビデオメニュー`, `カメラ選択` |

Expected count changes after implementation:

- `questionAliases.ja`: `3/27` entrypoints, `9` aliases -> `7/27` entrypoints, `21` aliases
- Package-owned aliases across all languages: `62` -> `74`
- `operationEntrypoints` total remains `27`
- Q&A counts remain unchanged: `71` normalized prompts in diagnostics, `12/12` Japanese localized questions and answers.

I validated this proposed alias set in memory without writing the YAML. Expected diagnostics with these exact aliases:

- `[OK] question aliases: 74 package-owned aliases have no cross-entrypoint duplicates`
- `[OK] qa alias overlap: 71 Q&A question prompts have no unsafe package-owned alias overlaps`
- `[INFO] qa alias substring risk` remains at `11` prompts; no new substring-risk count was introduced by this candidate set.

## Explicit deferrals

Do not include these in the Cycle 101 implementation slice:

- `ringcentral.video.toolbar.leave`: destructive meeting exit boundary.
- `ringcentral.video.more.recording`: meeting-wide recording state and consent/policy boundary.
- `ringcentral.video.toolbar.share`: exposes local screen/window choices and can lead to share start.
- `ringcentral.video.more.settings`, `ringcentral.video.settings.video`, `ringcentral.video.settings.background`, `ringcentral.video.settings.background.blur`, `ringcentral.video.more.background`: settings/background changes are broader than this alias-only slice.
- `ringcentral.video.more.notes`: notes/transcript panel includes `Start notes` and recording-adjacent controls.
- `ringcentral.video.toolbar.video` and extra aliases for `ringcentral.video.toolbar.audio`: the button routes can toggle local camera/mic state. Keep this cycle focused on menus, not state changes.
- `ringcentral.video.toolbar.react` and `ringcentral.video.toolbar.raise-hand`: both are meeting-visible signals; leave to a separate safety pass.
- `ringcentral.video.top.meeting-info`, `ringcentral.video.toolbar.invite`, `ringcentral.video.main.add-coworkers`: useful future aliases, but they expose private meeting identifiers, invite links, names, emails, or suggestions.

## Test updates needed

`tests/unit/test_material_packages.py`:

- Update `test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage`:
  - `report.entrypoints_with_aliases`: `3` -> `7`
  - `report.alias_total`: `9` -> `21`
  - keep `entrypoint_total == 27`, demo counts, Q&A counts, and `required_localization_complete is True`.
- Update/rename `test_ringcentral_package_owns_japanese_aliases_for_meeting_basics_routes` so it covers all seven Japanese alias-owning routes. Add exact expected sets for:
  - `ringcentral.video.top.network-quality`: `ネットワーク品質`, `接続品質`, `通話が不安定`
  - `ringcentral.video.top.views`: `表示レイアウト`, `表示切り替え`, `ギャラリービュー`
  - `ringcentral.video.toolbar.audio-menu`: `音声メニュー`, `マイクメニュー`, `スピーカーメニュー`
  - `ringcentral.video.toolbar.video-menu`: `カメラメニュー`, `ビデオメニュー`, `カメラ選択`
  - Preserve the existing exact sets for audio, Participants, and Chat.
- Update focused control-map tests that currently assert alias absence or old counts:
  - `test_meeting_control_map_has_japanese_audio_menu_narration`: replace `assert "ja" not in audio_menu_entrypoint.question_aliases` with an exact alias-list assertion; update report count assertions to `7` and `21`.
  - `test_meeting_control_map_has_japanese_camera_menu_narration`: same replacement and count updates.
  - `test_meeting_control_map_has_japanese_network_narration` and `test_meeting_control_map_has_japanese_views_narration`: add exact alias-list assertions for the new aliases.
  - Every remaining `report.entrypoints_with_aliases == 3` / `report.alias_total == 9` assertion in this file should move to `7` / `21`. Use `rg -n "entrypoints_with_aliases == 3|alias_total == 9" tests/unit/test_material_packages.py` to catch all stale assertions.
- Keep `assert "ja" not in ...question_aliases` for deferred high-risk or out-of-scope entrypoints such as camera toggle, share, reactions, raise hand, More, recording, notes, background, settings, leave, and overview.

`tests/unit/test_cli.py`:

- Update `test_localization_report_outputs_japanese_demo_and_qa_coverage`:
  - `questionAliases.ja present on 3/27 entrypoints (9 aliases)` -> `questionAliases.ja present on 7/27 entrypoints (21 aliases)`.
- Update `test_doctor_loads_profile_package_and_flow`:
  - `62 package-owned aliases have no cross-entrypoint duplicates` -> `74 package-owned aliases have no cross-entrypoint duplicates`.
  - Keep `71 Q&A question prompts have no unsafe package-owned alias overlaps`.
  - Keep substring-risk detail at `11 Q&A question prompts...` unless implementation uses different alias text and diagnostics prove a different count.

`tests/unit/test_diagnostics.py`:

- Update `test_diagnostics_reports_question_aliases_ok_for_ringcentral_package`:
  - `62 package-owned aliases...` -> `74 package-owned aliases...`.
- Keep `test_diagnostics_reports_qa_alias_overlap_ok_for_ringcentral_package` detail at `71 Q&A question prompts have no unsafe package-owned alias overlaps` for the recommended aliases.
- Existing duplicate/overlap coverage already exists:
  - Duplicate aliases: `test_diagnostics_warns_for_duplicate_question_aliases`, `test_diagnostics_warns_for_cross_language_question_alias_duplicates`, `test_diagnostics_ignores_same_entrypoint_question_alias_duplicates`, plus CLI `test_doctor_warns_for_duplicate_question_aliases`.
  - Q&A exact overlap: `test_diagnostics_reports_qa_alias_overlap_ok_for_ringcentral_package`, `test_doctor_warns_when_qa_question_shadows_entrypoint_alias`.
  - Q&A substring risk: `test_diagnostics_reports_qa_alias_substring_info_for_ringcentral_package`, `test_doctor_reports_qa_alias_substring_risk_as_info`.

## Source-index update

Yes, the implementation slice should update `docs/knowledge/ringcentral-video/source-index.md`.

Update only the localization bullet so it no longer says `questionAliases.ja` covers only microphone, Participants, and Chat basics. Suggested wording:

```markdown
- Localization: Japanese coverage is complete for the existing Q&A safety set, the four-step virtual background blur demo, the three-step meeting basics demo, all twenty-two steps of `meeting-controls-tour`, and all twenty-two steps of `meeting-control-map-demo`; `questionAliases.ja` now covers microphone, Participants, Chat, Network quality, View layout, audio menu, and camera menu basics, while higher-risk or privacy-sensitive entrypoint aliases remain future work.
```

No source-index table row count or official-source entry needs to change.

## Focused verification

Run these after the YAML/test/source-index implementation:

```powershell
.\.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language ja
.\.venv\Scripts\ai-presenter doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo
```

Expected report lines:

```text
Localization report: 51/51 demo steps
- localized questions: 12/12
- localized answers: 12/12
questionAliases.ja present on 7/27 entrypoints (21 aliases)
```

Focused pytest slice:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage tests\unit\test_material_packages.py::test_ringcentral_package_owns_japanese_aliases_for_meeting_basics_routes tests\unit\test_material_packages.py::test_meeting_control_map_has_japanese_network_narration tests\unit\test_material_packages.py::test_meeting_control_map_has_japanese_views_narration tests\unit\test_material_packages.py::test_meeting_control_map_has_japanese_audio_menu_narration tests\unit\test_material_packages.py::test_meeting_control_map_has_japanese_camera_menu_narration tests\unit\test_cli.py::test_localization_report_outputs_japanese_demo_and_qa_coverage tests\unit\test_cli.py::test_doctor_loads_profile_package_and_flow tests\unit\test_diagnostics.py::test_diagnostics_reports_question_aliases_ok_for_ringcentral_package tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_alias_overlap_ok_for_ringcentral_package
```

Stale-expectation check:

```powershell
rg -n "questionAliases\.ja present on 3/27|entrypoints_with_aliases == 3|alias_total == 9|62 package-owned aliases" tests docs
```

After implementation, remaining `3/27`, `9`, or `62` references should only appear in older handoff/history docs, not active tests or current source-index wording.

## Complete verification

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q
.\.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language ja --require-complete
.\.venv\Scripts\ai-presenter doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo
git diff --check -- packages/ringcentral-video.yaml tests/unit/test_material_packages.py tests/unit/test_cli.py tests/unit/test_diagnostics.py docs/knowledge/ringcentral-video/source-index.md docs/agent-handoffs/cycle-101-technical-scan.md
```

Implementation diff should be limited to the four `questionAliases.ja` additions, directly necessary test expectation/assertion updates, the source-index localization bullet, and assigned handoff/review docs. Do not include `.coverage`.
