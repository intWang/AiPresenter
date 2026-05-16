# Cycle 101 Risk Scan: RingCentral Video Japanese Question Aliases

## Scope

Risk review for the next narrow expansion of Japanese `questionAliases` in
`packages/ringcentral-video.yaml`.

Current scan baseline:

- Japanese demo narration: `51/51`
- Japanese Q&A localized questions: `12/12`
- Japanese Q&A localized answers: `12/12`
- Japanese aliases: `3/27` entrypoints, `9` aliases
- Existing Japanese alias entrypoints: microphone, Participants, Chat
- Current package-owned alias total used by doctor tests: `62`
- Current Q&A prompt total used by doctor tests: `71`
- Current doctor substring-risk baseline: `11` Q&A prompts with alias substrings, reported as INFO

This scan should not change YAML, code, tests, profiles, source-index docs, or
git history. The purpose is to guide a later implementation agent toward low
risk aliases that improve natural-language routing without making location
questions look like execution commands.

## Low-Risk Alias Principles

Prefer aliases that are short, explicit, and location-oriented:

- use noun phrases or "place" wording, such as `会議情報`, `会議IDの場所`, `接続品質`, or `表示レイアウト`
- when a settings-like surface is in scope, phrase it as an entrypoint or panel location, not as a request to change a setting
- target entrypoints whose normal route is an orientation popover, menu, or explain-only answer
- keep aliases tied to one visible control, not a broad workflow
- avoid verbs that imply the assistant should do the thing now
- avoid generic labels that could fit many entrypoints, such as `設定`, `メニュー`, `操作`, or `詳細`
- keep each alias unique across entrypoints after normalization
- add a small fixed batch and assert exact counts instead of letting aliases accrete casually

Good Japanese alias posture is "where is this control or entry point?" rather
than "perform this meeting action." A safe alias should still make sense when
the system answers with the entrypoint title and purpose only.

## Recommended First Wave

The lowest-risk first wave should stay close to read-only or orientation
surfaces. Suggested order:

1. `ringcentral.video.top.network-quality`
   - Candidate aliases: `ネットワーク品質`, `接続品質`, `通信状態`
   - Why first: it opens diagnostic status, has a troubleshooting Q&A already related to this entrypoint, and does not send visible meeting signals or expose meeting content by default.
   - Avoid: `音声が途切れる`, `映像が途切れる`, or `直して`; those sound like troubleshooting commands and overlap the existing Japanese Q&A prompt.

2. `ringcentral.video.top.meeting-info`
   - Candidate aliases: `会議情報`, `会議IDの場所`, `会議リンクの場所`
   - Why first: the route is explicitly explain-only in question handling, and the wording asks for location rather than copying or reading private values.
   - Avoid: `会議IDを教えて`, `リンクをコピー`, `招待リンク`; these invite privacy reads or copy actions.

3. `ringcentral.video.top.views`
   - Candidate aliases: `表示レイアウト`, `表示メニュー`
   - Why first: the intended action is to locate the layout menu, not choose a layout.
   - Avoid: `ギャラリー表示にする`, `全画面にする`, `表示を切り替えて`; these imply state changes.

4. `ringcentral.video.overview`
   - Candidate aliases: `会議の全体像`, `コントロールマップ`
   - Why first: `openSteps` is empty and the route is orientation-only.
   - Avoid: `全部操作`, `まとめて実行`, or broad phrases that suggest AiPresenter can control the whole meeting.

If this exact first wave is chosen, the expected Japanese alias count becomes
`7/27` entrypoints and `19` aliases, and the package-owned alias total becomes
`72`. If the implementation picks a smaller subset, write the exact target
counts before editing and make the tests assert those numbers.

## Defer Or Treat As Medium Risk

These may be useful later, but should not be mixed into the first low-risk
batch unless the implementation also adds focused routing and privacy tests:

- `ringcentral.video.toolbar.video-menu`: aliases like `カメラメニュー` or `ビデオ設定入口` are plausible, but "camera" language can drift into device switching.
- `ringcentral.video.toolbar.audio-menu`: aliases like `音声メニュー` or `スピーカー設定` can expose device recovery, but the menu includes leave-computer-audio and device details.
- `ringcentral.video.toolbar.invite` and `ringcentral.video.main.add-coworkers`: location aliases may be safe, but Japanese `招待` wording easily becomes "invite someone now" and can expose links, names, emails, or suggestions.
- `ringcentral.video.top.report-issue`: it opens a blocking modal and can become a submission workflow.
- `ringcentral.video.toolbar.react` and `ringcentral.video.toolbar.raise-hand`: both are visible meeting signals; defer until tests prove location questions stay answer-only and no signal is sent.

## High-Risk Avoidance For This Round

Do not add Japanese aliases for these entrypoints in this cycle:

- `Leave`: `退出`, `退室`, `終了`, and `会議を終了` are destructive or ambiguous between leaving for self and ending for everyone. A short alias could route a casual "where is Leave" question into an exit boundary, and command wording is hard to separate from intent in Japanese.
- `Recording`: `録画`, `録音`, `記録`, and `録画開始` affect consent, policy, and all participants. The package already has a Japanese Q&A safety prompt for recording; aliases here can collide with answer-only safety guidance.
- `Share`: `共有`, `画面共有`, and `共有画面` overlap shared-screen privacy Q&A and can imply starting a screen share or reading private shared content.
- `Settings`: `設定` is too broad. It can mean audio, video, background, translation, join preferences, general settings, or policy-dependent controls. Adding it as an alias would create cross-entrypoint ambiguity and a large modal state surface.
- `Notes`: `ノート`, `文字起こし`, `字幕`, and `トランスクリプト` overlap notes, captions, transcription, translation, post-meeting artifacts, and privacy reads. Notes can also start meeting-state-changing behavior.

