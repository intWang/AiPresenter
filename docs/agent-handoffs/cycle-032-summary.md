# Cycle 032 Summary: RingCentral Safety Presenter Skill

Date: 2026-05-16
Role: implementation summary

## Goal

Add a RingCentral-specific presenter safety skill so model-backed narration receives concrete privacy, side-effect, cleanup, and evidence-language boundaries while presenting RingCentral Video.

## Implemented

- Added `presenter/skills/ringcentral-safety.md`.
- Added identical packaged copy `src/ai_presenter/presenter/skills/ringcentral-safety.md`.
- Added `../presenter/skills/ringcentral-safety.md` after `live-explainer.md` in:
  - `profiles/ringcentral-video.yaml`
  - `profiles/ringcentral-video-bind-speaker.yaml`
  - `profiles/ringcentral-video-codex-cli-speaker.yaml`
  - `profiles/ringcentral-video-openai.example.yaml`
  - `profiles/ringcentral-video-piper-speaker.yaml`
  - `src/ai_presenter/profiles/ringcentral-video.yaml`
- Updated config loader tests to verify all root RingCentral profiles load `app-director`, `live-explainer`, and `ringcentral-safety` in order.
- Added packaged-profile resolution coverage for the packaged safety skill.
- Updated presenter context tests to verify the third skill loads and formats.
- Updated OpenAI and Codex CLI provider prompt tests to prove the safety skill reaches narration context.
- Added root/packaged presenter skill copy sync coverage.
- Kept the packaging copy-sync test in `tests/unit/test_presenter_skill_packaging.py` so this slice can be committed without staging unrelated `test_cli.py` history.
- Wrote Cycle 032 demand, technical scan, review, spec, and implementation plan docs.

## TDD Evidence

RED:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_config_loader.py::test_load_ringcentral_bind_speaker_profile tests\unit\test_config_loader.py::test_all_ringcentral_profiles_include_ringcentral_safety_skill tests\unit\test_config_loader.py::test_packaged_ringcentral_profile_resolves_packaged_safety_skill tests\unit\test_presenter_context.py::test_load_presenter_context_reads_configured_soul_and_memory tests\unit\test_openai_provider.py::test_narration_instructions_include_loaded_ringcentral_safety_skill tests\unit\test_codex_cli_provider.py::test_codex_cli_prompt_includes_loaded_ringcentral_safety_skill tests\unit\test_cli.py::test_packaged_presenter_skill_copies_match_repo_skills
```

Result: `11 failed`, all pointing to missing safety skill/profile wiring.

GREEN:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_config_loader.py::test_load_ringcentral_bind_speaker_profile tests\unit\test_config_loader.py::test_all_ringcentral_profiles_include_ringcentral_safety_skill tests\unit\test_config_loader.py::test_packaged_ringcentral_profile_resolves_packaged_safety_skill tests\unit\test_presenter_context.py::test_load_presenter_context_reads_configured_soul_and_memory tests\unit\test_openai_provider.py::test_narration_instructions_include_loaded_ringcentral_safety_skill tests\unit\test_codex_cli_provider.py::test_codex_cli_prompt_includes_loaded_ringcentral_safety_skill tests\unit\test_cli.py::test_packaged_presenter_skill_copies_match_repo_skills
```

Result: `11 passed in 2.33s`.

## Verification

Focused:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_config_loader.py tests\unit\test_presenter_context.py tests\unit\test_presenter_skill_packaging.py tests\unit\test_openai_provider.py::test_narration_instructions_include_presenter_soul_and_memory tests\unit\test_openai_provider.py::test_narration_instructions_include_loaded_ringcentral_safety_skill tests\unit\test_codex_cli_provider.py::test_codex_cli_prompt_includes_presenter_soul_and_memory tests\unit\test_codex_cli_provider.py::test_codex_cli_prompt_includes_loaded_ringcentral_safety_skill
```

Result: `37 passed in 2.74s`.

Static checks:

```powershell
.\.venv\Scripts\ruff check --no-cache tests\unit\test_config_loader.py tests\unit\test_presenter_context.py tests\unit\test_openai_provider.py tests\unit\test_codex_cli_provider.py tests\unit\test_cli.py
.\.venv\Scripts\mypy --no-incremental src\ai_presenter\runtime\presenter_context.py src\ai_presenter\config tests\unit\test_config_loader.py tests\unit\test_presenter_context.py tests\unit\test_openai_provider.py tests\unit\test_codex_cli_provider.py tests\unit\test_cli.py
```

Results:

- `All checks passed!`
- `Success: no issues found in 8 source files`

Full verification:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests
.\.venv\Scripts\ruff check --no-cache .
.\.venv\Scripts\mypy --no-incremental src tests
git diff --check
```

Results:

- `537 passed, 1 warning in 48.60s`
- `All checks passed!`
- `Success: no issues found in 80 source files`
- `git diff --check` exit 0 with existing LF-to-CRLF warnings only

The pytest warning is the existing pywinauto STA COM threading warning.

## Review

Review subagent found no blocker in the safety skill wiring. It noted that the broader worktree includes unrelated earlier-cycle changes, so any future staging/commit should be path-scoped.

## Out Of Scope Kept

- No live RingCentral automation.
- No package route edits.
- No acceptance evidence promotion.
- No runtime route safety policy changes.
- No controller UI changes.

## Suggested Next Slice

Move to a small performance-oriented slice: precompute or cache question/entrypoint matching candidates so repeated live questions do less per-call string/token work while preserving all existing precedence and safety behavior.
