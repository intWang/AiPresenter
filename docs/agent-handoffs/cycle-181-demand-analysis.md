# Cycle 181 Demand Analysis: Localized Participant Privacy

Date: 2026-05-17

## User Need

Chinese, Japanese, and Spanish users need the same Participants boundary added for English in Cycle 180:

- Navigation: open or locate the Participants panel/list/control surface.
- Disclosure: reveal who is present, names, roles, host/moderator identity, or roster details.

Cycle 181 should make localized identity intent answer-only without widening package aliases.

## Repository Signals

- `ringcentral.video.toolbar.participants` already has localized aliases for participant panel/list wording.
- Alias matching is substring-based, so a short localized alias can make identity prompts operable.
- Existing localized Q&A privacy copy covers chat plus participant names, but many natural localized identity variants did not reach that answer.
- English participant privacy matching already runs before package aliases and can be extended safely at runtime.

## Acceptance Criteria

- Safe localized panel prompts route to `ringcentral.video.toolbar.participants`, keep `can_operate is True`, and create an interrupt.
- Localized identity prompts return privacy guidance with `entrypoint_id is None`, `can_operate is False`, and no interrupt.
- Identity intent outranks panel/list wording when the prompt asks for names, roles, host/moderator identity, or who is present.
- Answers stay localized and mention names/roles/private tabs, explicit user request, and verified visible context.
- Controller and session regressions prove a Chinese mixed-meta identity prompt remains text-only.
- Do not add or broaden `questionAliases`.

## In-Scope Examples

Rejected identity examples:

- Chinese: `列出参会者`, `谁在会议里`, `读参会人名字`, `谁是主持人或协管员`
- Japanese: `参加者名を読んで`, `参加者の名前を教えて`, `参加者一覧に誰がいますか`, `ホストまたはモデレーターは誰ですか`
- Spanish: `Muestrame los participantes`, `Lista los participantes`, `Muestrame el panel de participantes con nombres`, `Quien esta en la reunion?`, `Quien es host o moderador?`

Safe panel examples:

- Chinese: `请简洁一点，参会者在哪里`, `参会人列表在哪里`, `打开参会人列表`
- Japanese: `参加者一覧はどこですか`, `参加者パネルを開いて`
- Spanish: `Muestrame el panel de participantes`, `Donde esta la lista de participantes?`

## Non-Goals

- Do not read participant names, roles, host/moderator status, or private tabs.
- Do not mute, remove, admit, lock, unlock, or change security settings.
- Do not run live/manual acceptance with real participant data.
- Do not update diagnostics counts unless package YAML changes.
