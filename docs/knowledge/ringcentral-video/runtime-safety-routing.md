# RingCentral Video Runtime Safety Routing

Date: 2026-05-16

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

## Sensitive Surface Rules

### Notes And Transcript

Notes, transcript, captions, translation, summaries, and post-meeting artifacts are privacy-sensitive.

- Safe default: explain where the related panel or artifact surface is.
- Unsafe default: start notes or transcription, read or summarize transcript or notes content, copy, save, export, or promise artifact availability.
- Runtime guard: English, Japanese, and Chinese Notes/Transcript action or content prompts route to an answer-only safety Q&A when they are not location lookups.
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

## Tone Is Style-Only

Cycle 109 added canonical tone `careful`, with aliases including `privacy`, `safety`, `safe`, `guarded`, and `compliance`.

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

Cycle 110 added a route-parity regression matrix for sensitive RingCentral prompts across `professional`, `friendly`, `coach`, `support`, and the user-facing `privacy` alias. If a future tone changes routing, authorization, or interrupt creation, the test should fail.

## Localization And Counts

Runtime-only safety hardening should not change package counts. Treat count drift as a review trigger unless the cycle explicitly changes YAML.

Current expected package signals, verified on 2026-05-16 with `localization-report` and `doctor`:

- Operation entrypoints: 27.
- Package-owned aliases: 87.
- Q&A prompts: 71.
- Chinese aliases: 15/27 entrypoints, 49 aliases.
- Japanese aliases: 13/27 entrypoints, 34 aliases.
- Chinese and Japanese localization coverage: 51/51 demo steps, 12/12 Q&A questions, 12/12 Q&A answers.
- `doctor` may report one INFO-level Q&A alias substring risk summary; this is expected until the package design changes.

## Verification Commands

Use these commands after changing question routing, voice tone behavior, package aliases, or RingCentral Video Q&A policy:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests
.\.venv\Scripts\ruff check --no-cache .
.\.venv\Scripts\mypy --no-incremental src tests
.\.venv\Scripts\ai-presenter doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo
.\.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language zh --require-complete
.\.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language ja --require-complete
git diff --check
```

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

## Maintenance Checklist

- Before adding an alias, decide whether it is a control name or an action/content intent. Control names may belong in YAML; action/content intents usually belong in runtime safety matching or Q&A.
- Before making an entrypoint operable from questions, check `privacy-matrix.md`, `locator-matrix.md`, and `validation-checklist-index.md`.
- Before changing a safety answer, check localized Q&A coverage and avoid English prefixes in authored Chinese/Japanese answers.
- Before expanding tone behavior, run route-parity tests. Tone must remain style-only.
- Before promoting any live route evidence, record a dated acceptance run first.
