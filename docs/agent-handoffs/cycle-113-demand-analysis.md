# Cycle 113 Demand Analysis: Spanish RingCentral Video Language Wedge

Date: 2026-05-16
Scope: demand analysis only. This file is the only file edited by this handoff.

## Product Demand

AiPresenter already has a real multilingual foundation for RingCentral Video, but the current language set is still narrow: runtime voice choices are English, Chinese, and Japanese, while the RingCentral Video package has complete Chinese and Japanese localization for the existing demo/Q&A safety set. A small new-language wedge is useful now because it tests whether the localization model can grow beyond East Asian coverage without asking one cycle to translate the full package.

The highest-value next language is Spanish (`es`), not Korean (`ko`) or French (`fr`).

Why Spanish now:

- RingCentral's own source-index references already include Spanish-language support URLs, so Spanish is adjacent to the product-source trail already used by the package.
- Spanish is a high-demand business language for North America, LATAM, and distributed support/training teams, which fits RingCentral Video demos and enablement workflows.
- Spanish gives useful script and tokenization coverage without requiring a new writing system, making it a lower-risk first third language than Korean.
- French is also valuable, especially for Canada and EMEA, but Spanish likely reaches more RingCentral Video training and support users first.
- The current package has `es` coverage of `0/51` demo steps, `0/12` localized Q&A questions, `0/12` localized Q&A answers, and `0/27` entrypoints with aliases. That makes a thin first slice easy to measure.

Recommendation: add a Spanish safety-and-navigation wedge, not full Spanish demo narration.

## Target Users

- Spanish-speaking sales engineers, support specialists, and customer success staff who need RingCentral Video answers during a demo or training session.
- Operators who use the controller language selector and expect Spanish to be available for safe, common RingCentral Video questions.
- Reviewers who want proof that a new language can be added without weakening recording, meeting-link, transcript, chat, invite, share, or leave boundaries.
- Future localization agents who need a repeatable pattern before adding broader Spanish demo narration or additional languages.

The first Spanish slice should optimize for trust and routing correctness, not fluent coverage of every demo step.

## Recommended One-Cycle Slice

Add Spanish as a supported presenter language and localize only the RingCentral Video Q&A safety set plus a small set of high-signal entrypoint aliases.

Minimum package scope:

- Add `localizedQuestions.es` and `localizedAnswers.es` for the existing 12 RingCentral Video Q&A items.
- Add `questionAliases.es` for about 8 to 10 high-value entrypoints:
  - `ringcentral.video.top.meeting-info`
  - `ringcentral.video.top.network-quality`
  - `ringcentral.video.toolbar.microphone`
  - `ringcentral.video.toolbar.audio-menu`
  - `ringcentral.video.toolbar.camera`
  - `ringcentral.video.toolbar.share`
  - `ringcentral.video.toolbar.participants`
  - `ringcentral.video.toolbar.chat`
  - `ringcentral.video.more.recording`
  - `ringcentral.video.more.notes`
- Keep Spanish demo `localizedText` out of scope unless implementation finishes early and can add one very small smoke flow without disturbing counts. The preferred cycle stays Q&A/aliases only.

Runtime scope:

- Extend `PresenterLanguage` and language metadata in `src/ai_presenter/runtime/voice.py` from `en|zh|ja` to include `es`.
- Add aliases such as `es`, `es-es`, `es-mx`, `es-us`, `spanish`, and `espanol`.
- Let Spanish require the OpenAI speech provider for real voice output, matching Japanese's safe route. Do not route Spanish to local Piper or Windows SAPI unless a future cycle validates assets.
- Ensure generated dynamic fallback text can say "Speak in Spanish" and that package-authored Spanish Q&A answers are not prefixed with English style text.

Tests/docs scope:

- Add focused tests for language normalization, voice listing/doctor behavior, localization report counts, and Spanish Q&A routing.
- Update README/runbook examples only if the implementation changes user-facing CLI/controller language choices. Keep docs concise and count-specific.

## Acceptance Criteria

A future Cycle 113 implementation satisfies this demand when:

- `PresenterVoiceSettings(language="es")` normalizes successfully, and aliases such as `Spanish`, `es-MX`, and `espanol` map to canonical `es`.
- The controller/CLI voice choices include Spanish with the existing tone choices.
- `validate_profile_voice(...)` allows Spanish with `openai` and rejects unsupported local-only routes with a clear message.
- `localization-report --package ringcentral-video --language es` reports:
  - `0/51` demo steps localized, unless the implementation explicitly adds a tiny demo smoke slice;
  - `12/12` Q&A questions localized;
  - `12/12` Q&A answers localized;
  - a nonzero Spanish alias count covering the chosen high-value entrypoints.
