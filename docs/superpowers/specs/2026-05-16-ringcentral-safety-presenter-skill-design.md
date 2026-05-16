# RingCentral Safety Presenter Skill Design

Date: 2026-05-16

## Goal

Add a RingCentral-specific presenter skill that teaches model-backed narration to keep privacy, side effects, evidence, and cleanup boundaries visible during RingCentral Video demos.

## Context

RingCentral Video knowledge already exists in `docs/knowledge/ringcentral-video/privacy-matrix.md`, `validation-checklist-index.md`, `evidence-index.md`, and `packages/ringcentral-video.yaml`. The presenter context currently loads only two general skills: `app-director` and `live-explainer`. Those skills contain broad guidance such as explain-only handling for private or destructive controls, but they do not encode the concrete RingCentral surfaces that repeatedly matter during demos: chat, participants, invite links, meeting information, recording, leave/end, notes/transcripts, shared-screen content, settings, background, and accepted evidence levels.

This slice turns that scattered knowledge into a concise, loadable skill without changing any route execution policy.

## Design

Create `ringcentral-safety.md` in both presenter skill locations:

- `presenter/skills/ringcentral-safety.md`
- `src/ai_presenter/presenter/skills/ringcentral-safety.md`

The two files must have identical content because repo-root profiles support local development while `src/ai_presenter` files are packaged by `pyproject.toml`.

Add the new skill after `live-explainer.md` in all RingCentral profile `skillPaths`. The order should stay:

1. `app-director`
2. `live-explainer`
3. `ringcentral-safety`

The skill content should be short enough for provider prompts, but specific enough to guide narration:

- explain controls and visible UI structure by default;
- do not read private values such as meeting IDs, invite links, names, emails, chat messages, notes, transcript content, room imagery, account data, or report contents unless explicitly asked and verified;
- keep recording, leave/end, host/security, final share, invite sending, notes/transcript start, and persistent settings changes explain-only unless the user gives explicit instruction and a safe workflow exists;
- distinguish repo-tested, observed, accepted, backlog, and blocked evidence language;
- name cleanup expectations for modals, menus, panels, settings, raise hand, and reaction surfaces;
- recover safely when the UI is uncertain by stopping at explanation instead of acting.

## Files

Modify:

- `profiles/ringcentral-video.yaml`
- `profiles/ringcentral-video-bind-speaker.yaml`
- `profiles/ringcentral-video-codex-cli-speaker.yaml`
- `profiles/ringcentral-video-openai.example.yaml`
- `profiles/ringcentral-video-piper-speaker.yaml`
- `src/ai_presenter/profiles/ringcentral-video.yaml`
- `tests/unit/test_config_loader.py`
- `tests/unit/test_presenter_context.py`
- `tests/unit/test_openai_provider.py`
- `tests/unit/test_codex_cli_provider.py`
- `tests/unit/test_presenter_skill_packaging.py`

Create:

- `presenter/skills/ringcentral-safety.md`
- `src/ai_presenter/presenter/skills/ringcentral-safety.md`

## Behavior

Loading a RingCentral profile should resolve the new skill path. `load_presenter_context()` should expose a third skill named `ringcentral-safety`, and provider prompt formatting should include the skill text just like existing skills.

No Python production code should be required. If implementation starts to require runtime policy changes, split that into a future slice.

## Tests

Use tests as the behavior contract:

- `test_load_ringcentral_bind_speaker_profile` expects the third resolved skill path.
- A parametrized config-loader test expects every root RingCentral profile to load the same three skills in the same order.
- A packaged-profile test expects `src/ai_presenter/profiles/ringcentral-video.yaml` to resolve its packaged safety skill copy.
- `test_load_presenter_context_reads_configured_soul_and_memory` expects the third skill name and a RingCentral safety marker in its content.
- OpenAI and Codex CLI prompt tests expect a skill marker proving `ringcentral-safety` content reaches model narration context.
- A packaged-copy sync test expects root `presenter/skills/*.md` and packaged `src/ai_presenter/presenter/skills/*.md` to have the same filenames and content.
- Optional content checks can assert the skill mentions blocked recording/leave boundaries and accepted evidence language.

## Out Of Scope

- No live RingCentralVideo automation.
- No route `can_operate` changes.
- No acceptance evidence promotion.
- No package route edits.
- No UI redesign.
- No language or tone expansion in this slice.

## Risks

- Prompt inclusion is testable, but model behavior is not deterministic. Keep the skill direct and operational.
- Duplicate root and packaged copies can drift. Tests should cover profile loading; final review should compare skill copies.
- Overly long skill content can dilute provider prompts. Keep it concise and avoid copying the full privacy matrix.
