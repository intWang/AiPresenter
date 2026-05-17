# Cycle 183 Demand Analysis: zh/ja Privacy Parity And Text-Only UX

Date: 2026-05-17

## User Need

Chinese and Japanese operators need the same durable participant privacy guidance that Spanish received in Cycle 182. They also need the operator summary to reflect that a privacy prompt was answered intentionally in text, not that AiPresenter failed to match a control.

## Product Boundary

- Navigation: where/open/show the Participants panel/list may demonstrate `ringcentral.video.toolbar.participants`.
- Identity disclosure: who is present, names, roles, host/moderator identity, or list/show participants as people disclosure stays answer-only.

Identity intent outranks panel/list wording.

## Acceptance Criteria

- `docs/knowledge/ringcentral-video/privacy-matrix.md` includes Chinese and Japanese participant examples.
- Chinese safe examples: `参会者在哪里`, `参会人列表在哪里`, `打开参会人列表`.
- Chinese answer-only examples: `列出参会者`, `谁在会议里`, `读参会人名字`, `谁是主持人或协管员`.
- Japanese safe examples: `参加者一覧はどこですか`, `参加者パネルを開いて`.
- Japanese answer-only examples: `参加者名を読んで`, `参加者の名前を教えて`, `参加者一覧に誰がいますか`, `ホストまたはモデレーターは誰ですか`.
- `describe_question_result()` no longer labels matched Q&A privacy guidance as `no matching safe control`.
- No interrupt or demo starts for privacy Q&A answers.
- No YAML aliases are added.

## Non-Goals

- Do not change voice readiness rules for zh/ja profiles.
- Do not add live RingCentral acceptance using real participant data.
- Do not alter package routing beyond outcome wording and durable docs.
