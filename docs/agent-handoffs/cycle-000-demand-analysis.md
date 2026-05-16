# Cycle 000 Demand Analysis

Date: 2026-05-16
Role: demand-analysis subagent
Write scope: this file only

## 1. Product Positioning And Implemented Capability

AiPresenter is a config-driven live software presenter for desktop app demos. The current MVP is optimized around RingCentral Video: it can launch or bind a meeting window, observe verified UI state, narrate concise presenter guidance, run scripted material-package demos, and let a human steer a demo through a small local controller.

The product is no longer only a CLI loop. It now has:

- Typer commands for `run`, `demo`, `controller`, `flows`, `entrypoints`, and `doctor`.
- YAML profiles for fake, OpenAI, Codex CLI, Piper, Windows SAPI English, and Windows SAPI Chinese/fallback speech paths.
- Presenter identity, durable coaching memory, and reusable skills loaded from Markdown.
- A RingCentral Video material package with 27 operation entrypoints, 4 demo flows, 21 explainers, 3 Q&A entries, and manual controls for `say`, `skip`, and `focus`.
- A synchronized timeline runner with `before`, `during`, and `after` narration placement, action offsets, deferred cleanup, pause/resume/end control, and manual directives.
- A Tk controller with Material package vs Running desktop app targets, running-window refresh/scan, Start/Pause/End, English/Chinese and tone selectors, text questions, and chat-style history.
- A temporary package generator for arbitrary visible desktop controls, with conservative safe/risky classification.
- Diagnostics for profile/package/flow/provider context, OpenAI env vars, explainer coverage, and RingCentral `DisableAffinityMask`.

The strongest current value proposition is: "A presenter can run a safe, narrated RingCentral Video feature tour and answer live questions without inventing private meeting content." The next product step should convert this working MVP into a more trustworthy controller-led demo tool.

## 2. User Goal Decomposition

### UI

Users need the controller to feel operationally clear while a demo is running. Current controls exist, but the UI is still sparse: no step timeline, no visible current/next step, no action safety marker, no scan result details, no provider readiness indicator, and limited error recovery guidance.

Observed user-facing goals:

- Choose prepared package or running app target with confidence.
- Understand what will happen before pressing Start or Submit.
- See whether a question caused text-only answer, safe demonstration, queued interrupt, or error.
- Know when the app is paused, ending, switching to an answer, or waiting for scan.
- Avoid accidental clicks on risky controls.

### Performance

The demo runtime captures live state before each package step in the RingCentral path. Because the profile observes screenshot, UI Automation, and metadata, the state adjuster may do more work than needed for decisions such as participant-count adaptation. The controller also scans visible controls synchronously. There is no latency budget or timing telemetry for capture, scan, TTS, playback, action execution, cleanup, or question match.

Observed user-facing goals:

- Keep narration/action timing tight.
- Avoid controller freezes during refresh/scan/start.
- Make slow provider or desktop automation failures visible.
- Know whether lag comes from TTS, capture, UI Automation, or action cleanup.

### Language Types

English is the default and preferred RingCentral Video tour language. Chinese output exists for `meeting-control-map-demo` via `localizedText.zh`, and Chinese speech can route to Windows SAPI Huihui from selected profiles. However, question matching is still English-centric: the matcher tokenizes only `[a-z0-9]+`, so Chinese user questions such as "聊天在哪里" will not match package entrypoints. Non-control-map flows and Q&A answers still fall back to English text replacement when Chinese localized text is absent.

Observed user-facing goals:

- English tours remain polished and natural.
- Chinese output should sound authored, not word-replaced.
- Chinese users should be able to type Chinese questions, not only English labels like `chat`.
- Unsupported language/provider combinations should fail before audio playback starts.

### Tone Types

Current tones are `professional`, `conversational`, and `concise`. They affect deterministic text rendering and Windows SAPI rate for Chinese. The implementation is intentionally modest: conversational English prepends "Sure.", concise picks the first sentence, and localized Chinese concise also picks the first sentence. OpenAI/Codex event narration does not yet receive active controller voice settings as a first-class prompt instruction for material scripts.

Observed user-facing goals:

- Professional: precise, product-specialist, safe.
- Conversational: warmer and less stiff without becoming verbose.
- Concise: faster, transition-focused, no repeated obvious explanation.
- Tone should not change safety decisions or factual content.

### Skills

