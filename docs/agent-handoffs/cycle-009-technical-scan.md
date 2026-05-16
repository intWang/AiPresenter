# Cycle 009 Technical Scan

Date: 2026-05-16

Scope: read-only scan for the next candidate, expanding presenter language aliases and tone types. Production code was not edited by this sidecar; only this handoff document was created.

Workspace note: the worktree was already dirty when this scan began. Existing modified and untracked files were left untouched. I also observed an untracked implementation plan at `docs/superpowers/plans/2026-05-16-voice-language-tone-expansion.md`; do not overwrite or assume ownership of it without coordinating.

## Summary

The safest seam is `PresenterVoiceSettings` in `src/ai_presenter/runtime/voice.py`. Today it is a frozen dataclass with `Literal` annotations, but those annotations do not validate runtime inputs. A call like `PresenterVoiceSettings(language="zh-CN")` would store `"zh-CN"` as-is, miss `localizedText.zh`, log a non-canonical language, and skip Chinese provider routing because the code checks `settings.language == "zh"`.

Add normalization at construction time and keep downstream code canonical. The rest of the system should continue to see only `en` or `zh` for language, and only known tone literals for tone. That avoids YAML duplication such as `zh-CN` keys, preserves existing English defaults, and keeps current provider routing intact.

For new tones such as `friendly`, `coach`, and `formal`, keep existing `professional`, `conversational`, and `concise` outputs unchanged. Add new tone literals and complete their description, label, text rendering, and SAPI-rate behavior in one pass so controller labels and runtime dictionaries cannot drift.

## Current Code Seams

- `src/ai_presenter/runtime/voice.py:7` defines `PresenterLanguage = Literal["en", "zh"]`.
- `src/ai_presenter/runtime/voice.py:8` defines `PresenterTone = Literal["professional", "conversational", "concise"]`.
- `src/ai_presenter/runtime/voice.py:10` has `_TONE_DESCRIPTIONS`; adding a tone without updating this map causes `render_voice_instruction()` to raise `KeyError` at `src/ai_presenter/runtime/voice.py:41`.
- `src/ai_presenter/runtime/voice.py:33` uses `@dataclass(frozen=True)` with generated init. This preserves equality/repr nicely, but provides no runtime validation or alias normalization.
- `src/ai_presenter/runtime/voice.py:39` renders language as Chinese only for exact `"zh"`; any alias currently becomes English.
- `src/ai_presenter/runtime/voice.py:55` resolves localized narration with `narration.localized_text.get(settings.language)`. Package data uses `zh`, so aliases such as `zh-CN` miss authored Chinese.
- `src/ai_presenter/runtime/voice.py:62` and `src/ai_presenter/runtime/voice.py:73` validate and route speech providers by exact canonical language.
- `src/ai_presenter/runtime/voice.py:82` maps SAPI rate only for Chinese `conversational` and `concise`; every other language/tone combination currently returns `0`.
- `src/ai_presenter/runtime/voice.py:91` and `src/ai_presenter/runtime/voice.py:99` are the deterministic text style points. Existing output behavior lives here and should not change for the current three tones.

## Controller And CLI Surfaces

There is no argparse surface in the current code; the CLI is Typer-based in `src/ai_presenter/cli.py`. The `controller` command at `src/ai_presenter/cli.py:110` accepts only `--profile`, `--package`, `--flow`, `--dry-run`, and `--debug`. Language/tone controls exist only in the Tk controller.

Tk/controller seams:

- `src/ai_presenter/runtime/controller.py:439` and `src/ai_presenter/runtime/controller.py:440` initialize display labels `"English"` and `"Professional"`.
- `src/ai_presenter/runtime/controller.py:444` maps display tone labels to `PresenterTone` values. Add new tones here or, preferably, replace this local map with shared metadata from `runtime.voice`.
- `src/ai_presenter/runtime/controller.py:457` builds `PresenterVoiceSettings` from Tk state. The language branch treats every non-`"Chinese"` label as `"en"`, so future labels should not rely on ad hoc conditionals.
- `src/ai_presenter/runtime/controller.py:605` and `src/ai_presenter/runtime/controller.py:671` apply the current voice before starting or answering.
- `src/ai_presenter/runtime/controller.py:768` and `src/ai_presenter/runtime/controller.py:769` hard-code the language and tone `OptionMenu` values.
- `src/ai_presenter/runtime/controller_view_model.py:10` and `src/ai_presenter/runtime/controller_view_model.py:11` maintain separate label maps for language/tone. Adding tone values only in `voice.py` will break `render_voice_label()` at `src/ai_presenter/runtime/controller_view_model.py:92`.

