# Cycle 032 Technical Scan: RingCentral Safety Presenter Skill

Date: 2026-05-16
Role: technical discovery
Scope: read-only technical scan. No production code was edited in this pass.

## Findings

- Presenter skills are duplicated in root `presenter/skills/` and packaged `src/ai_presenter/presenter/skills/`. Current files are content-identical.
- Root has five RingCentral profiles with `narration.skillPaths`: `ringcentral-video.yaml`, `ringcentral-video-bind-speaker.yaml`, `ringcentral-video-codex-cli-speaker.yaml`, `ringcentral-video-openai.example.yaml`, and `ringcentral-video-piper-speaker.yaml`.
- Packaged `src/ai_presenter/profiles/` currently has only `ringcentral-video.yaml`.
- `load_profile()` resolves `soulPath`, `memoryPath`, and `skillPaths` relative to the profile file and fails if a referenced file is missing.
- `load_presenter_context()` reads markdown files into `PresenterContext`.
- `format_presenter_context()` appends skill sections as `Presenter skill - {name}:`.
- OpenAI and Codex CLI narration providers include formatted presenter context in prompts.
- Fake narration and scripted material demo narration do not consume these skills.

## Implementation Recommendation

- Add `presenter/skills/ringcentral-safety.md`.
- Add identical packaged copy `src/ai_presenter/presenter/skills/ringcentral-safety.md`.
- Append `../presenter/skills/ringcentral-safety.md` after `live-explainer.md` in all root RingCentral profiles and the packaged base profile.
- Keep the skill behavior-focused: privacy boundaries, shared-screen limits, chat/participants/invite redaction, recording/leave confirmation, dialog cleanup, and evidence language.
- Do not change Python runtime code unless tests reveal a loading bug.

## Tests To Add Or Update

- Add a parametrized config-loader test proving every root RingCentral profile loads skills in this order: `app-director`, `live-explainer`, `ringcentral-safety`.
- Add a packaged-profile test proving `src/ai_presenter/profiles/ringcentral-video.yaml` resolves `src/ai_presenter/presenter/skills/ringcentral-safety.md`.
- Update the existing bind-speaker path assertion to include the third skill.
- Update presenter-context tests so the third skill is loaded, named, and formatted.
- Add or update provider prompt tests to prove the safety skill marker reaches OpenAI and Codex CLI prompts.
- Add a root-vs-packaged skill copy sync test comparing filenames and contents, preferably in a dedicated packaging test file so it does not mix with unrelated CLI test changes.

## Red Test Commands

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_config_loader.py::test_all_ringcentral_profiles_include_ringcentral_safety_skill tests\unit\test_config_loader.py::test_packaged_ringcentral_profile_resolves_packaged_safety_skill tests\unit\test_presenter_context.py::test_load_presenter_context_reads_configured_soul_and_memory
```

Expected before implementation: missing test functions or failing assertions because `ringcentral-safety` is not configured.

## Risks

- YAML references without both skill copies will break `load_profile()`.
- This is prompt-context safety, not deterministic runtime enforcement.
- Material package scripts and Q&A remain governed by package YAML and existing question safety logic.
- Root and packaged copies can drift unless tests explicitly compare them.
- Prompt bloat is possible if the skill copies full policy tables instead of concise behavior rules.

## Suggested Focused Verification

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_config_loader.py tests\unit\test_presenter_context.py tests\unit\test_openai_provider.py::test_narration_instructions_include_presenter_soul_and_memory tests\unit\test_codex_cli_provider.py::test_codex_cli_prompt_includes_presenter_soul_and_memory
.\.venv\Scripts\ruff check --no-cache tests\unit\test_config_loader.py tests\unit\test_presenter_context.py tests\unit\test_openai_provider.py tests\unit\test_codex_cli_provider.py
.\.venv\Scripts\mypy --no-incremental src\ai_presenter\runtime\presenter_context.py src\ai_presenter\config tests\unit\test_config_loader.py tests\unit\test_presenter_context.py tests\unit\test_openai_provider.py tests\unit\test_codex_cli_provider.py
```

## Commands Used

```powershell
rg --files -g 'presenter/skills/*.md' -g 'src/ai_presenter/presenter/skills/*.md' -g 'profiles/ringcentral-video*.yaml' -g 'src/ai_presenter/profiles/ringcentral-video*.yaml' -g 'tests/unit/test_config_loader.py' -g 'tests/unit/test_presenter_context.py' -g 'tests/unit/*provider*'
rg -n "skillPaths|skill_paths|skills|PresenterContext|presenter_context|soulPath|memoryPath" src tests profiles presenter packages docs -g '!*.pyc'
Get-Content presenter\skills\app-director.md
Get-Content presenter\skills\live-explainer.md
Get-Content profiles\ringcentral-video*.yaml
Get-Content src\ai_presenter\profiles\ringcentral-video.yaml
Get-Content src\ai_presenter\runtime\presenter_context.py
Get-Content tests\unit\test_config_loader.py
Get-Content tests\unit\test_presenter_context.py
Get-Content tests\unit\test_openai_provider.py
Get-Content tests\unit\test_codex_cli_provider.py
Compare-Object (Get-Content 'presenter\skills\app-director.md') (Get-Content 'src\ai_presenter\presenter\skills\app-director.md')
Compare-Object (Get-Content 'presenter\skills\live-explainer.md') (Get-Content 'src\ai_presenter\presenter\skills\live-explainer.md')
```
