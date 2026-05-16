# Cycle 101 Demand Analysis: Japanese Question Aliases

## Scope

Cycle 101 should move from completed Japanese demo narration into a narrow Japanese `questionAliases` slice for RingCentral Video. This analysis only defines the next implementation target. It does not change YAML, code, tests, profiles, coverage files, or git history.

Parallel-work note: `.coverage` was already dirty during this analysis and should be ignored.

## Baseline Confirmed

Commands run during analysis:

```powershell
.\.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language ja
.\.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language ja --require-complete
.\.venv\Scripts\ai-presenter doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo
```

Current Japanese localization state:

- Demo narration is complete: `51/51`.
- `meeting-control-map-demo` is complete: `22/22`.
- Japanese Q&A is complete: `12/12` localized questions and `12/12` localized answers.
- `questionAliases.ja` is still partial: `3/27` entrypoints and `9` aliases.
- Current Japanese aliases cover only:
  - `ringcentral.video.toolbar.audio`: `マイク`, `ミュート`, `音声`
  - `ringcentral.video.toolbar.participants`: `参加者`, `参加者一覧`, `参加者パネル`
  - `ringcentral.video.toolbar.chat`: `チャット`, `チャットパネル`, `メッセージ`
- Doctor currently reports `62 package-owned aliases have no cross-entrypoint duplicates`, `71 Q&A question prompts have no unsafe package-owned alias overlaps`, and no warnings.

## User Need

Japanese users should be able to ask natural questions such as:

- `マイク設定はどこですか`
- `スピーカー設定を確認したい`
- `カメラはどこですか`
- `ビデオ設定はどこですか`
- `ネットワーク品質を見たい`
- `会議情報はどこですか`
- `会議IDを確認したい`

These should route to the correct RingCentral Video entrypoint answer without requiring English control names or exact demo wording.

The feature is question routing only. It should improve explainability and lookup behavior, not broaden what AiPresenter may execute automatically.

## Recommended Slice

Recommend adding Japanese aliases to 4 entrypoints, 3 aliases each. This advances coverage from `3/27`, `9 aliases` to `7/27`, `21 aliases` while staying small enough for focused review.

| Priority | Entrypoint | Proposed aliases | Why this slice |
| --- | --- | --- | --- |
| P0 | `ringcentral.video.toolbar.audio-menu` | `音声設定`, `マイク設定`, `スピーカー設定` | High-frequency support need. The entrypoint opens the microphone/speaker menu with `cleanup: escape`; question flow already treats it as not directly operable because its purpose includes leave-computer-audio risk wording. Complements existing broad `マイク` alias on the microphone toggle. |
| P0 | `ringcentral.video.toolbar.video-menu` | `カメラ`, `カメラ設定`, `ビデオ設定` | Covers the user-facing camera/video-settings need without routing broad camera questions to the direct camera toggle. The entrypoint opens a menu with `cleanup: escape` and points toward camera selection and More video settings. |
| P1 | `ringcentral.video.top.network-quality` | `ネットワーク品質`, `接続品質`, `通信状態` | Low-risk diagnostic popover for audio/video troubleshooting. It is already a related entrypoint for the Japanese Q&A item about interrupted audio/video, so this makes the direct lookup path consistent. |
| P1 | `ringcentral.video.top.meeting-info` | `会議情報`, `会議ID`, `会議リンク` | Common lookup need, but privacy-sensitive because the popover can expose IDs and links. Runtime already has `ringcentral.video.top.meeting-info` in `_QUESTION_EXPLAIN_ONLY_ENTRYPOINT_IDS`, so matched questions remain answer-only. |

In-memory validation of this alias set produced:

- `questionAliases.ja`: `7/27` entrypoints, `21 aliases`.
- Package-owned aliases total: `62 -> 74`.
- Doctor-style diagnostics:
  - `question aliases`: OK, `74 package-owned aliases have no cross-entrypoint duplicates`.
  - `qa alias overlap`: OK, `71 Q&A question prompts have no unsafe package-owned alias overlaps`.
  - `qa alias substring risk`: remains the existing INFO count, not a new warning.

## Deferred Candidates

Do not include these in the Cycle 101 slice:

- `ringcentral.video.toolbar.video`: defer direct camera-toggle aliases. Its purpose is to toggle local camera on/off, so broad aliases like `カメラ` are safer on `video-menu` for now.
- `ringcentral.video.toolbar.share`: screen sharing starts a potentially sensitive sharing flow.
- `ringcentral.video.more.recording`: recording has consent and privacy implications.
- `ringcentral.video.toolbar.leave`: leaving or ending the meeting is a destructive boundary.
- `ringcentral.video.more.settings` and broad Settings aliases: too broad and likely to route ambiguous user intent into a deep modal.
- `ringcentral.video.toolbar.more`: too broad and contains deeper/riskier actions.
- `ringcentral.video.top.report-issue`: opens a blocking report dialog and can look like filing an issue.

If direct camera toggle, Share, Recording, Leave, or broad Settings aliases become necessary, handle each as a separate safety-reviewed slice with explicit negative tests.

## Safety Boundaries

