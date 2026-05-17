# RingCentral Video Runtime Safety Routing

Date: 2026-05-17

## Purpose

This note captures the repo-local routing rules that keep AiPresenter safe when it answers RingCentral Video questions. It is a maintenance guide for future agents and reviewers. It does not replace the package YAML, privacy matrix, locator matrix, or dated acceptance evidence.

The core invariant is simple: question routing may identify a useful control or Q&A answer, but operation permission is decided separately. Tone and language may change phrasing, not safety.

## Current Runtime Anchors

| Area | Source | Maintainer Rule |
| --- | --- | --- |
| Package content | `packages/ringcentral-video.yaml` | Package aliases describe discoverable controls. Do not add action, content-reading, copying, export, or summary requests as aliases by default. |
| Question matching | `src/ai_presenter/runtime/questions.py` | Match Q&A first, then entrypoint aliases/tokens. Safety Q&A should win over broad entrypoint fallback when a prompt asks for private content or meeting-state changes. |
| Operation permission | `_can_operate(...)` in `runtime.questions` | `entrypoint_id` is not permission. `questionPolicy: answerOnly`, missing `openSteps`, and risky entrypoint wording keep `can_operate=False`. |
| Interrupt creation | `create_question_interrupt_step(...)` in `runtime.session` | A question can queue a demo only when `entrypoint_id` is present and `can_operate=True`. |
| Tone rendering | `src/ai_presenter/runtime/voice.py` | Tone applies after route and eligibility are decided. `careful` and aliases such as `privacy` are style hints, not policy engines. |
| Package diagnostics | `runtime.diagnostics` and CLI `doctor` | Alias duplicate, Q&A duplicate, alias overlap, and alias substring signals are regression tripwires for future package growth. |

## Question Normalization Boundary

Runtime question matching and diagnostics share the package-level
`normalize_question_prompt()` match key.

- Q&A exact prompts, Q&A fragments, package-owned aliases, token fallback, legacy
  aliases, and diagnostics all use the same normalized key.
- Latin diacritics are folded for Latin base characters, so Spanish prompts can
  match with or without accents: `menú de cámara` and `menu de camara` have the
  same match key.
- The normalizer uses canonical decomposition, not compatibility decomposition.
  Do not rely on it to fold halfwidth Japanese, fullwidth Latin, ligatures,
  transliterations, variants, stemming, or semantic intent.
- Q&A-first precedence still comes before entrypoint alias routing. A safety Q&A
  can block an otherwise matching Spanish, Chinese, Japanese, or English alias.

## Sensitive Surface Rules

### Notes And Transcript

Notes, transcript, captions, translation, summaries, and post-meeting artifacts are privacy-sensitive.

- Safe default: explain where the related panel or artifact surface is.
- Unsafe default: start notes or transcription, read or summarize transcript or notes content, copy, save, export, or promise artifact availability.
- Runtime guard: English, Japanese, and Chinese Notes/Transcript action or content prompts route to an answer-only safety Q&A when they are not location lookups. Authored Spanish safety Q&A prompts still win through Q&A-first matching, including unaccented variants, but broad Spanish action-term expansion is a separate future slice.
- Location guard: location-style prompts must remain helpful. They may identify the Notes/Transcript surface, but still must not queue an interrupt when the entrypoint is `answerOnly`.

### Recording

Recording changes meeting state and may require host role, meeting policy, and participant consent.

- Safe default: explain the recording surface and consent boundary.
- Unsafe default: start, stop, download, play back, summarize, or inspect recording content.
- Runtime guard: recording safety prompts stay answer-only. `ringcentral.video.more.recording` remains non-operable from questions.

### Meeting Information

Meeting information may include IDs, links, dial-in details, host identity, and account or encryption details.

- Safe default: explain where meeting details live and why they matter.
- Unsafe default: read, copy, or submit exact values without explicit user request and verified visible context.
- Package guard: Meeting information uses `questionPolicy: answerOnly`, so question answers can name the surface without queuing a click.

### Chat, Participants, Invite, Share

These controls are common demo targets, but their contents are private or meeting-impacting.

- Chat: do not read messages by default.
- Participants: do not read names, roles, or host-control states by default.
- Invite/Add coworkers: do not read invite links, suggestions, names, emails, or send invitations by default.
- Share: do not click final Share or describe shared content without explicit confirmation and verified context.

### Leave, End, Host, Security

Leave/end and host/security controls are high-impact or role-gated.

- Safe default: explain the control purpose and location.
- Unsafe default: click Leave/End, lock/unlock, admit/remove people, mute others, or change permissions without a separate confirmation workflow.

## Private Surface Examples

These examples document existing routing boundaries only. They do not add product aliases, change package Q&A, promote live evidence, or make any route accepted for unattended operation.