Recommended controller shape: expose shared voice choice metadata from `runtime.voice`, then build both Tk menus and controller labels from that shared source. That removes the need to update `voice.py`, `controller.py`, and `controller_view_model.py` in parallel for every new tone.

## Session And Question Paths

- `src/ai_presenter/runtime/session.py:31` defaults sessions to `PresenterVoiceSettings()`.
- `src/ai_presenter/runtime/session.py:55` validates voice when the selected target is a material package target.
- `src/ai_presenter/runtime/session.py:60` passes the active voice into `answer_question()`.
- `src/ai_presenter/runtime/questions.py:147` logs `voice.language` and `voice.tone` as metadata. Normalize before this point so logs stay canonical and dashboards do not split `zh`, `zh-CN`, and `zh_CN`.
- `src/ai_presenter/runtime/questions.py:239` matches Q&A across all localized question strings, independent of active language.
- `src/ai_presenter/runtime/questions.py:246` selects localized answers by exact `voice.language`. This is another reason `zh-CN -> zh` should happen before rendering.
- `src/ai_presenter/runtime/questions.py:349` delegates final deterministic answer rendering to `render_presenter_text()`, so new tone text behavior belongs in `voice.py`.

## Package Localized Data

- `src/ai_presenter/packages/models.py:35` supports `OperationEntrypoint.questionAliases` as `dict[str, list[str]]`.
- `src/ai_presenter/packages/models.py:52` supports `DemoStepNarration.localizedText` as `dict[str, str]`.
- `src/ai_presenter/packages/models.py:79` supports Q&A `localizedQuestions` and `localizedAnswers`.
- `packages/ringcentral-video.yaml:202`, `:244`, `:265`, `:302`, and `:437` contain package-owned `questionAliases.zh`.
- `packages/ringcentral-video.yaml:755` through `:1005` contain `localizedText.zh` for the meeting control map flow.
- `packages/ringcentral-video.yaml:1176` and `:1182` contain localized Q&A question/answer data under `zh`.

Do not add duplicate `zh-CN` package keys for this candidate. Normalize incoming user/API/controller language codes to `zh` instead. That keeps package authoring simple and avoids subtly different localized content per alias.

## TTS And Provider Implications

- `src/ai_presenter/runtime/factory.py:57` creates provider registries with an optional `PresenterVoiceSettings`.
- `src/ai_presenter/runtime/factory.py:75` registers OpenAI speech directly; `OpenAISpeechProvider` receives only final text, model, and voice, not tone/language metadata.
- `src/ai_presenter/runtime/factory.py:77` registers Piper for English and a `windows-sapi-zh` fallback. Chinese provider routing depends on canonical `"zh"` in `resolve_speech_provider_name()`.
- `src/ai_presenter/runtime/factory.py:82`, `:93`, `:102`, `:112`, `:121`, `:131`, and `:140` construct Windows SAPI providers with `sapi_rate_for_voice()` using the active tone.
- `src/ai_presenter/runtime/factory.py:278` validates the canonical voice and `src/ai_presenter/runtime/factory.py:280` resolves the speech provider name before running the timeline.
- `src/ai_presenter/providers/windows_speech.py:12` supports voice name, rate, and volume only. New expressive tones cannot become rich prosody here; at most they can map to conservative rate changes.
- `src/ai_presenter/providers/piper_provider.py:13` is a fixed voice CLI wrapper. It has no tone controls; tone is only in the rendered text.
- `src/ai_presenter/providers/openai_provider.py:52` calls audio speech with model, voice, input, and `response_format="wav"`. There is no current TTS instruction field in this wrapper.
- `src/ai_presenter/providers/codex_cli.py:101` explicitly asks for one concise English narration sentence in event narration. Controller material demos/questions use `voice.py`, but expanding live presenter-loop language/tone would need a separate provider-interface pass.

Provider-safe rule: normalize before registry creation and validation. Do not let provider routing compare aliases directly.

## Safe API Shape

Keep the public value object but make it normalizing:

```python
@dataclass(frozen=True, init=False)
class PresenterVoiceSettings:
    language: PresenterLanguage
    tone: PresenterTone

    def __init__(
        self,
        language: str = "en",
        tone: str = "professional",
    ) -> None:
        object.__setattr__(self, "language", normalize_presenter_language(language))
        object.__setattr__(self, "tone", normalize_presenter_tone(tone))
```

Add small helpers:

