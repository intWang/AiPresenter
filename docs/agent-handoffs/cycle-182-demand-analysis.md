# Cycle 182 Demand Analysis: Spanish Accent Participant Privacy

Date: 2026-05-17

## User Need

Spanish-speaking operators need participant privacy routing to work across natural accented and unaccented prompts. The product should treat `Muéstrame/Muestrame`, `Quién/Quien`, `Quiénes/Quienes`, `está/esta`, `están/estan`, `reunión/reunion`, and optional inverted punctuation as the same intent when deciding privacy vs navigation.

## Boundary

- Navigation: show, open, or locate the Participants panel/list.
- Identity disclosure: ask who is present, show/list participants, request names/roles, or identify host/moderator status.

The second category must stay answer-only even when the prompt also says panel or list.

## Acceptance Criteria

- Accented and unaccented Spanish identity prompts return participant privacy Q&A.
- Identity responses have `entrypoint_id is None`, `can_operate is False`, and no interrupt.
- Accented and unaccented Spanish panel/list navigation remains operable.
- `¿...?` punctuation does not change routing.
- Spanish answers remain localized and mention names, roles, private tabs, explicit request, and verified context.
- No YAML `questionAliases` are added for accent variants.
- Durable RingCentralVideo privacy docs explain the Spanish boundary.

## Prompt Examples

Safe navigation:

- `Muéstrame el panel de participantes`
- `Muestrame el panel de participantes`
- `¿Dónde está la lista de participantes?`
- `Donde esta la lista de participantes?`

Answer-only identity:

- `Muéstrame los participantes`
- `Lista los participantes`
- `¿Quién está en la reunión?`
- `¿Quiénes están en la reunión?`
- `¿Quiénes están en el panel de participantes?`
- `¿Quiénes están en la lista de participantes?`
- `Muéstrame el panel de participantes con nombres`
- `Muestrame la lista de participantes con roles`
- `¿Quién es host o moderador?`

## Non-Goals

- Do not read participant names, roles, host/moderator identity, or private tabs.
- Do not open the Participants panel for identity disclosure requests.
- Do not change voice-provider support or Spanish runtime readiness.
- Do not run live/manual acceptance using real participant data.