The theme is not that these features are forbidden forever. They need their own
explicit demand analysis, answer-only routing checks, privacy copy checks, and
possibly confirmation UX before they become Japanese aliases.

## Japanese Word-Form Risks

Japanese aliases are substring-matched after Q&A matching. That creates several
specific risks:

- Synonym overlap: `参加者`, `メンバー`, `人`, and `招待` can blur Participants, Invite, Add coworkers, host controls, and privacy Q&A.
- Q&A prompt substring overlap: existing prompts contain words like `チャット`, `参加者名`, `音声`, `ビデオ`, `ノート`, `文字起こし`, `字幕`, `録画`, and `共有画面`. Q&A-first matching still protects exact or fragment Q&A matches, but new aliases may increase the INFO substring-risk count.
- Cross-entrypoint duplicate risk: `背景` could belong to background settings, More background, or blur selection; `設定` could belong almost anywhere; `メニュー` is not specific enough.
- Command wording: `開いて`, `押して`, `開始`, `変更`, `切り替えて`, `コピー`, `送信`, `退出`, `終了`, `読んで`, and `要約して` should not be aliases. They describe actions, not entrypoints.
- Mixed script variants: if an alias uses an English product term such as `Network quality`, `Invite`, `Share`, `Notes`, or `Leave`, pair it with Japanese location wording and ensure it does not duplicate another language alias after normalization.
- Short noun ambiguity: very short aliases can match inside longer prompts. Prefer slightly longer, control-specific phrases when the short noun appears in safety Q&A.

## Test And Doctor Guardrails

A later implementation should keep the test movement narrow and exact:

- `tests/unit/test_material_packages.py`
  - update the Japanese alias ownership test to include the new exact alias set
  - assert `report.entrypoints_with_aliases` and `report.alias_total` exactly
  - keep demo narration and Q&A localization counts unchanged at `51/51`, `12/12`, and `12/12`

- `tests/unit/test_questions.py`
  - add direct Japanese routing examples with `_ENTRYPOINT_ALIASES` monkeypatched to `{}` so package-owned aliases are the thing being tested
  - add "stays Q&A" tests for any alias that appears inside an existing Japanese Q&A prompt
  - assert `can_operate` stays false for explain-only or risky surfaces and true only for intentionally safe popover/menu openings

- `tests/unit/test_diagnostics.py` and doctor CLI tests
  - update `question aliases` from `62` to the exact new package-owned alias total
  - require no cross-entrypoint duplicate aliases
  - require `qa alias overlap` to remain OK with `71` Q&A prompts
  - treat `qa alias substring risk` INFO as acceptable only if the count/details change for expected, reviewed Japanese substrings
  - do not convert substring INFO into a WARN/FAIL workaround unless the routing is actually unsafe

- CLI localization report
  - keep `Localization report: 51/51 demo steps, 12/12 Q&A questions, 12/12 Q&A answers localized for ja.`
  - change only the `questionAliases.ja present on ...` line to the exact new alias count
  - keep `--require-complete` passing; alias coverage is not the completeness gate

Recommended command set for the later implementation:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py tests\unit\test_questions.py tests\unit\test_diagnostics.py tests\unit\test_cli.py
.\.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language ja
.\.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language ja --require-complete
.\.venv\Scripts\ai-presenter doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo
git diff --check
```

Doctor output may still include an INFO-level Q&A alias substring risk. That is
acceptable when Q&A-first matching is preserved, no unsafe exact overlap appears,
and the changed INFO detail is expected from the new aliases.

## Demo And Q&A Coverage Boundaries

This alias expansion should not change demo or Q&A coverage:

- do not add or edit `localizedText.ja`
- do not add or edit Q&A questions or answers
- do not retarget demo steps
- do not add routes, selectors, `openSteps`, cleanup behavior, action offsets, presenter notes, or operation handlers
- do not weaken tests that protect Share, Recording, Notes, Leave, Settings, participant names, chat contents, shared-screen contents, meeting IDs, invite links, or device/account details

If an alias needs new safety wording to feel acceptable, that is a sign it
belongs in a separate Q&A or confirmation-safety cycle, not this alias-only
slice.

## Reviewer Checklist

- Confirm this risk-scan agent changed only `docs/agent-handoffs/cycle-101-risk-scan.md`.
- Confirm no YAML, code, tests, source-index docs, profiles, fixtures, or generated files changed in this scan.
- Confirm the proposed first implementation batch uses fixed exact counts before editing.
- Confirm low-risk aliases are short, clear, and location/entrypoint oriented.
- Confirm no aliases are added for Leave, Recording, Share, Settings, Notes, or generic More.
- Confirm any later implementation preserves Q&A-first matching and exact Q&A coverage.
- Confirm duplicate alias doctor checks stay OK.
- Confirm `.coverage` is not staged.

## Commit Hygiene

This risk-scan agent should create only
`docs/agent-handoffs/cycle-101-risk-scan.md` and should not commit.

At scan time, `git status --short` showed `.coverage` already modified before
this document was created. Treat it as existing or parallel-agent/generated
state:

- do not stage `.coverage`
- do not overwrite, revert, normalize, or format `.coverage`
- do not revert any files, because other agents and the main session are working in the same repo
- re-check `git status --short` before staging in any later implementation session
- keep any later implementation commit narrow: Japanese alias YAML plus directly necessary tests only
- do not stage unrelated handoff docs, generated artifacts, screenshots, logs, `.coverage`, or other agents' WIP

No commit should be made by this risk-scan agent.
