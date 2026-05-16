# Cycle 102 Demand Analysis: Japanese Read-Only Meeting Info And Overview Aliases

## Scope

This is a demand-analysis handoff for the next Japanese `questionAliases` slice in `packages/ringcentral-video.yaml`.

This document is analysis only. It does not change YAML, code, tests, profiles, coverage files, or git history.

Parallel-work note: `.coverage` is already dirty and should be ignored. `docs/agent-handoffs/cycle-102-risk-scan.md` already exists from another agent and was read as background only.

## Baseline Verified

Commands run during this analysis:

```powershell
.\.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language ja
.\.venv\Scripts\ai-presenter doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo
```

Current package state:

- Japanese demo narration is complete: `51/51`.
- `meeting-control-map-demo` is complete: `22/22`.
- Japanese Q&A is complete: `12/12` localized questions and `12/12` localized answers.
- `questionAliases.ja` is currently `7/27` entrypoints and `21 aliases`.
- Total package-owned aliases are currently `74`.
- Doctor currently reports `11 ok, 1 info, 0 warnings, 0 failed`.
- Doctor duplicate/overlap baseline:
  - `[OK] question aliases: 74 package-owned aliases have no cross-entrypoint duplicates`
  - `[OK] qa alias overlap: 71 Q&A question prompts have no unsafe package-owned alias overlaps`
  - `[INFO] qa alias substring risk: 11 Q&A question prompts ...`

Current Japanese alias coverage is limited to:

- `ringcentral.video.toolbar.audio`
- `ringcentral.video.toolbar.participants`
- `ringcentral.video.toolbar.chat`
- `ringcentral.video.top.network-quality`
- `ringcentral.video.top.views`
- `ringcentral.video.toolbar.audio-menu`
- `ringcentral.video.toolbar.video-menu`

No Japanese aliases currently exist for `ringcentral.video.top.meeting-info` or `ringcentral.video.overview`.

## User Need

Japanese users should be able to ask location/orientation questions and receive explanations without needing English control names.

Target user questions:

- `会議情報はどこですか` - equivalent to the demand phrasing `会议信息在哪里`.
- `会議IDの場所を知りたい`
- `会議リンクの場所はどこですか`
- `会議の全体像を教えて`
- `コントロールマップはありますか`

The desired behavior is answer/explanation only. The alias should help users find or understand the control area; it should not copy a meeting link, read a meeting ID, start a demo flow, change settings, share, record, invite, or leave.

## Recommended Slice

Recommend adding Japanese aliases to exactly 2 entrypoints, 3 aliases each. This is the narrowest slice that covers the requested user need while avoiding a third entrypoint that would drift toward modal/reporting or collaboration surfaces.

| Priority | Entrypoint | Proposed `questionAliases.ja` | Rationale |
| --- | --- | --- | --- |
| P0 | `ringcentral.video.overview` | `会議の全体像`, `会議画面の概要`, `コントロールマップ` | Lowest-risk target. The entrypoint has `openSteps: []`, and `_can_operate` returns `False` for entries with no open steps. Existing control-map narration already uses overview for orientation and summary. Keep this as map/orientation wording only. |
| P1 | `ringcentral.video.top.meeting-info` | `会議情報はどこ`, `会議IDの場所`, `会議リンクの場所` | Covers the requested meeting-info, meeting-ID-location, and meeting-link-location questions. This is privacy-sensitive because the popover can expose meeting ID, link, dial-in details, host, and copy-link controls. Runtime already includes this entrypoint in `_QUESTION_EXPLAIN_ONLY_ENTRYPOINT_IDS`, so alias matches remain `can_operate is False`. |

Do not add a third entrypoint in Cycle 102. The obvious remaining top-bar candidate, `ringcentral.video.top.report-issue`, opens a blocking modal and is less read-only than overview. Collaboration candidates such as Invite/Add coworkers are explicitly out of scope because they expose names, emails, suggestions, and invite links.

## Candidate Validation

I validated the proposed 6 aliases in memory only, without writing YAML. Result:

- `questionAliases.ja`: `9/27` entrypoints, `27 aliases`.
- Total package-owned aliases: `80`.
- `question aliases`: OK, `80 package-owned aliases have no cross-entrypoint duplicates`.
- `qa alias overlap`: OK, `71 Q&A question prompts have no unsafe package-owned alias overlaps`.
- `qa alias substring risk`: unchanged INFO baseline, `11` prompts.

In-memory routing checks with legacy aliases disabled by package ownership behavior:

- `会議の全体像を教えて` -> `ringcentral.video.overview`, `can_operate=False`
- `会議画面の概要はどこですか` -> `ringcentral.video.overview`, `can_operate=False`
- `コントロールマップはありますか` -> `ringcentral.video.overview`, `can_operate=False`
- `会議情報はどこですか` -> `ringcentral.video.top.meeting-info`, `can_operate=False`
- `会議IDの場所を知りたい` -> `ringcentral.video.top.meeting-info`, `can_operate=False`
- `会議リンクの場所はどこですか` -> `ringcentral.video.top.meeting-info`, `can_operate=False`

Negative in-memory checks also stayed non-operable:

- `会議IDを読んで` -> no operable response
- `会議リンクをコピーして` -> no operable response
- `招待リンクをコピーして` -> no operable response
- `UIを全部制御できますか` -> no operable response
- `全コントロールを操作して` -> no operable response

## Safety Boundaries

`meeting-info` boundaries:

- Treat the matched answer as answer-only/location-only.
- Do not copy links, click copy-link controls, read exact meeting IDs, read dial-in details, read host/account details, or read encryption-specific values unless the user explicitly requests that exact value and visible context has been verified.
- Even with explicit value requests, this alias slice should not implement value-reading or copy behavior. That belongs to a separate privacy-reviewed feature.
- Use location wording only. Do not add aliases such as `会議IDを教えて`, `会議IDを読んで`, `会議リンクをコピー`, `招待リンク`, `ダイヤルインを読んで`, or `ホスト名を読んで`.

