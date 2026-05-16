# Cycle 116 Demand Analysis: Spanish RingCentral Video Safety Q&A Completion

Date: 2026-05-16
Scope: demand analysis only. This file is the only file edited by this handoff.

## Product Demand

The next best Cycle 116 slice should expand RingCentral Video usefulness for a new language without changing live automation risk. The strongest small move is to complete the Spanish report-only Q&A safety set for the existing RingCentral Video package.

Current local baselines from this demand cycle:

- `localization-report --language es`: `0/51` demo narration steps, `1/12` Q&A questions, `1/12` Q&A answers, and `questionAliases.es` on `1/27` entrypoints with `3` aliases.
- `localization-report --language zh --require-complete`: `51/51` demo steps, `12/12` Q&A questions, `12/12` Q&A answers.
- `localization-report --language ja --require-complete`: `51/51` demo steps, `12/12` Q&A questions, `12/12` Q&A answers.
- `voices`: runtime presenter languages are still English, Chinese, and Japanese. Runtime tones already include Professional, Conversational, Concise, Friendly, Coach, Formal, Support, and Careful.
- `doctor`: current package diagnostics pass with `11 ok`, `1 info`, `0 warnings`, and `0 failed`; the known info is the Q&A alias substring-risk summary.

Cycle 113 seeded Spanish with one background/privacy Q&A and three background aliases, but deliberately left Spanish out of runtime voice support and full demo narration. That was the right conservative opening. Cycle 116 should now make the Spanish safety layer meaningful across the whole Q&A surface before attempting Spanish demo narration or runtime voice support.

## Why This Beats The Other Slices

| Candidate | Value | Risk | Verdict |
| --- | --- | --- | --- |
| Complete Spanish Q&A safety coverage | Directly expands language coverage, deepens RingCentral Video support, and covers recurring privacy/support questions in a measurable way. | Low if kept package/report-only and tested through localization plus question routing. | Recommended. |
| Add another canonical tone | Tone expansion is already broad: `support` and `careful` cover troubleshooting and privacy. Another tone would mostly be presentation style. | Medium product ambiguity and low incremental RingCentral depth. | Defer until user asks for a named use case such as sales, executive, or training. |
| Runtime Spanish presenter language | More visible than package Q&A, but current Spanish package coverage is too thin and no local Spanish TTS route is validated. | Medium: provider validation, controller/CLI choices, docs, and voice readiness could imply demo readiness too early. | Defer until Spanish Q&A is complete and demo narration has a plan. |
| Diagnostics shared-index performance | Still useful because Cycle 114 implemented a different matcher optimization, leaving diagnostics-index reuse available. | Low, but mostly maintainer-facing after a recent performance cycle. | Defer behind user-facing language coverage. |
| Live RingCentral acceptance run | Important for confidence, especially Chat, Add coworkers, top-bar, and More routes. | Depends on current app availability and careful manual evidence capture. | Good future validation cycle, but less implementable as a small code/package slice. |
| New RingCentral feature entrypoints such as captions, whiteboard, or host controls | Deepens package support, but source/evidence docs flag observation, role, privacy, and locator gaps. | Medium to high unless kept explain-only and source-backed. | Defer until Spanish safety parity and current locator evidence are stronger. |

The Spanish Q&A slice also fits the user's recurring asks:

- Expand languages: moves Spanish from a tiny seed toward useful package coverage.
- Expand tone types: no new tone is needed because `support` and `careful` already cover the relevant support/privacy jobs.
- Improve UI/performance: avoids UI churn after recent controller/performance work; keeps the implementation narrow and fast to verify.
- Mine AiPresenter needs: uses the persistent memory themes of safe, complete RingCentral Video teaching, natural support answers, and privacy boundaries.
- Deepen RingCentral Video support: covers the existing 12 high-signal RingCentral Q&A items across privacy, invite, chat, participants, host controls, reactions, audio/video readiness, network quality, notes, captions/translation, post-meeting artifacts, and recording.