- Add only `questionAliases.ja` entries to the selected entrypoints.
- Do not change `openSteps`, locators, cleanup behavior, routes, Q&A, demo narration, runtime matching, or `_can_operate`.
- Aliases should route questions to entrypoint explanations. They must not imply that AiPresenter clicked, selected, toggled, recorded, shared, invited, left, submitted, or changed any meeting setting.
- Keep `meeting-info` answer-only. Its aliases may match `会議ID` and `会議リンク`, but the answer should summarize the entrypoint purpose and preserve the existing privacy gate.
- Keep Q&A-first behavior intact. Existing Japanese Q&A items such as `音声とビデオの準備を確認するにはどうすればいいですか` and `音声や映像が途切れるときはどうすればいいですか` should still return their curated Q&A answers before alias fallback.
- Avoid exact duplicate normalized aliases across entrypoints. Do not reuse current aliases `マイク`, `ミュート`, `音声`, `参加者`, `参加者一覧`, `参加者パネル`, `チャット`, `チャットパネル`, or `メッセージ` on another entrypoint.

## Acceptance Criteria

After implementation:

- `questionAliases.ja` advances from `3/27` entrypoints and `9 aliases` to exactly `7/27` entrypoints and `21 aliases`.
- Total package-owned aliases advances from `62` to exactly `74`.
- Japanese demo coverage remains `51/51`.
- `meeting-control-map-demo` remains `22/22`.
- Japanese Q&A remains `12/12` localized questions and `12/12` localized answers.
- `.\.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language ja --require-complete` still exits successfully.
- Doctor has no duplicate alias warning and no unsafe Q&A alias overlap warning.
- Expected doctor lines after implementation should include:

```text
[OK] question aliases: 74 package-owned aliases have no cross-entrypoint duplicates
[OK] qa alias overlap: 71 Q&A question prompts have no unsafe package-owned alias overlaps
```

The existing `qa alias substring risk` INFO may remain INFO. Do not treat it as a regression unless the count or examples change because of the new Japanese aliases.

## Suggested Test Assertions

Update focused material-package assertions:

- `build_localization_status(package, language="ja").entrypoints_with_aliases == 7`
- `build_localization_status(package, language="ja").alias_total == 21`
- The four selected entrypoints have exactly the proposed Japanese alias lists.
- `ringcentral.video.toolbar.video` still has no `questionAliases.ja` in this slice.
- Demo and Q&A coverage assertions remain `51/51`, `22/22`, `12/12`, and `12/12`.

Add or update question-routing assertions with legacy aliases disabled:

```python
expected = {
    "マイク設定はどこですか": "ringcentral.video.toolbar.audio-menu",
    "スピーカー設定はどこですか": "ringcentral.video.toolbar.audio-menu",
    "カメラはどこですか": "ringcentral.video.toolbar.video-menu",
    "ビデオ設定はどこですか": "ringcentral.video.toolbar.video-menu",
    "ネットワーク品質を確認したい": "ringcentral.video.top.network-quality",
    "接続品質はどこですか": "ringcentral.video.top.network-quality",
    "会議情報はどこですか": "ringcentral.video.top.meeting-info",
    "会議IDを確認したい": "ringcentral.video.top.meeting-info",
}
```

Also assert the key safety outcomes:

- `answer_question(... "会議IDを確認したい" ...).can_operate is False`
- `answer_question(... "マイク設定はどこですか" ...).entrypoint_id == "ringcentral.video.toolbar.audio-menu"`
- `answer_question(... "カメラはどこですか" ...).entrypoint_id == "ringcentral.video.toolbar.video-menu"`
- `answer_question(... "カメラはどこですか" ...).entrypoint_id != "ringcentral.video.toolbar.video"`
- Existing Japanese Q&A safety cases still win over aliases:
  - `チャット内容や参加者名を読み上げられますか` stays answer-only.
  - `音声や映像が途切れるときはどうすればいいですか` still returns the curated troubleshooting Q&A answer and related `network-quality` entrypoint.

Update CLI and diagnostics assertions:

- `tests/unit/test_cli.py` Japanese localization report line changes to `questionAliases.ja present on 7/27 entrypoints (21 aliases)`.
- `tests/unit/test_diagnostics.py` question-alias OK detail changes from `62 package-owned aliases` to `74 package-owned aliases`.
- Doctor CLI expectation changes from `62 package-owned aliases` to `74 package-owned aliases`.
- `qa alias overlap` remains OK.

Suggested verification commands after implementation:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py tests\unit\test_questions.py tests\unit\test_cli.py tests\unit\test_diagnostics.py
.\.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language ja
.\.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language ja --require-complete
.\.venv\Scripts\ai-presenter doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo
git diff --check -- packages/ringcentral-video.yaml tests/unit/test_material_packages.py tests/unit/test_questions.py tests/unit/test_cli.py tests/unit/test_diagnostics.py
```

## Do Not Do

- Do not add aliases to Leave, Recording, Share, broad Settings, More, Report issue, or direct camera toggle in this slice.
- Do not change permission logic to make a newly matched risky entrypoint operable.
- Do not change Q&A answers, localized Q&A prompts, demo flows, demo narration, presenters, profiles, locators, or runtime matching.
- Do not add more than the 12 proposed Japanese aliases unless a follow-up analysis explicitly scopes it.
- Do not update unrelated docs or source-index wording unless the implementation assignment explicitly asks for it.
- Do not touch `.coverage`.
- Do not commit from the implementation agent unless explicitly requested.