- Spanish prompts for Meeting information, Notes/Transcript, Recording, Chat privacy, Participants privacy, Share, Invite, Leave, and Network quality route with the same safety posture as English:
  - sensitive controls remain `can_operate=False`;
  - answer-only entrypoints create no interrupt step;
  - safe Network quality remains operable if its existing entrypoint policy allows it.
- Existing Chinese and Japanese localization baselines remain unchanged: `51/51` demo steps and `12/12` Q&A question/answer coverage for both languages.
- Existing package counts and route behavior change only where Spanish data is intentionally added.
- Verification includes focused unit tests, Spanish localization report, existing Chinese/Japanese localization reports, doctor voice/profile checks, and `git diff --check`.

## Non-Goals

- Do not translate all 51 demo narration steps in this cycle.
- Do not add Spanish RingCentral Video locators, new entrypoints, new demo flows, or new manual acceptance evidence.
- Do not change production routing semantics except the minimum needed to recognize Spanish as a supported presenter language.
- Do not add Korean or French in the same cycle.
- Do not add local Spanish TTS asset discovery or Windows/Piper Spanish fallback until a voice-asset cycle validates it.
- Do not change tone types, safety policies, `questionPolicy`, or the careful/privacy tone parity rules.
- Do not promote any route to live accepted status based on localization or unit tests.
- Do not stage, delete, or normalize `.coverage`; it is already dirty.

## Safety Boundaries

Spanish must preserve the RingCentral Video safety model:

- Meeting information may be explained, but meeting IDs, links, dial-in details, account details, and host identity should not be read or copied by default.
- Notes/Transcript location questions may receive location help, but starting notes/transcription, reading transcripts, summarizing notes, copying/exporting artifacts, or creating minutes must stay answer-only or no-match.
- Recording prompts must not start, stop, inspect, summarize, or promise recording artifacts.
- Chat, Participants, Invite/Add coworkers, and Share answers must not invent or read private visible content.
- Leave/end meeting and host/moderator controls remain non-operable unless a future explicit confirmation workflow exists.
- Tone remains style-only. Spanish plus `careful`/`privacy` must not change route identity, authorization, or interrupt-step creation.

## Likely File Areas For Implementation

Implementation will likely touch these areas in a future cycle:

- `src/ai_presenter/runtime/voice.py` for `PresenterLanguage`, labels, aliases, voice instructions, and profile validation.
- `src/ai_presenter/runtime/voice_assets.py` only if the implementation needs explicit Spanish asset status messaging; prefer avoiding asset expansion this cycle.
- `src/ai_presenter/cli.py` and `src/ai_presenter/runtime/controller.py` only through existing `PRESENTER_LANGUAGE_CHOICES` consumers unless tests reveal hard-coded language assumptions.
- `packages/ringcentral-video.yaml` for `localizedQuestions.es`, `localizedAnswers.es`, and selected `questionAliases.es`.
- `tests/unit/test_voice.py`, `tests/unit/test_cli.py`, `tests/unit/test_controller.py`, `tests/unit/test_material_packages.py`, and `tests/unit/test_questions.py` for focused regression coverage.
- `README.md` or `docs/runbooks/ringcentral-manual-acceptance.md` only if Spanish becomes a documented operator path.

This demand-analysis cycle does not implement any of those changes.

## Docs And Test Expectations

Future implementation should document exact Spanish count baselines in the implementation handoff, because Spanish will intentionally be partial. Avoid describing Spanish as "complete" until demo narration also reaches the package's existing completeness bar.

Recommended verification set:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_voice.py tests\unit\test_cli.py tests\unit\test_controller.py tests\unit\test_material_packages.py tests\unit\test_questions.py
.\.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language es
.\.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language zh --require-complete
.\.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language ja --require-complete
.\.venv\Scripts\ai-presenter doctor --profile ringcentral-video-openai --package ringcentral-video --flow meeting-control-map-demo --language es --tone professional
git diff --check
```

If `ringcentral-video-openai` is not a valid installed profile name in the future implementation context, use the OpenAI-backed example/profile path already supported by that cycle. Do not use fake/Piper/Windows SAPI as proof of real Spanish speech readiness.

## Handoff Notes

- Spanish is the best first new-language wedge because it is useful, measurable, source-adjacent, and lower implementation risk than adding a new script family.
- Keep the slice deliberately small: language support plus Spanish Q&A safety coverage plus selected aliases.
- Treat Spanish Q&A safety as the product value. Full demo narration can be a later cycle after the language plumbing and safety routes are proven.
- Preserve the existing Chinese/Japanese complete-localization baselines and avoid accidental package count drift.
- `.coverage` was dirty before this handoff; do not stage it in the main session commit.