| Surface | Safe Location Prompt | Private Content Or Action Prompt | Expected Runtime Result | Why |
| --- | --- | --- | --- | --- |
| Chat | `open chat`, `where is chat` | `Read chat aloud`, `Summarize the chat`, `What did John say in chat?` | Location prompts may route to `ringcentral.video.toolbar.chat`; content prompts stay answer-only with no interrupt. | Chat can contain public and private messages. |
| Meeting information | `meeting information`, `where is meeting information?` | `Read meeting information aloud`, `Copy meeting link`, `Share meeting details` | Prompts may identify `ringcentral.video.top.meeting-info`, but `questionPolicy: answerOnly` keeps `can_operate=False`. | Meeting details can include IDs, links, dial-in, host, and encryption values. |
| Recording | `recording`, `where is Start recording?` | `Start recording`, `Stop recording`, `Are we recording?` | Prompts may identify `ringcentral.video.more.recording`, but the route remains non-operable and creates no interrupt. | Recording changes meeting state and may require role, policy, and consent checks. |
| Notes and Transcript | `where are Notes and Transcript?` | `Start meeting notes`, `Read the transcript`, `Summarize the transcript` | Location prompts may identify `ringcentral.video.more.notes`; `questionPolicy: answerOnly` and Q&A guards prevent interrupts for notes/transcript actions or content. | Notes/transcript surfaces can expose meeting content and recording-adjacent controls. |

## Tone Is Style-Only

Cycle 109 added canonical tone `careful`, with aliases including `privacy`, `safety`, `safe`, `guarded`, and `compliance`. Cycle 195 added canonical tone `executive`, with aliases including `briefing` and `boardroom`. Cycle 207 added canonical tone `instructor`, with aliases including `trainer`, `training`, `teacher`, and `tutorial`; it is phrasing only and does not create product tutorial routes or meeting-control permission.
For the full repo-wide tone catalog, use `docs/knowledge/presenter-tone-behavior-matrix.md`.

Tone may:

- Change English generated prefixes such as `Safety note.`
- Change Chinese generated prefixes for dynamic text.
- Change voice instruction text, labels, and speech pacing.

Tone must not:

- Change `entrypoint_id`.
- Change `can_operate`.
- Change `questionPolicy`.
- Change Q&A-first matching.
- Change whether `create_question_interrupt_step(...)` returns a step.
- Add or remove package aliases, Q&A, demo flow steps, or locator routes.

Cycle 110 added a route-parity regression matrix for sensitive RingCentral prompts across `professional`, `friendly`, `coach`, `executive`, `instructor`, `support`, and the user-facing `tutorial` and `privacy` aliases. If a future tone changes routing, authorization, or interrupt creation, the test should fail.

## Presenter Meta Requests Are Runtime Answer-Only

Presenter expression requests are runtime answer-only guards, not RingCentralVideo package aliases or Q&A. These prompts ask AiPresenter to change how it answers, such as language, tone, pacing, detail, guidance depth, or user familiarity; they are not RingCentral Video control requests.

The runtime handles high-confidence Presenter meta phrases in `src/ai_presenter/runtime/questions.py`. Q&A safety matching still runs first, and contained authored Q&A must still win before package aliases when a style prefix is added to a sensitive RingCentral prompt. Pure meta requests are answer-only: they should not produce a RingCentralVideo entrypoint, operation permission, or `create_question_interrupt_step(...)`.

Mixed prompts can still preserve explicit RingCentralVideo intent through authored Q&A, package aliases, meeting-info location lookup, or entrypoint titles. Broad entrypoint token fallback is skipped while Presenter meta matching is active.

Do not claim persistent language or tone state changes from this guard. It does not persist language, tone, pacing, detail, or guidance-depth settings unless a separate controller or session state slice implements and tests that behavior.

Do not add Presenter meta phrases to `packages/ringcentral-video.yaml` as aliases, Q&A, localized titles, or package facts. The package owns RingCentral Video surfaces and product knowledge; the runtime guard owns Presenter expression requests. YAML, localization, and package-count drift are regressions unless a separate package slice explicitly owns them.

Keep fragments phrase-level, especially for Chinese and other CJK prompts. Bare safety, privacy, status, language, tone, or pacing words can steal meeting-info, encryption, host-control, notes/transcript, recording, chat, participants, share, invite, leave, or full-screen routes. Mojibake text should remain unsupported rather than becoming a valid Presenter meta request or RingCentral Video alias.

Repo tests prove local routing boundaries only. They are not live RingCentral acceptance evidence.

## Localization And Counts

Runtime-only safety hardening should not change package counts. Treat count drift as a review trigger unless the cycle explicitly changes YAML.

Current expected package signals as of 2026-05-17:

- Operation entrypoints: 27.
- Demo flows: 4, with 51 total demo steps.
- Explainers: 21, covering 27/27 entrypoints.
- Q&A items: 16.
- 224 Q&A question prompts.
- 171 package-owned aliases.
- Answer-only question-policy entrypoints: 2 (`ringcentral.video.top.meeting-info`, `ringcentral.video.more.notes`).
- English aliases: 4/27 entrypoints, 17 aliases.
- Chinese aliases: 15/27 entrypoints, 49 aliases.
- Japanese aliases: 13/27 entrypoints, 34 aliases.
- Spanish aliases: 26/27 entrypoints, 69 aliases.
- French package seed: `meeting-basics-demo` has 3/3 French narration
  strings, `vbg-blur-demo` has 4/4 French narration strings, background
  privacy, recording safety, and leaving/ending safety Q&A have French
  question/answer text, and French aliases cover 1/27 entrypoints with 2
  aliases. French remains package-only and is not runtime `--language fr` support.
- Chinese, Japanese, and Spanish required package localization coverage: 51/51 demo steps, 16/16 Q&A questions, 16/16 Q&A answers.
- Spanish is runtime-selectable only with OpenAI-backed speech. Its localization
  is complete, but local SAPI/Piper routes and live RingCentral acceptance are
  still out of scope.
- `doctor` reports one OK-level answer-only question-policy summary covering
  2 entrypoints and may report one INFO-level Q&A alias substring risk summary
  covering 11 prompts; this is expected until the package design changes.

## Verification Commands

Use these commands after changing question routing, voice tone behavior, package aliases, or RingCentral Video Q&A policy:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests
.\.venv\Scripts\ruff check --no-cache .
.\.venv\Scripts\mypy --no-incremental src tests
.\.venv\Scripts\ai-presenter doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo
.\.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language zh --require-complete
.\.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language ja --require-complete
.\.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language es --require-complete
git diff --check
```

For Spanish runtime checks, keep the provider boundary explicit:

```powershell
.\.venv\Scripts\ai-presenter doctor --profile profiles/ringcentral-video-openai.example.yaml --package ringcentral-video --flow meeting-control-map-demo --language es --require-localization
.\.venv\Scripts\ai-presenter demo --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo --language es --dry-run
```

Expected result: Spanish package localization and runtime language support are
OK on the OpenAI route, while local profiles still reject Spanish before runtime
with a profile voice compatibility error.

Focused sentinels:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py::test_ringcentral_sensitive_prompt_routing_is_tone_invariant
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py::test_ringcentral_chinese_notes_action_requests_stay_answer_only tests\unit\test_questions.py::test_ringcentral_chinese_transcript_content_requests_stay_answer_only tests\unit\test_questions.py::test_ringcentral_chinese_notes_location_routes_still_match_notes
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_voice.py tests\unit\test_cli.py::test_voices_lists_language_tone_choices tests\unit\test_controller.py::test_render_voice_label_uses_controller_labels
```

## Recent Cycle Anchors

| Cycle | Commit | What It Locked Down |
| --- | --- | --- |
| 104 | `394fba0` | Japanese recording safety and location handling stayed non-operable from questions. |
| 105 | `adcc876` | `questionPolicy: answerOnly` separated question answers from queued operation for sensitive entrypoints. |
| 106 | `146c51a` | Japanese Notes/Transcript location aliases were added while preserving answer-only behavior. |
| 107 | `64d7f31` | English and Japanese Notes/Transcript action/content prompts route to safety Q&A while location prompts remain useful. |
| 108 | `1a0d358` | Chinese Notes/Transcript action and content prompts route to safety Q&A while location prompts remain useful. |
| 109 | `35a34dd` | `careful` tone and privacy/safety aliases are rendering hints only. |
| 110 | `f45ea46` | Sensitive RingCentral prompt routing is invariant across selected tones. |
| 124 | `346fd0c` | Spanish package localization became complete across demo narration and Q&A while runtime Spanish stayed unsupported. |
| 125 | `9e2ac26` | Spanish package-owned aliases expanded to 26/27 entrypoints with Q&A-first precedence preserved. |
| 126 | `6177d10` | Latin diacritic folding made Spanish aliases and Q&A prompts accent-insensitive without compatibility-folding Japanese width forms. |

## Maintenance Checklist

- Before adding an alias, decide whether it is a control name or an action/content intent. Control names may belong in YAML; action/content intents usually belong in runtime safety matching or Q&A.
- Before making an entrypoint operable from questions, check `privacy-matrix.md`, `locator-matrix.md`, and `validation-checklist-index.md`.
- Before changing a safety answer, check localized Q&A coverage and avoid English prefixes in authored Chinese/Japanese answers.
- Before expanding tone behavior, run route-parity tests. Tone must remain style-only.
- Before documenting Presenter meta routing, verify the wording says answer-only/no-interrupt, does not claim persistent voice-state mutation, keeps package YAML ownership separate, and does not promote repo tests to live RingCentral evidence.
- Before promoting any live route evidence, record a dated acceptance run first.