`presenter/soul.md`, `presenter/memory.md`, `presenter/skills/app-director.md`, and `presenter/skills/live-explainer.md` define the product voice and demo behavior. They are loaded into OpenAI/Codex narration context. Scripted material flows and deterministic Q&A mostly bypass these skills except through pre-authored package text.

Observed user-facing goals:

- Demo structure should feel directed by feature neighborhoods, not button enumeration.
- Live answers should recover and return to the main thread.
- Blocking dialogs and privacy-sensitive surfaces should be handled as explicit boundaries.
- Skills should shape generated/adaptive content consistently, not only model-provider narration.

### RingCentralVideo Material Package

The package has a strong in-meeting control map: top bar status, meeting information, network quality, view layout, report issue, people controls, media controls, sharing, reactions, More, notes, background, settings, recording, and leave. It also encodes privacy constraints for meeting IDs, invite links, participant names, chat, shared screen, recording, notes, and leave/end behavior.

The earlier material-package spec named broader coverage areas that are not fully present yet: scheduling/joining beyond start, captions/live transcription, whiteboard, security/waiting room, host/moderator controls, breakout rooms, AI summaries/recaps, recent recordings, post-meeting artifacts, and CPU/connection detail beyond network quality.

Observed user-facing goals:

- Complete RingCentral Video tour coverage for the actual meeting build under test.
- Clearly separate executable, explain-only, risky, permission-dependent, and currently unverified controls.
- Keep package content maintainable as RingCentral UI changes.
- Expand Q&A beyond the current 3 entries so controller questions feel product-aware.

## 3. High-Value Requirement Candidates

| Priority | Candidate | User value | Main risk | Acceptance |
| --- | --- | --- | --- | --- |
| P0 | True resumable question interrupts | The spec promises that safe questions temporarily branch and then resume the active flow. Current controller implementation stops the current run and starts a single-step answer flow, so the original step position is not preserved. Fixing this makes live Q&A feel like an interruption, not a derailment. | Requires careful threading/state handling around `DemoControl`, `MaterialDemoRuntime`, and current target state. | While a flow is running, ask a safe question like `chat`; AiPresenter demonstrates the matched entrypoint, then continues with the next original flow step. Regression tests prove flow index is preserved and End still cancels pending/resume work. |
| P0 | First-class Chinese question input | Chinese output exists, but Chinese typed questions cannot match because question tokenization only recognizes Latin/digits. This blocks the Chinese controller experience. | Matching may become fuzzy enough to misroute controls unless aliases are curated. | With language set to Chinese, questions like `聊天在哪里`, `怎么邀请别人`, `怎么共享屏幕`, and `怎么离开会议` return the expected entrypoint or safe text-only answer. Risky matches remain non-operable. |
| P0 | Controller operational clarity pass | Users need to see what is running, what will happen next, whether a question is text-only or demonstrable, and why a control was not clicked. | UI changes may outgrow Tk if treated as a full redesign. | Controller shows current target, current/next step, last action, safety disposition, provider/language/tone readiness, and actionable errors. Existing manual acceptance path still fits on one screen and passes focused UI tests for pure formatting/state helpers. |
| P1 | Voice/provider readiness preflight | Language selectors can route Chinese to Windows SAPI Huihui or OpenAI, but the controller does not visibly preflight installed voices or Piper/OpenAI runtime readiness before Start. Users discover failures during the demo. | Windows voice detection may vary by machine. | `doctor` and controller status report whether selected profile/language/tone has an available speech provider/voice/model/env. Unsupported combinations block Start with a clear message. |
| P1 | Performance and timing telemetry | Narration quality depends on tight audio/action sync, but there are no measured budgets for capture, UIA scan, TTS synthesis, playback, action execution, or cleanup. | Instrumentation can add noise if every step logs too much. | Debug logs include per-step timing fields for capture, state adjustment, synth, playback, action, cleanup, and total step time. A focused test verifies timing records without real sleep/audio. |
| P1 | Lightweight RingCentral state capture for demo adjustment | The state adjuster captures all configured sources before every RingCentral package step, even when only participant count or simple UI state is needed. Reducing capture cost improves flow smoothness. | Must not weaken safety by relying on stale state. | State adjustment uses a minimal source set or cached observation where appropriate. Tests show participant-count adaptation still works; logs show fewer screenshots or reduced capture time during scripted demos. |
| P1 | Package-level safety metadata | Safety is currently inferred from words in entrypoint id/title/purpose and duplicated between question handling and temporary package generation. Explicit metadata would make risky/explain-only behavior auditable. | YAML schema change touches package validation and existing tests. | Entrypoints can declare safety such as `safeToOperate`, `requiresConfirmation`, `privacySensitive`, or `permissionDependent`. Question handling uses metadata before lexical fallback. Existing risky controls remain non-operable. |
| P1 | RingCentral package coverage expansion | The package is strong for the current meeting toolbar but thinner than the earlier broad RCV spec. Expanding coverage makes Q&A and tours feel more product-complete. | Needs real UI verification; adding non-executable knowledge can overclaim capability. | Add verified or explicitly explain-only entries/Q&A for captions/transcript, whiteboard, host/security controls, post-meeting artifacts, scheduling/joining, and AI notes/summaries. Package tests assert coverage and privacy notes. |
| P1 | Native Chinese package content beyond control map | Only `meeting-control-map-demo` has authored Chinese scripts. Other flows and Q&A still degrade to substitutions. | User memory says English should remain default; Chinese work should not distract from English tour quality. | All shipped RCV demo flows and high-frequency Q&A have `localizedText.zh` or localized answer fields. Chinese concise/conversational variants remain natural and do not add stiff prefixes. |
| P2 | Curated alias and semantic question matching | Current matching handles exact/fuzzy English tokens but has limited synonym/intent support. Users will ask "Where do I see who's here?" rather than "participants". | A model-based matcher could add nondeterminism and safety risk. | Add deterministic aliases per entrypoint/explainer, including English and Chinese synonyms. Tests cover common paraphrases and ensure risky aliases do not operate. |
| P2 | Skill-aware scripted response generation | Skills shape model-provider event narration, but deterministic Q&A and package scripts do not dynamically consult skills. A light bridge would make answers feel more like the configured presenter. | Could blur deterministic safety guarantees if skills are applied through an LLM without constraints. | A deterministic renderer or constrained provider prompt includes selected skill/tone guidance while preserving exact package facts and safety metadata. Golden tests cover professional/conversational/concise output. |
| P2 | Material package authoring and validation aid | As packages grow, hand-editing YAML becomes error-prone. A local validation/coverage report would help future agents and users maintain app packages. | Tooling can become a side project unless scoped to validation/reporting. | Add a command or doctor section that reports entrypoints without QA, explainers, safety metadata, localized text, executable steps, and verification status. No business runtime behavior changes. |