- `normalize_presenter_language(value: str) -> PresenterLanguage`
- `normalize_presenter_tone(value: str) -> PresenterTone`
- `language_label(language: str | PresenterLanguage) -> str`
- `tone_label(tone: str | PresenterTone) -> str`
- `PRESENTER_LANGUAGE_CHOICES`
- `PRESENTER_TONE_CHOICES`

Recommended language aliases:

- `en`, `en-us`, `en_us`, `english` -> `en`
- `zh`, `zh-cn`, `zh_cn`, `zh-hans`, `zh_hans`, `chinese` -> `zh`

Recommended tone aliases:

- Preserve existing canonical tones: `professional`, `conversational`, `concise`
- Add canonical tones: `friendly`, `coach`, `formal`
- Optional friendly aliases: `warm` -> `friendly`, `mentor` -> `coach`, `structured` -> `formal`

Reject unknown languages and tones with `ValueError`. Silent fallback would hide operator mistakes and could route the wrong TTS provider.

## Tone Compatibility

Do not rename or remap existing tones:

- `professional` should keep current default output.
- `conversational` should keep current `Sure.` English prefix and Chinese fallback prefix behavior.
- `concise` should keep first-sentence behavior.

For new tones, prefer additive deterministic behavior:

- `friendly`: warmer than professional, but only when explicitly selected.
- `coach`: step-by-step framing, but keep factual package content unchanged.
- `formal`: can initially behave like professional text output with a different instruction/label, which preserves low risk while exposing the requested type.

For localized authored narration, be cautious with prefixes. `render_narration_text()` currently applies only concise truncation to localized text via `_apply_tone_to_localized_text()`. That is good: authored Chinese scripts should not get automatic English-style filler unless the product deliberately wants it.

For Windows SAPI, keep rate mapping modest. A safe first mapping is:

- `professional` and `formal`: `0`
- `conversational` and `friendly`: `-1` for Chinese
- `concise`: `1` for Chinese
- `coach`: `0` or `-1` for Chinese, depending on desired pace; test it explicitly

## Tests To Update

- `tests/unit/test_voice.py:13` locks defaults. Add normalization, rejection, new tone instruction/rendering, and provider-routing tests here.
- `tests/unit/test_voice.py:97` locks Chinese SAPI rate behavior. Extend it for new tones without changing existing assertions.
- `tests/unit/test_controller.py:371` locks controller voice labels. Add labels for at least `zh-CN` normalization and one expanded tone.
- `tests/unit/test_controller_view_model.py:6` and `:41` lock operator-view labels. Add view-model coverage for a new tone such as `coach`.
- `tests/unit/test_controller_session.py:61` and `:77` exercise active voice in questions and SAPI profile routing. Add an alias input such as `language="zh-CN"` to prove it routes and answers as Chinese.
- `tests/unit/test_questions.py:26`, `:252`, and `:431` cover Chinese answer rendering, localized answers, and logging. Add assertions that logs contain canonical `language=zh` for alias input.
- `tests/unit/test_runtime_factory.py:95`, `:475`, and `:546` cover provider registry/routing/rate behavior. Add an alias-routing test through `run_existing_window_material_demo()` or `resolve_speech_provider_name()`.
- `tests/unit/test_material_packages.py:203` already asserts `meeting-control-map-demo` has `localizedText.zh`; this should not need new `zh-CN` package data.
- `tests/unit/test_cli.py:81` covers controller dry-run only. No CLI language/tone test is needed unless CLI flags are added.

