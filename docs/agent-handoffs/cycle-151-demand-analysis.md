# Cycle 151 Demand Analysis: Language Alias Display Slice

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`

## User Value

The long-running product direction is to expand presenter languages and tones,
but the next smallest valuable slice should improve how users select an
already-supported language rather than adding a new canonical tone or a new
runtime language.

Spanish is already package-complete for RingCentral Video and runtime-selectable
through OpenAI-backed speech only. The current voice surface accepts `es`,
`es-ES`, `es-MX`, `Spanish`, and `espanol`, and `voices` already has an
ASCII-safe catalog. The practical gap is operator ergonomics: a demo operator or
maintainer may naturally type `Español`, `es-419`, `es-LA`, or a LatAm Spanish
phrase when preparing a RingCentral demo for Spanish-speaking users. Supporting
those inputs as aliases to the existing `es` route is useful, easy to explain,
and testable without changing provider behavior.

This is more valuable right now than adding a ninth tone. The existing tone set
already covers the main RingCentral/AiPresenter situations:

- `professional` and `formal` for product or executive walkthroughs.
- `coach` and `friendly` for guided demos.
- `support` for troubleshooting.
- `careful` for privacy, consent, recording, and boundary-sensitive controls.

A new canonical tone would require expanding choice metadata, prompt
description, render behavior, CLI catalog expectations, and controller menu
surface. That is still small technically, but it creates a new user-facing mode
without an obvious unmet RingCentral use case. Spanish alias/display polish has
a clearer next-step value and a lower risk profile because it stays inside an
existing language boundary.

## Recommended Minimum Scope

Prioritize a language alias/display slice for Spanish only:

1. Add additional Spanish aliases that normalize to existing canonical `es`.
   Recommended inputs:
   - `es-419`
   - `es-la`
   - `latam-spanish`
   - `latin-american-spanish`
   - `español`
2. Keep `language_label("es") == "Spanish"` and keep the canonical package key
   displayed as `Language: es` for package-local commands.
3. Preserve `voices` ASCII-safe output when it lists aliases. If `Español` is
   included in the public alias list, the catalog should still be printable on
   legacy Windows consoles through the existing backslash-escaped formatting.
4. Treat these aliases as input and discovery polish only. They do not add local
   Spanish SAPI/Piper support, new package localization, new matching behavior,
   or live demo acceptance.

Likely implementation files for the next worker:

- `src/ai_presenter/runtime/voice.py`
- `tests/unit/test_voice.py`
- `tests/unit/test_cli.py`
- possibly `README.md` or `docs/knowledge/language-lifecycle.md` only if the
  implementation worker chooses to document the new aliases

The safest testing anchor is `PresenterVoiceSettings(language=...)` plus the
existing public alias helper and `voices` catalog tests. If package-local
commands share presenter aliases through `resolve_package_language_key`, add or
adjust a focused CLI test that proves `entrypoints` or `localization-report`
still resolves these aliases to package key `es` while unknown package-only
keys remain raw.

## Do Not Touch

- Do not add a new `PresenterLanguage` canonical value.
- Do not add Spanish local SAPI/Piper routing, profiles, assets, or fallback
  behavior.
- Do not change OpenAI-only Spanish provider compatibility.
- Do not change demo/controller/doctor runtime support claims except for tests
  that prove the new aliases resolve to the existing `es` behavior.
- Do not claim live RingCentral Video acceptance, provider availability, or
  runtime execution evidence.
- Do not expand package Spanish content, Q&A aliases, entrypoint metadata, or
  localization completeness rules.
- Do not add a new canonical tone in the same cycle.
- Do not edit `.coverage`, package metadata, unrelated tests, or unrelated docs.
- Do not revert other workers' changes.

## Acceptance Criteria

The implementation should be considered complete only when these repo-local
contracts hold:

- `PresenterVoiceSettings(language="es-419").language == "es"`.
- `PresenterVoiceSettings(language="es-LA").language == "es"`.
- `PresenterVoiceSettings(language="latin-american-spanish").language == "es"`.
- `PresenterVoiceSettings(language="Español").language == "es"`.
- `presenter_language_aliases("es")` exposes the new aliases in a stable order.
- `ai-presenter voices` still exits `0`, lists Spanish aliases, and its stdout
  remains ASCII-safe.
- OpenAI Spanish profile checks still pass through the existing `es` route.
- Local fake/Piper/Windows Spanish profile checks still fail with the existing
  OpenAI requirement.
- Unknown package-only language keys, such as `de`, still remain package-local
  lookup keys and are not rejected as unsupported presenter languages by
  `localization-report` or `entrypoints`.
- No provider/runtime/live RingCentral acceptance is claimed or implied.

Suggested focused verification for the implementation worker:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_voice.py tests\unit\test_cli.py::test_voices_lists_language_tone_choices tests\unit\test_cli.py::test_voices_catalog_output_is_ascii_safe_for_legacy_windows_console tests\unit\test_cli.py::test_package_language_alias_normalization_is_documented tests\unit\test_cli.py::test_voices_targeted_openai_spanish_profile_is_supported tests\unit\test_cli.py::test_voices_profile_reports_supported_and_unsupported_languages
git diff --check
git status --short
```

If the worker edits only docs during implementation planning, use the narrower
doc checks requested by that cycle instead.

## Implementation Handoff Prompt

```text
Cycle151 implementation task. You are not the only worker in the repo; do not
revert other changes and do not touch `.coverage` unless explicitly instructed.

Repository: C:\Users\rcadmin\Documents\Repos\AiPresenter

Goal: implement the Cycle151 minimum language alias/display slice. Add
Spanish input aliases that normalize to existing canonical `es`: `es-419`,
`es-la`, `latam-spanish`, `latin-american-spanish`, and `español`.

Read first:
- docs/agent-handoffs/cycle-151-demand-analysis.md
- docs/knowledge/language-lifecycle.md
- src/ai_presenter/runtime/voice.py
- tests/unit/test_voice.py
- tests/unit/test_cli.py around `voices` and package language alias tests

Scope:
- Prefer the smallest code/test change in `runtime.voice` and focused unit
  tests.
- Keep `language_label("es") == "Spanish"` and all provider compatibility
  behavior unchanged.
- Preserve ASCII-safe `ai-presenter voices` output.
- If package-local CLI language resolution consumes presenter aliases, cover
  that `es-419`/`Español` resolve to package key `es` without blocking unknown
  package-only keys like `de`.

Do not:
- Add a new runtime language.
- Add local Spanish SAPI/Piper support.
- Add or change live RingCentral acceptance claims.
- Add a new canonical tone in this cycle.
- Modify package localization content or Q&A matching.
- Touch `.coverage`.

Acceptance:
- Focused voice and CLI tests pass.
- `git diff --check` passes.
- The final diff does not include provider/runtime acceptance claims or
  unrelated files.
```