## 4. Confirmation Needed Vs Low-Risk Direct Design

Needs user confirmation before design:

- Whether the next cycle should prioritize controller UI, multilingual Q&A, RingCentral knowledge expansion, or performance instrumentation.
- Whether Chinese should be a first-class input language now, or only a supported output mode for authored demos.
- Whether risky controls should ever become operable after confirmation, or remain explain-only for this product phase.
- Whether RingCentral package expansion should include unverified explain-only product knowledge, or only controls observed in the local build.
- Whether future controller UI should remain Tk for speed or move toward a richer GUI/web surface.
- Whether OpenAI TTS should be treated as the premium tone path, with Piper/SAPI as local smoke paths.

Can go directly into low-risk engineering design:

- Add regression tests and design for resumable question interrupts, because current behavior diverges from the written controller spec.
- Add Chinese question matching aliases/tokenization while preserving existing English tests and risky-action blocks.
- Add provider/language readiness checks to `doctor` and controller status.
- Add timing telemetry behind debug logging.
- Add package coverage reporting for localized text, Q&A, explainers, and safety notes.
- Reduce RingCentral demo state capture to the minimum source set needed for adaptive decisions, with fallback to current full capture.

## 5. Recommendations To Main Session

Recommended next cycle theme: "make the controller trustworthy during live interruption." The best P0 bundle is:

1. True resumable question interrupts.
2. First-class Chinese question input for the existing RCV package.
3. Controller operational clarity for status, current/next step, safety, and provider readiness.

This bundle is coherent because it improves the user's live control loop rather than adding unrelated product breadth. It also gives technical scan and test review agents clear handoff points: controller state architecture, interrupt runtime tests, matcher coverage, and manual acceptance.

Suggested sequencing:

1. Ask user to confirm whether controller trust/usability is the next implementation theme.
2. If yes, write a focused design spec for resumable interrupts plus controller status visibility.
3. Keep RingCentral package expansion as the next P1 content cycle, because it benefits from a stronger controller and coverage report first.
4. Treat performance telemetry as a parallel low-risk engineering track if technical scan finds the capture path is noisy or slow.
5. Preserve the current safety posture: privacy-sensitive and destructive controls remain explain-only unless the user explicitly approves a future confirmation workflow.