## Recommended One-Cycle Slice

Complete Spanish localized Q&A for RingCentral Video while keeping Spanish report-only.

Minimum package scope:

- Add `localizedQuestions.es` and `localizedAnswers.es` for the remaining 11 Q&A items in `packages/ringcentral-video.yaml`.
- Preserve the existing Spanish background/privacy seed.
- Keep UI labels such as `Chat`, `Participants`, `Share`, `Notes`, `Settings`, `Background`, `Recording`, and `Network quality` in English when they refer to current RingCentral UI labels.
- Use Spanish phrasing that is natural for support/training, but keep answers concise and safety-aligned with English, Chinese, and Japanese.
- Add only a very small number of Spanish aliases if required by question-routing tests. Prefer Q&A prompt coverage over broad `questionAliases.es` expansion in this cycle.

Runtime scope:

- Do not add Spanish to `PresenterLanguage`, `PRESENTER_LANGUAGE_CHOICES`, CLI choices, controller choices, or voice asset checks.
- `PresenterVoiceSettings(language="es")` should continue to reject Spanish until a later runtime-language cycle.
- Existing tones should work as style metadata for supported runtime languages only. Do not add a new tone.

Testing scope:

- Add or update package/CLI localization tests so Spanish reports `12/12` Q&A questions and `12/12` Q&A answers while still reporting `0/51` demo narration steps.
- Add targeted question-routing tests for Spanish safety prompts that should hit Q&A answers and remain non-operable.
- Keep existing Chinese and Japanese completeness tests green.
- Update package diagnostics count expectations deliberately if Spanish localized prompt candidates change the Q&A prompt count.

## Target Spanish Q&A Coverage

The future implementation should cover the remaining Spanish Q&A items:

- Can the presenter describe shared-screen content?
- How can I bring people into the meeting?
- Can the presenter read meeting messages or participant names?
- Where are host controls for participants?
- Can AiPresenter send a reaction or raise my hand safely?
- How do I make sure my audio and video are ready?
- How do I troubleshoot choppy audio or video?
- Where are notes and transcript controls?
- Where are captions, live transcription, and translation controls?
- Where can I find post-meeting recordings, transcripts, summaries, or insights?
- How do I handle meeting recording safely?

The Spanish answers should preserve these boundaries:

- Do not read meeting links, meeting IDs, dial-in details, host identities, names, emails, chat messages, participant roles, notes, transcripts, captions, shared-screen content, recordings, summaries, or insights by default.
- Do not promise that post-meeting artifacts exist.
- Do not start notes, transcription, captions, translation, recording, reactions, raise hand, invite sending, screen sharing, host controls, or leave/end actions.
- For location questions, explain the surface and state the boundary. Do not queue an interrupt for answer-only entrypoints.

## Acceptance Criteria

A future Cycle 116 implementation satisfies this demand when:

- `localization-report --package ringcentral-video --language es` reports:
  - `0/51` demo steps localized;
  - `12/12` Q&A questions localized;
  - `12/12` Q&A answers localized;
  - Spanish alias counts either remain the seed baseline or change only for explicitly chosen high-signal aliases.
- `localization-report --package ringcentral-video --language es --require-complete` still fails because Spanish demo narration is intentionally incomplete.
- `localization-report --package ringcentral-video --language zh --require-complete` and `--language ja --require-complete` still pass with `51/51` demo steps and `12/12` Q&A question/answer coverage.
- `ai-presenter voices` still lists English, Chinese, and Japanese only; Spanish is not presented as a runtime voice.
- `PresenterVoiceSettings(language="es")` still raises `Unsupported presenter language: es`.
- Spanish prompts for chat/participant privacy, recording, notes/transcript content, captions/translation, post-meeting artifacts, share content, invite links, host controls, reactions, audio/video readiness, and network quality route to the intended Q&A or safe entrypoint behavior.
- Sensitive Spanish Q&A prompts remain `can_operate=False` and produce no question interrupt step.
- Safe location-style prompts remain helpful and do not become destructive or content-reading actions.
- Doctor diagnostics still complete successfully; any changed Q&A prompt count is documented in tests and the implementation handoff.
- No production route policy, `questionPolicy`, `openSteps`, locator metadata, profile, provider routing, or live acceptance evidence changes are introduced.

