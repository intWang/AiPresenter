# Presenter Tone Behavior Matrix

Date: 2026-05-17
Scope: repo-wide AiPresenter runtime tone behavior.

## Purpose

This matrix records the current public presenter tone contract from
`src/ai_presenter/runtime/voice.py`. Use it when adding tone aliases,
extending language support, reviewing CLI voice output, or checking whether a
RingCentral Video change accidentally moved tone into routing policy.

Tone is style-only. It changes phrasing, voice instructions, and limited local
speech pacing. It must not change `entrypoint_id`, `can_operate`,
`questionPolicy`, Q&A-first matching, `create_question_interrupt_step(...)`,
package YAML, locators, demo flows, or live acceptance evidence.

## Canonical Tone Matrix

| Tone | Label | Aliases | Public voice instruction description | English dynamic rendering | Chinese dynamic rendering | Japanese and Spanish localized rendering | Chinese SAPI rate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `professional` | Professional | `professional`, `pro` | professional, structured, and product-specialist | Keeps source text unchanged. | Replaces known English UI terms; adds no tone prefix. | Keeps localized text unchanged. | `0` |
| `conversational` | Conversational | `conversational`, `conversation`, `casual` | natural, conversational, warm, and easy to follow | Adds `Sure.` before generated English text. | Adds `我来说明一下。` before dynamic Chinese text. | Keeps localized text unchanged. | `-1` |
| `concise` | Concise | `concise`, `brief` | concise, brisk, and transition-focused | Uses the first sentence only. | Replaces known English UI terms; keeps existing dynamic Chinese behavior without truncating generated fallback text. | Japanese and Spanish: only `concise` applies first-sentence shortening. | `1` |
| `friendly` | Friendly | `friendly`, `warm` | friendly, warm, reassuring, and approachable | Adds `Happy to help.` before generated English text. | Adds `可以的，我来说明一下。` before dynamic Chinese text. | Keeps localized text unchanged. | `-1` |
| `coach` | Coach | `coach`, `coaching`, `mentor` | coach-like, step-by-step, and encouraging | Adds `Let's walk through it.` before generated English text. | Adds `我们一步步来看。` before dynamic Chinese text. | Keeps localized text unchanged. | `0` |
| `formal` | Formal | `formal`, `structured` | formal, polished, and restrained | Adds `Certainly.` before generated English text. | Adds `请允许我说明。` before dynamic Chinese text. | Keeps localized text unchanged. | `0` |
| `executive` | Executive | `executive`, `briefing`, `boardroom` | executive, decision-oriented, polished, and outcome-focused | Adds `Executive brief.` before generated English text. | Adds `我简要说明关键点。` before dynamic Chinese text. | Keeps localized text unchanged. | `0` |
| `instructor` | Instructor | `instructor`, `trainer`, `training`, `teacher`, `tutorial` | instructional, clear, paced, and context-setting | Adds `Training note.` before generated English text. | Adds `我会用教学语气说明。` before dynamic Chinese text. | Keeps localized text unchanged. | `0` |
| `support` | Support | `support`, `supportive`, `helpdesk`, `troubleshooting`, `recovery`, `calm`, `steady`, `reassuring`, `empathetic` | calm, diagnostic, recovery-focused, and reassuring | Adds `Let's troubleshoot this.` before generated English text. | Replaces known English UI terms; adds no tone prefix. | Keeps localized text unchanged. | `-1` |
| `careful` | Careful | `careful`, `safety`, `safe`, `privacy`, `guarded`, `compliance` | careful, privacy-aware, concise, and boundary-focused | Adds `Safety note.` before generated English text. | Adds `我会谨慎说明。` before dynamic Chinese text. | Keeps localized text unchanged. | `0` |

## Localized Narration Contract

Localized package narration is already authored in the target language. For
Japanese and Spanish, the runtime does not add English prefixes for friendly,
coach, formal, executive, instructor, support, careful, conversational, or professional
tones. It only applies first-sentence shortening for `concise`.

Chinese dynamic text has a small deterministic replacement layer for common
English UI terms, then applies the tone prefix shown above when one exists.
Chinese localized narration uses the same localized-text path as other package
narration, so concise localized narration can still shorten to the first
sentence.

## Provider And Pacing Boundaries

Runtime voice validation remains separate from tone choice:

- Chinese output requires OpenAI speech or `windows-sapi-zh`.
- Japanese output requires OpenAI speech.
- Spanish output requires OpenAI speech; local SAPI/Piper Spanish remains out of
  scope unless a later provider slice changes and tests it.
- Chinese SAPI rate is `-1` for `conversational`, `friendly`, and `support`; `1`
  for `concise`; and `0` for all other tones.

## Safety And Routing Boundaries

`privacy`, `safety`, and `compliance` are aliases for `careful`; they are not
policy engines. `empathetic`, `calm`, and `reassuring` are aliases for
`support`; they are recovery/helpdesk style hints, not permission changes.
`briefing` and `boardroom` are aliases for `executive`; they are decision-style
hints, not meeting-control shortcuts.
`instructor`, `trainer`, `training`, `teacher`, and `tutorial` are aliases for `instructor`; they are onboarding and walkthrough style hints, not product tutorial routes or permission changes.

Tone must not:

- Change route selection, Q&A-first matching, or package alias matching.
- Change whether an entrypoint has `questionPolicy: answerOnly`.
- Change `entrypoint_id` or `can_operate`.
- Change whether `create_question_interrupt_step(...)` returns a step.
- Add package aliases, Q&A prompts, demo steps, locators, or acceptance claims.

For RingCentral Video safety details, use
`docs/knowledge/ringcentral-video/runtime-safety-routing.md`. This matrix is the
tone behavior catalog; the RingCentral note is the runtime safety routing and
privacy-boundary catalog.

## Maintenance Checklist

- When adding a canonical tone, update `PRESENTER_TONE_CHOICES`, aliases,
  descriptions, rendering tests, CLI voice output, and this matrix together.
- When adding an alias, decide whether it is only style language. If it could be
  read as a control, action, privacy policy, or meeting-state request, add route
  tests before accepting it.
- When adding a language, document localized narration behavior separately from
  provider compatibility.
- Before committing, run the focused voice and route tests plus the standard
  final gate for the cycle.
