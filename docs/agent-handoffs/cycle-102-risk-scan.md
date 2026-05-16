# Cycle 102 Risk Scan: Japanese Read-Only Meeting Info And Overview Aliases

## Scope

Risk review for a possible next narrow Japanese `questionAliases` expansion in
`packages/ringcentral-video.yaml`.

This scan is documentation-only. Do not change YAML, code, tests, profiles,
fixtures, source-index docs, generated files, or git history in this cycle.

Current baseline after Cycle 101:

- Japanese demo narration: `51/51`
- Japanese Q&A localized questions: `12/12`
- Japanese Q&A localized answers: `12/12`
- Japanese aliases: `7/27` entrypoints, `21` aliases
- Package-owned aliases: `74`
- Doctor Q&A prompt total: `71`
- Doctor substring-risk baseline: `11` Q&A prompts, INFO level
- Existing Japanese alias entrypoints: Network quality, View layout, audio, audio menu, camera menu, Participants, Chat
- No Japanese aliases currently exist for `ringcentral.video.top.meeting-info` or `ringcentral.video.overview`

The user explicitly asked this scan to cover whether `meeting-info` aliases
could induce reading meeting IDs/links or copying invite links, and whether
`overview` or `control-map` aliases could overpromise complete UI control.

## Core Finding

`meeting-info` is safe only as a read-only location alias surface. It is not
safe as a value-retrieval or invite-link workflow surface.

`overview` is safer than `meeting-info` because it has no `openSteps` and is
orientation-only, but broad "control map" language can still overpromise that
AiPresenter controls every RingCentral Video UI surface. The alias wording must
make it clear that the presenter explains the meeting surface map; it must not
promise complete automation, coverage, or execution.

Do not touch or broaden aliases for `Share`, `Recording`, `Leave`, `Settings`,
`Notes`, `Invite`, or `Add coworkers` in the implementation that follows this
scan.

## Meeting Info Risk

The entrypoint purpose currently says Meeting information includes meeting
title, host, meeting ID, copy link, dial-in info, encryption, and an end-to-end
encryption option. Its presenter notes already warn that the popover can expose
private meeting identifiers and copy-link controls, and the question layer
forces `ringcentral.video.top.meeting-info` to `can_operate == False`.

That means Japanese aliases can help users find the control, but they must not
sound like instructions to reveal or copy private values.

Safe alias posture:

- ask where the Meeting information entrypoint is
- use "場所" or "入口" wording
- keep the phrase anchored to the control, not the value
- preserve answer-only behavior through tests

Recommended safe Japanese aliases for `ringcentral.video.top.meeting-info`:

- `会議情報の場所`
- `Meeting information の場所`
- `会議詳細の入口`

Optional but higher scrutiny:

- `会議IDの場所`
- `会議リンクの場所`

These optional forms are location-oriented, but they mention sensitive values.
Only add them if the implementation also adds direct answer-only tests proving
they do not open the popover from Q&A routing and do not imply reading or
copying the values.

Prohibited meeting-info aliases:

- `会議IDを教えて`
- `会議IDを読んで`
- `会議IDを表示して`
- `会議リンクを教えて`
- `会議リンクを読んで`
- `リンクをコピー`
- `招待リンク`
- `招待リンクをコピー`
- `会議情報をコピー`
- `ダイヤルインを読んで`
- `ホスト名を読んで`

Risk decision: a first implementation should prefer only the first three safe
aliases. Defer `会議IDの場所` and `会議リンクの場所` unless the slice is explicitly
privacy-test-heavy.

## Overview And Control-Map Risk

`ringcentral.video.overview` has `openSteps: []` and the control-map flow uses
it for orientation and summary narration. This is a good candidate for Japanese
read-only aliases as long as the wording does not imply AiPresenter can operate
the whole UI.

Safe alias posture:

- present the meeting window as a map or overview
- explain where categories of controls live
- avoid "all controls", "everything", "fully operate", or "complete UI" claims
- avoid action verbs that imply the alias will start a whole demo flow or
  execute controls

Recommended safe Japanese aliases for `ringcentral.video.overview`:

- `会議画面の概要`
- `会議画面の見取り図`
- `コントロールの全体像`

Acceptable with caution:

- `コントロールマップ`

This mirrors the flow title and is natural, but reviewers should confirm the
answer remains the `Meeting overview` entrypoint answer, not a promise to run
the entire `meeting-control-map-demo` or cover every future RingCentral control.

Prohibited overview/control-map aliases:

- `全部の操作`
- `すべて操作`
- `全コントロールを操作`
- `UIを全部制御`
- `完全なコントロール`
- `全機能を説明`
- `全部実行`
- `まとめて操作`
- `フル操作`
- `完全対応`

Risk decision: overview aliases are lower privacy risk than meeting-info, but
they need overclaim tests. The answer should describe current package scope and
orientation, not complete RingCentral Video coverage.

## Surfaces To Leave Untouched

Do not add or modify Japanese aliases, Q&A, routes, localized text, or tests for
these surfaces in the next implementation slice:

- `Share`
- `Recording`
- `Leave`
- `Settings`
- `Notes`
- `Invite`
- `Add coworkers`

Also do not add broad aliases for `More`, background settings, host controls, or
participant management as part of this slice. Those belong to separate risk
reviews.