## Non-Goals

- Do not translate the 51 demo narration steps into Spanish.
- Do not add Spanish runtime voice support, Spanish controller/CLI language choices, Spanish OpenAI/SAPI/Piper routing, or Spanish voice asset readiness checks.
- Do not add Korean, French, or another new language in the same cycle.
- Do not add new RingCentral Video entrypoints, flows, locators, state extraction, live acceptance evidence, or official-source docs.
- Do not broaden Spanish aliases across all 27 entrypoints unless a focused test proves a specific alias is needed.
- Do not add or remove canonical tones.
- Do not change tone behavior, route authorization, `can_operate`, Q&A-first matching, or interrupt-step creation.
- Do not edit README unless the implementation explicitly decides that report-only Spanish Q&A coverage needs one concise documentation note.
- Do not stage, delete, regenerate, or normalize `.coverage`; it is already dirty in the worktree.

## Likely Files For Future Implementation

Preferred implementation files:

- `packages/ringcentral-video.yaml`
  - Add Spanish localized Q&A questions and answers.
- `tests/unit/test_material_packages.py`
  - Assert Spanish Q&A coverage and package facts.
- `tests/unit/test_cli.py`
  - Assert Spanish localization report output and `--require-complete` failure.
- `tests/unit/test_questions.py`
  - Assert Spanish safety prompts route to non-operable Q&A behavior.

Likely unchanged:

- `src/ai_presenter/runtime/voice.py`
- `src/ai_presenter/runtime/controller.py`
- `src/ai_presenter/runtime/controller_view_model.py`
- `profiles/*`
- `docs/knowledge/*`
- README

If diagnostics counts change, update only the focused assertions that encode package-owned alias or Q&A prompt counts, with an implementation note explaining the intentional count movement.

## Verification Guidance

Recommended future verification:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py tests\unit\test_cli.py tests\unit\test_questions.py
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language es
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language es --require-complete
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language zh --require-complete
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ja --require-complete
.\.venv\Scripts\ai-presenter.exe voices
.\.venv\Scripts\ai-presenter.exe doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo
git diff --check
git status --short --untracked-files=all
```

No live RingCentral acceptance is required for this package-localization slice. It is package and routing coverage only.

## Lightweight Validation For This Handoff

Read-only checks run during this demand analysis:

```powershell
Test-Path docs\agent-handoffs\cycle-116-demand-analysis.md
.\.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language es
.\.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language zh --require-complete
.\.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language ja --require-complete
.\.venv\Scripts\ai-presenter voices
.\.venv\Scripts\ai-presenter doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo
git status --short
```

Observed results:

- The Cycle 116 handoff file did not exist before this edit.
- Spanish is currently a partial package seed: `0/51` demo steps, `1/12` Q&A questions, `1/12` Q&A answers, `1/27` entrypoints with `3` aliases.
- Chinese and Japanese completeness reports pass.
- Runtime voices list English, Chinese, and Japanese; tones include Support and Careful.
- Doctor passes with `11 ok`, `1 info`, `0 warnings`, `0 failed`.
- `.coverage` is modified and out of scope.

## Handoff Notes

The key discipline for Cycle 116 is to avoid turning a package-language improvement into a runtime-language promise. Spanish Q&A completion is valuable because it makes Spanish RingCentral Video safety answers real and measurable. Spanish demo narration, Spanish voice routing, and Spanish live acceptance should each get their own later slice.