`overview` boundaries:

- Use orientation only: meeting window overview, control categories, and where major areas live.
- Do not imply AiPresenter can operate every control, start the full `meeting-control-map-demo`, or cover all future RingCentral Video features.
- Avoid aliases like `全部の操作`, `すべて操作`, `全コントロールを操作`, `UIを全部制御`, `全部実行`, or `完全対応`.

General boundaries:

- Add only the two `questionAliases.ja` blocks above.
- Do not change `openSteps`, locators, cleanup behavior, operation logic, Q&A, demo narration, runtime matching, profiles, or source code.
- Preserve `_QUESTION_EXPLAIN_ONLY_ENTRYPOINT_IDS` behavior for `ringcentral.video.top.meeting-info`.
- Preserve Q&A-first matching.

## Do Not Do

Do not add Japanese aliases to these entrypoints in Cycle 102:

- `Share`
- `Recording`
- `Leave`
- `Settings`
- `Notes`
- `Invite`
- `Add coworkers`

Also avoid broad `More`, background settings, host controls, participant-management controls, direct camera toggle, and Report issue in this slice.

## Acceptance Criteria

After implementation:

- `questionAliases.ja` advances from `7/27` entrypoints and `21 aliases` to exactly `9/27` entrypoints and `27 aliases`.
- Total package-owned aliases advance from `74` to exactly `80`.
- Japanese demo coverage remains `51/51`.
- `meeting-control-map-demo` remains `22/22`.
- Japanese Q&A remains `12/12` localized questions and `12/12` localized answers.
- `.\.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language ja --require-complete` still exits successfully.
- Doctor has no duplicate alias warning and no unsafe Q&A alias overlap warning.
- Expected doctor lines after implementation include:

```text
[OK] question aliases: 80 package-owned aliases have no cross-entrypoint duplicates
[OK] qa alias overlap: 71 Q&A question prompts have no unsafe package-owned alias overlaps
```

The existing `qa alias substring risk` INFO should remain INFO. The validated candidate set keeps the count at `11`; if an implementation changes that count, treat it as a review item and explain why the new substring is still protected by Q&A-first matching.

## Suggested Test Assertions

Material package and localization status:

- `build_localization_status(package, language="ja").entrypoints_with_aliases == 9`
- `build_localization_status(package, language="ja").alias_total == 27`
- `ringcentral.video.overview.question_aliases["ja"] == ["会議の全体像", "会議画面の概要", "コントロールマップ"]`
- `ringcentral.video.top.meeting-info.question_aliases["ja"] == ["会議情報はどこ", "会議IDの場所", "会議リンクの場所"]`
- `ringcentral.video.overview.open_steps == []`
- `ringcentral.video.top.meeting-info` keeps its existing `cleanup: escape` route and privacy presenter notes.
- `Share`, `Recording`, `Leave`, `Settings`, `Notes`, `Invite`, and `Add coworkers` still have no `questionAliases.ja`.

Question routing with `_ENTRYPOINT_ALIASES` monkeypatched to `{}`:

```python
expected = {
    "会議の全体像を教えて": ("ringcentral.video.overview", False),
    "会議画面の概要はどこですか": ("ringcentral.video.overview", False),
    "コントロールマップはありますか": ("ringcentral.video.overview", False),
    "会議情報はどこですか": ("ringcentral.video.top.meeting-info", False),
    "会議IDの場所を知りたい": ("ringcentral.video.top.meeting-info", False),
    "会議リンクの場所はどこですか": ("ringcentral.video.top.meeting-info", False),
}
```

Privacy and overclaim negative assertions:

- `answer_question(... "会議IDを読んで" ...).can_operate is False`
- `answer_question(... "会議リンクをコピーして" ...).can_operate is False`
- `answer_question(... "招待リンクをコピーして" ...).entrypoint_id != "ringcentral.video.toolbar.invite"`
- `answer_question(... "招待リンクをコピーして" ...).entrypoint_id != "ringcentral.video.main.add-coworkers"`
- `answer_question(... "UIを全部制御できますか" ...).can_operate is False`
- `answer_question(... "全コントロールを操作して" ...).can_operate is False`

Existing safety cases should keep passing:

- `チャット内容や参加者名を読み上げられますか` stays answer-only.
- `音声や映像が途切れるときはどうすればいいですか` still returns the curated Japanese troubleshooting Q&A answer and the related `network-quality` entrypoint.
- `カメラメニューはどこですか` still routes to `ringcentral.video.toolbar.video-menu`, not direct camera toggle.

CLI and diagnostics assertion updates:

- `tests/unit/test_cli.py` Japanese localization report line becomes `questionAliases.ja present on 9/27 entrypoints (27 aliases)`.
- Doctor CLI expectation changes from `74 package-owned aliases` to `80 package-owned aliases`.
- `tests/unit/test_diagnostics.py` question-alias OK detail changes to `80 package-owned aliases have no cross-entrypoint duplicates`.
- `qa alias overlap` remains OK for `71` Q&A prompts.
- `qa alias substring risk` remains INFO and, for this candidate set, remains `11`.

Suggested verification commands after implementation:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py tests\unit\test_questions.py tests\unit\test_cli.py tests\unit\test_diagnostics.py
.\.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language ja
.\.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language ja --require-complete
.\.venv\Scripts\ai-presenter doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo
git diff --check -- packages/ringcentral-video.yaml tests/unit/test_material_packages.py tests/unit/test_questions.py tests/unit/test_cli.py tests/unit/test_diagnostics.py
```
