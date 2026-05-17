# Cycle 181 Risk Scan: Localized Participant Privacy

Date: 2026-05-17

## Key Risks

1. **P1 - Localized identity prompts become operable.**
   CJK and Spanish prompts can contain short participant aliases inside a disclosure request. Runtime privacy matching must run before alias fallback.

2. **P1 - Panel/list wording can hide identity intent.**
   Prompts such as `Muestrame el panel de participantes con nombres` and `参加者一覧に誰がいますか` contain valid panel/list terms but still ask for identities. Identity terms must outrank panel/list exemptions.

3. **P2 - Chinese `谁在会议里` changes semantics.**
   It was previously a Participants alias. This cycle explicitly reclassifies it as identity disclosure because it asks who is in the meeting.

4. **P2 - Voice-provider tests can overreach.**
   Controller/session tests using the default `ringcentral-video-bind-speaker` profile cannot set Japanese or Spanish voice output. Keep ja/es coverage at question-routing level unless the test uses an OpenAI speech profile.

5. **P3 - Diagnostics drift.**
   YAML aliases are unchanged, so alias and localized Q&A counts should not change.

## Must Not Break

- Q&A/safety matching remains before package alias and entrypoint matching.
- `show participants panel`, `open participants panel`, and explicit localized panel/list location prompts remain operable.
- `show participants panel names` and localized panel/list-plus-names prompts remain answer-only.
- Host-control prompts such as mute all, remove, lock, unlock, and security settings stay answer-only.
- `.coverage` remains unstaged.

## Mitigations

- Add localized question-level tests for zh/ja/es identity prompts and safe panel prompts.
- Add controller/session regression for Chinese mixed-meta safe and sensitive participant prompts.
- Keep implementation limited to `src/ai_presenter/runtime/questions.py` constants.