## Doctor And Q&A Overlap Guardrails

Q&A-first matching currently runs before entrypoint alias fallback, exact Q&A
prompts are indexed by normalized text, and package aliases are substring
matched by longest-first order. Doctor already reports cross-entrypoint duplicate
aliases, exact Q&A alias overlap, and INFO-level Q&A alias substring risk.

Guardrails for a later implementation:

- Keep `meeting-info` in the explicit explain-only entrypoint set so
  `can_operate` remains `False`.
- Add no alias that exactly equals a Japanese Q&A prompt.
- Avoid aliases that appear inside sensitive Q&A prompts unless the Q&A's
  `relatedEntrypointIds` make that overlap safe.
- Treat any new doctor substring-risk count as acceptable only when the changed
  detail is expected, reviewed, and still protected by Q&A-first matching.
- Require doctor `question aliases` to remain OK with no cross-entrypoint
  duplicates.
- Require doctor `qa alias overlap` to remain OK for all `71` Q&A prompts.
- Do not weaken the existing INFO-only substring diagnostic into silence.
- Keep alias counts exact in tests; no loose greater-than assertions.
- Keep localization completeness unchanged: `51/51`, `12/12`, `12/12`.

Specific Q&A overlaps to protect:

- Meeting-info aliases must not shadow invite, shared-screen, participant-name,
  recording, notes/transcript, post-meeting artifact, or host-control Q&A.
- `会議リンク` and `招待リンク` are not equivalent. Do not use `招待リンク` for
  meeting-info because it drifts into Invite/Add coworkers behavior.
- Overview aliases must not answer questions about sending reactions, raising a
  hand, sharing the screen, recording, leaving, or changing settings.
- `コントロール` can appear broadly; prefer longer phrases like
  `コントロールの全体像` when routing to overview.

## Test Suggestions

A later implementation should use TDD and keep the movement small.

Recommended focused tests:

- `tests/unit/test_material_packages.py`
  - update `test_ringcentral_package_owns_japanese_aliases_for_meeting_control_routes` with the exact new aliases
  - assert the exact new `questionAliases.ja` entrypoint count and alias total
  - assert `Share`, `Recording`, `Leave`, `Settings`, `Notes`, `Invite`, and
    `Add coworkers` still do not gain Japanese aliases

- `tests/unit/test_questions.py`
  - with `_ENTRYPOINT_ALIASES` monkeypatched to `{}`, assert safe meeting-info
    aliases route to `ringcentral.video.top.meeting-info` and `can_operate is False`
  - add Japanese privacy questions such as `会議IDを読んで`,
    `会議リンクをコピーして`, and `招待リンクをコピーして` and assert they are
    answer-only, never operable, and never route to Invite/Add coworkers
  - assert safe overview aliases route to `ringcentral.video.overview` and
    `can_operate is False`
  - add overclaim prompts such as `UIを全部制御できますか` and
    `全コントロールを操作して` and assert no operable response is produced

- `tests/unit/test_cli.py` and `tests/unit/test_diagnostics.py`
  - update doctor package-owned alias count exactly
  - keep Q&A prompt total at `71`
  - keep `qa alias overlap` OK
  - review and update the substring INFO count only if the new aliases change
    it for expected reasons

Suggested manual verification commands for the later implementation:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py tests\unit\test_questions.py tests\unit\test_cli.py tests\unit\test_diagnostics.py
.\.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language ja
.\.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language ja --require-complete
.\.venv\Scripts\ai-presenter doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo
git diff --check
```

## Suggested Narrow Implementation Shape

Safest next batch:

- `ringcentral.video.top.meeting-info`
  - `会議情報の場所`
  - `Meeting information の場所`
  - `会議詳細の入口`
- `ringcentral.video.overview`
  - `会議画面の概要`
  - `会議画面の見取り図`
  - `コントロールの全体像`

Expected count movement for this exact batch:

- `questionAliases.ja`: `7/27` entrypoints, `21` aliases -> `9/27` entrypoints, `27` aliases
- total package-owned aliases: `74` -> `80`

Do not add `会議IDの場所`, `会議リンクの場所`, or `コントロールマップ` in this
first slice unless the implementation explicitly wants the extra privacy and
overclaim tests. If those three are added too, write the revised counts before
editing and make tests assert them exactly.

## Reviewer Checklist

- Confirm this risk-scan agent changed only `docs/agent-handoffs/cycle-102-risk-scan.md`.
- Confirm no YAML, code, tests, source-index docs, profiles, fixtures, or generated files changed.
- Confirm meeting-info aliases are location-only and never value-read, copy, invite, or link-sharing commands.
- Confirm overview/control-map aliases explain current meeting-surface orientation and do not promise complete UI control.
- Confirm `Share`, `Recording`, `Leave`, `Settings`, `Notes`, `Invite`, and `Add coworkers` remain untouched.
- Confirm later implementation preserves Q&A-first matching, exact doctor counts, and explain-only behavior.

## Commit Hygiene

This risk-scan agent should not stage or commit anything.

Before any later implementation stage, re-check `git status --short` and stage
only the intended YAML/test/source-index/handoff files for that implementation.
Do not stage unrelated handoff docs, generated artifacts, logs, screenshots,
`.coverage`, or other agents' work.
