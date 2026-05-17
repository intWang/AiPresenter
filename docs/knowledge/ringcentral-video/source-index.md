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
| `packages/ringcentral-video.yaml` | Main package knowledge | 27 entrypoints, 4 flows, 51 demo steps, 21 explainers, 16 Q&A items, 222 Q&A question prompts, 171 package-owned aliases, complete Spanish/Chinese/Japanese required package localization, French package-local seed coverage, Spanish optional entrypoint display metadata on 8/27 titles and 8/27 purposes, manual controls, safety notes. |
| `profiles/ringcentral-video*.yaml` | Runtime profiles | Launch/bind paths and provider combinations for fake, OpenAI, Codex CLI, Piper, Windows SAPI paths. |
| `src/ai_presenter/adapters/ringcentral.py` | State extraction | Meeting joined, mic, camera, participant count, permission/waiting-room dialogs, connection warning. |
| `src/ai_presenter/runtime/package_demo.py` | Action execution | Supported actions and cleanup modes for package `openSteps`. |
| `src/ai_presenter/runtime/adaptive_demo.py` | Demo adaptation | Current participant-count adjustment for empty-room vs active meeting behavior. |
| `src/ai_presenter/runtime/questions.py` | Question matching | Q&A-first matching, then package-owned localized `questionAliases`, legacy aliases, and token scoring; shared Latin-diacritic-insensitive normalization supports Spanish unaccented prompts. Spanish aliases are package-owned query metadata; runtime Spanish output is profile/provider gated separately. |
| `docs/runbooks/ringcentral-manual-acceptance.md` | Manual acceptance checklist | Procedure only; dated acceptance evidence must be recorded in `docs/knowledge/ringcentral-video/acceptance-runs.md`. |
| `docs/knowledge/ringcentral-video/observation-log.md` | Observation log | Append-only live and repo-derived observations by date, build, locale, meeting state, and source. |
| `docs/knowledge/ringcentral-video/locator-matrix.md` | Locator evidence | Entrypoint locator strategy, confidence, cleanup mode, and current validation gaps. |
| `docs/knowledge/ringcentral-video/state-matrix.md` | State coverage | RingCentral Video meeting states, adapter signals, package behavior, and missing-state backlog. |
| `docs/knowledge/ringcentral-video/privacy-matrix.md` | Privacy and safety policy | Sensitive surfaces, allowed summaries, disallowed readings, and confirmation boundaries. |
| `docs/knowledge/ringcentral-video/evidence-index.md` | Evidence navigation | Cross-links package entrypoints, observation evidence, locator confidence, privacy policy, and next acceptance targets. |
| `docs/knowledge/ringcentral-video/runtime-safety-routing.md` | Runtime safety-routing guide | Consolidates recent Q&A-first, `answerOnly`, Notes/Transcript, recording, tone-as-style-only rules, and private-surface examples for chat, meeting information, recording, and notes/transcript with verification anchors. |
| `docs/knowledge/ringcentral-video/validation-checklist-index.md` | Manual validation procedure | Operator-ready checklist for turning evidence gaps into privacy-safe manual runs; proof still belongs in `acceptance-runs.md`. |
| `docs/agent-handoffs/cycle-000-ringcentral-knowledge.md` | Cycle 000 review | Identifies locator drift, state gaps, schema companion-doc need. |
| `docs/agent-handoffs/cycle-001-retro.md` | Cycle 001 lessons | Notes encoding/alias risks and recommends knowledge package hardening. |
| `tests/unit/test_material_packages.py` | Package validation | Validates package schema, references, explainers, QA, and localization coverage. |
| `tests/unit/test_runtime_factory.py`, `tests/unit/test_profile_runner.py`, and `tests/integration/test_ringcentral_profile.py` | Profile/runtime behavior | Protect provider registry, profile runner, RingCentral adapter, and dry-run/material-demo runtime assumptions with fakes and repository-local adapter fixtures. |

## Source Discipline

- A feature listed in official docs may be added to backlog or explain-only package knowledge.
- A feature should not become executable until it has a local observation record and a locator entry; executable live confidence also needs privacy, side-effect, cleanup, and dated acceptance evidence.
- Sensitive surfaces require privacy policy entries before they are exposed in demos or Q&A.
- Layout variants should be recorded as observations before changing YAML routes.
- `validation-targets --acceptance-runs` is a guard input, not an evidence-generation command.

## Coverage Implications

Current package coverage is strongest for in-meeting attendee controls. The official sources indicate future coverage gaps:

- Before meeting: scheduling, joining, calendar connections, personal meeting ID.
- In meeting: closed captions, whiteboard, presentation mode, computer audio sharing, background noise, CPU/network detail.
- Host/moderator: recording, security, waiting room, participant management, mute others, turn off video, moderator assignment.
- After meeting: recordings, advanced insights, transcripts or summaries where available; current package has answer-only Q&A coverage but no executable post-meeting route.
- Localization: Chinese, Japanese, and Spanish package localization is complete for the existing Q&A safety set, the four-step virtual background blur demo, the three-step meeting basics demo, all twenty-two steps of `meeting-controls-tour`, and all twenty-two steps of `meeting-control-map-demo`. `questionAliases.en` covers 4/27 entrypoints with 17 aliases, `questionAliases.zh` covers 15/27 entrypoints with 49 aliases, `questionAliases.ja` covers 13/27 entrypoints with 34 aliases, `questionAliases.es` covers 26/27 entrypoints with 69 aliases, and `questionAliases.fr` covers 1/27 entrypoints with 2 aliases. French package-local seed coverage is 7/51 demo steps, covering `meeting-basics-demo` and `vbg-blur-demo`, plus 1/16 Q&A questions and answers; French remains package-only and is not runtime `--language fr` support. Spanish optional entrypoint display metadata covers `localizedTitles.es` on 8/27 entrypoints and `localizedPurposes.es` on 8/27 entrypoints. Spanish is runtime-selectable only with OpenAI-backed speech; local SAPI/Piper routes and live RingCentral acceptance remain future work.
- Query normalization: package-owned aliases and Q&A prompts share the same match key used by diagnostics. Latin diacritics are folded for Latin base characters, so Spanish accented and unaccented prompts can match the same package knowledge. The normalizer does not intentionally width-fold Japanese or perform transliteration, stemming, or semantic matching.
- Meeting signals: Reactions and Raise hand now have answer-only safety Q&A; plain location questions should still route to their toolbar entrypoints.
- Question policy: sensitive but executable informational entrypoints can declare `questionPolicy: answerOnly`. RingCentral Video uses this for Meeting information and Notes/Transcript so question responses can identify the entrypoint without queuing interrupt steps or opening privacy-sensitive UI.
- Diagnostics: doctor reports `question policy` counts for answer-only entrypoints, and reports an INFO-level `qa alias substring risk` summary when package-owned aliases appear inside longer Q&A prompts, so future alias expansion can add runtime regressions before it becomes a privacy routing issue.
- Runtime safety routing: Notes/Transcript and recording action/content prompts should stay answer-only, `questionPolicy: answerOnly` protects Meeting information and Notes/Transcript from queued question interrupts, and presenter tone remains style-only. See `runtime-safety-routing.md` before changing question matching, aliases, Q&A safety copy, or tone behavior.