Suggested focused verification for an implementation cycle:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_voice.py tests\unit\test_controller.py tests\unit\test_controller_view_model.py tests\unit\test_controller_session.py tests\unit\test_questions.py tests\unit\test_runtime_factory.py
.\.venv\Scripts\ruff check --no-cache src\ai_presenter\runtime\voice.py src\ai_presenter\runtime\controller.py src\ai_presenter\runtime\controller_view_model.py tests\unit\test_voice.py tests\unit\test_controller.py tests\unit\test_controller_view_model.py tests\unit\test_controller_session.py tests\unit\test_questions.py tests\unit\test_runtime_factory.py
.\.venv\Scripts\mypy --no-incremental src\ai_presenter\runtime\voice.py src\ai_presenter\runtime\controller.py src\ai_presenter\runtime\controller_view_model.py
```

## Implementation Cautions

- `Literal` is a static typing contract here, not runtime safety. Add runtime normalization/rejection at the value-object boundary.
- If `PresenterVoiceSettings.__init__` accepts `str`, keep fields typed as canonical `PresenterLanguage` and `PresenterTone` after normalization.
- Keep `PresenterVoiceSettings()` equality stable for existing tests that compare dataclass instances in controller runner calls.
- Update every dictionary keyed by `PresenterTone`: `_TONE_DESCRIPTIONS`, controller/view labels, and any new choice metadata.
- Do not change package schema keys. Existing package-localized data is already keyed by canonical `zh`.
- Do not make OpenAI/Piper/Windows provider constructors depend on free-form tone objects in this pass. Keep provider interfaces stable and feed them canonical final text/provider names.
- Be careful with live event narration. `CodexCliNarrationProvider` is currently English-only by prompt, while material-package narration is language-aware through `voice.py`.

## Commands Used

```powershell
Get-Content -LiteralPath 'C:\Users\rcadmin\.codex\superpowers\skills\using-superpowers\SKILL.md'
Get-Content -LiteralPath 'C:\Users\rcadmin\.codex\superpowers\skills\writing-plans\SKILL.md'
git status --short
rg --files
rg -n "voice|tone|language|Language|Literal|question|controller|argparse|Tk|tts|provider" src tests package.json pyproject.toml
Get-ChildItem -LiteralPath 'docs\agent-handoffs' -Force
rg -n "^" src\ai_presenter\runtime\voice.py
rg -n "^" src\ai_presenter\runtime\session.py
rg -n "^" src\ai_presenter\cli.py
rg -n "^" src\ai_presenter\runtime\controller.py
rg -n "^" src\ai_presenter\runtime\controller_view_model.py
rg -n "^" src\ai_presenter\runtime\factory.py
rg -n "^" src\ai_presenter\runtime\questions.py
rg -n "^" src\ai_presenter\packages\models.py
rg -n "^" tests\unit\test_voice.py
rg -n "^" tests\unit\test_controller.py
rg -n "^" tests\unit\test_controller_session.py
rg -n "^" tests\unit\test_questions.py
rg -n "voice|language|tone|controller|dry run|OptionMenu|PresenterVoiceSettings|localized|questionAliases|localizedText|localizedAnswers|localizedQuestions|zh|Chinese|Professional|Conversational|Concise" tests\unit\test_cli.py tests\unit\test_material_packages.py tests\unit\test_material_runtime.py tests\unit\test_package_demo.py packages\ringcentral-video.yaml profiles\ringcentral-video*.yaml src\ai_presenter\profiles\ringcentral-video.yaml
rg -n "^" tests\unit\test_material_packages.py
rg -n "^" tests\unit\test_cli.py
rg -n "^" tests\unit\test_package_demo.py
rg -n -C 4 "questionAliases|localizedText|localizedQuestions|localizedAnswers|^qa:" packages\ringcentral-video.yaml
rg -n "id:|providers:|narration:|speech:|vision:" profiles src\ai_presenter\profiles
rg -n "language|tone|PresenterVoiceSettings|render_voice_label|OptionMenu|current_voice|set_voice|voice=" src tests
rg -n "Localized|localized|questionAliases|language|tone|zh-CN|zh_CN|zh" docs\superpowers docs\agent-handoffs README.md
rg -n "^" docs\superpowers\plans\2026-05-16-voice-language-tone-expansion.md
rg -n -C 3 "language and tone|controller target|question|tone selectors|controller" README.md
rg -n "^" tests\unit\test_controller_view_model.py
rg -n "^" tests\unit\test_runtime_factory.py
rg -n "^" src\ai_presenter\providers\openai_provider.py
rg -n "^" src\ai_presenter\providers\piper_provider.py
rg -n "^" src\ai_presenter\providers\windows_speech.py
rg -n "^" src\ai_presenter\providers\codex_cli.py
rg -n "python|mypy|ruff|typer|pydantic" pyproject.toml
rg -n "Provider|providers|speech|Literal|windows-sapi|piper|openai|fake|codex-cli" src\ai_presenter\config\models.py tests\unit\test_config_loader.py tests\unit\test_provider_registry.py tests\unit\test_openai_provider.py tests\unit\test_piper_provider.py tests\unit\test_windows_speech_provider.py
rg -n -C 4 "class ProviderConfig|speech: str|normalize_provider_name|providers:" src\ai_presenter\config\models.py
rg -n "^" src\ai_presenter\config\models.py
Get-Content -LiteralPath 'docs\agent-handoffs\cycle-008-technical-scan.md' -TotalCount 180
Test-Path -LiteralPath 'docs\agent-handoffs\cycle-009-technical-scan.md'
```

Notes on command results: two broad `rg` scans returned nonzero because `package.json` does not exist and PowerShell passed `profiles\ringcentral-video*.yaml` in a way `rg` treated as an invalid path. Both commands still produced useful partial output, and later targeted scans replaced the missing coverage.
