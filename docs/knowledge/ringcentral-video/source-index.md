# RingCentral Video Source Index

Date: 2026-05-16

## Purpose

This index separates product-scope sources from executable automation evidence for the AiPresenter RingCentral Video package.

- Official RingCentral sources describe product surfaces and feature taxonomy.
- Repository-local sources describe what AiPresenter currently knows, tests, and may operate.
- Live manual observations are required before a locator or flow is treated as current-build evidence.

## Official RingCentral Sources

| Source | URL | Supports | Use In Package |
| --- | --- | --- | --- |
| RingCentral Video introduction | https://support.ringcentral.com/es/es/shared/content/app/intro-to-ringcentral-video-.html | Product framing: start, schedule, join, manage meetings, view recordings, chat, background, captions, security. | Scope future lifecycle, recordings, captions, and security coverage. |
| In-meeting controls index | https://support.ringcentral.com/au/en/video/in-meeting-controls.html | Attendee controls, host controls, virtual background, presentation mode, breakout rooms. | Coverage map for future entrypoints and QA. |
| Attendee controls | https://support.ringcentral.com/es/es/shared/content/app/using-ringcentral-video-attendee-controls-desktop-web.html | Meeting ID, network, mute/unmute, video, share, invite, participants, chat, More, Leave. | Compare against current toolbar package coverage. |
| Host controls side navigation | https://support.ringcentral.com/shared/sidenav/app/video/desktop-web/ringcentral-host-host-controls.html | Host/moderator topics: recording, participants, security, waiting room, moderator, mute others, turn off video. | Future host-control and permission-dependent coverage. |
| Meeting settings index | https://support.ringcentral.com/ca/en/video/meeting-settings.html | Managing meetings, recordings, settings, entry/exit tones, end-to-end encryption, audio settings, screen-share DND, advanced insights. | Future before/after meeting and settings coverage. |

## Repository-Local Sources

| Source | Role | Repository Signal |
| --- | --- | --- |
| `packages/ringcentral-video.yaml` | Main package knowledge | 27 entrypoints, 4 flows, 21 explainers, 12 QA items with Chinese and Japanese Q&A localization, manual controls, safety notes. |
| `profiles/ringcentral-video*.yaml` | Runtime profiles | Launch/bind paths and provider combinations for fake, OpenAI, Codex CLI, Piper, Windows SAPI paths. |
| `src/ai_presenter/adapters/ringcentral.py` | State extraction | Meeting joined, mic, camera, participant count, permission/waiting-room dialogs, connection warning. |
| `src/ai_presenter/runtime/package_demo.py` | Action execution | Supported actions and cleanup modes for package `openSteps`. |
| `src/ai_presenter/runtime/adaptive_demo.py` | Demo adaptation | Current participant-count adjustment for empty-room vs active meeting behavior. |
| `src/ai_presenter/runtime/questions.py` | Question matching | English token matching plus package-owned localized Q&A and `questionAliases`; Japanese Q&A now has localized no-match text, while legacy Python aliases remain as fallback. |
| `docs/runbooks/ringcentral-manual-acceptance.md` | Manual acceptance checklist | Procedure only; dated acceptance evidence must be recorded in `docs/knowledge/ringcentral-video/acceptance-runs.md`. |
| `docs/knowledge/ringcentral-video/evidence-index.md` | Evidence navigation | Cross-links package entrypoints, observation evidence, locator confidence, privacy policy, and next acceptance targets. |
| `docs/knowledge/ringcentral-video/runtime-safety-routing.md` | Runtime safety-routing guide | Consolidates recent Q&A-first, `answerOnly`, Notes/Transcript, recording, and tone-as-style-only rules with verification anchors. |
| `docs/knowledge/ringcentral-video/validation-checklist-index.md` | Manual validation procedure | Operator-ready checklist for turning evidence gaps into privacy-safe manual runs; proof still belongs in `acceptance-runs.md`. |
| `docs/agent-handoffs/cycle-000-ringcentral-knowledge.md` | Cycle 000 review | Identifies locator drift, state gaps, schema companion-doc need. |
| `docs/agent-handoffs/cycle-001-retro.md` | Cycle 001 lessons | Notes encoding/alias risks and recommends knowledge package hardening. |
| `tests/unit/test_material_packages.py` | Package validation | Validates package schema, references, explainers, QA, and localization coverage. |
| `tests/unit/test_ringcentral_profile.py` and `tests/integration/test_ringcentral_profile.py` | Profile/runtime behavior | Protects RingCentral adapter/profile assumptions with fakes and dry-run style paths. |

## Source Discipline

- A feature listed in official docs may be added to backlog or explain-only package knowledge.
- A feature should not become executable until it has a local observation record and a locator entry.
- Sensitive surfaces require privacy policy entries before they are exposed in demos or Q&A.
- Layout variants should be recorded as observations before changing YAML routes.

## Coverage Implications

Current package coverage is strongest for in-meeting attendee controls. The official sources indicate future coverage gaps:

- Before meeting: scheduling, joining, calendar connections, personal meeting ID.
- In meeting: closed captions, whiteboard, presentation mode, computer audio sharing, background noise, CPU/network detail.
- Host/moderator: recording, security, waiting room, participant management, mute others, turn off video, moderator assignment.
- After meeting: recordings, advanced insights, transcripts or summaries where available; current package has answer-only Q&A coverage but no executable post-meeting route.
- Localization: Japanese coverage is complete for the existing Q&A safety set, the four-step virtual background blur demo, the three-step meeting basics demo, all twenty-two steps of `meeting-controls-tour`, and all twenty-two steps of `meeting-control-map-demo`; `questionAliases.ja` now covers microphone, Participants, Chat, Network quality, View layout, audio menu, camera menu, Meeting information location, meeting overview basics, Reactions/Raise hand location discovery, Recording location discovery, and Notes/Transcript location discovery, while value-reading, copy-link, destructive, signal-sending, state-toggle, Notes/Transcript opening, and other higher-risk aliases remain future work.
- Meeting signals: Reactions and Raise hand now have answer-only safety Q&A; plain location questions should still route to their toolbar entrypoints.
- Question policy: sensitive but executable informational entrypoints can declare `questionPolicy: answerOnly`. RingCentral Video uses this for Meeting information and Notes/Transcript so question responses can identify the entrypoint without queuing interrupt steps or opening privacy-sensitive UI.
- Diagnostics: doctor now reports an INFO-level `qa alias substring risk` summary when package-owned aliases appear inside longer Q&A prompts, so future alias expansion can add runtime regressions before it becomes a privacy routing issue.
- Runtime safety routing: Notes/Transcript and recording action/content prompts should stay answer-only, `questionPolicy: answerOnly` protects Meeting information and Notes/Transcript from queued question interrupts, and presenter tone remains style-only. See `runtime-safety-routing.md` before changing question matching, aliases, Q&A safety copy, or tone behavior.
