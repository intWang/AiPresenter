# Cycle 009 Demand Analysis: Voice Language And Tone Expansion

Date: 2026-05-16
Role: demand-analysis sidecar
Write scope: this file only

## Read Scope

Reviewed local repo evidence only. No production code was modified.

- `README.md`
- `docs/agent-handoffs/cycle-004-demand-analysis.md`
- `docs/agent-handoffs/cycle-006-summary.md`
- `docs/agent-handoffs/cycle-007-summary.md`
- `docs/agent-handoffs/cycle-008-demand-analysis.md`
- `docs/agent-handoffs/cycle-008-summary.md`
- `docs/runbooks/ringcentral-manual-acceptance.md`
- `docs/superpowers/specs/2026-05-15-controller-app-selection-questions-design.md`
- `docs/superpowers/specs/2026-05-15-native-chinese-narration-design.md`
- `docs/superpowers/specs/2026-05-15-piper-tts-design.md`
- `docs/superpowers/specs/2026-05-16-localized-qa-aliases-design.md`
- `docs/superpowers/specs/2026-05-16-voice-language-tone-expansion-design.md`
- `docs/superpowers/plans/2026-05-16-voice-language-tone-expansion.md`
- `packages/ringcentral-video.yaml`
- `profiles/ringcentral-video-*.yaml`
- `src/ai_presenter/cli.py`
- `src/ai_presenter/runtime/controller.py`
- `src/ai_presenter/runtime/controller_view_model.py`
- `src/ai_presenter/runtime/factory.py`
- `src/ai_presenter/runtime/questions.py`
- `src/ai_presenter/runtime/voice.py`
- `src/ai_presenter/providers/openai_provider.py`
- `src/ai_presenter/providers/piper_provider.py`
- `src/ai_presenter/providers/windows_speech.py`
- focused unit tests for voice, controller, controller view model, questions, and material packages

The working tree was already dirty before this handoff. I treated all existing modified and
untracked files as other agents' work, including the existing voice language/tone spec and plan,
and did not revert or overwrite them.

## Current Context

The user explicitly asked for continuous optimization and specifically asked to expand language
types and tone types. Cycles 006-008 already laid the path for a narrow, user-visible voice
increment:

- Cycle 006 moved the first multilingual content slice into package data with `questionAliases`,
  `localizedQuestions`, `localizedAnswers`, and Chinese package content for selected RingCentral
  controls.
- Native Chinese narration work added `localizedText` for demo step narration and made authored
  Chinese scripts preferable to English word replacement.
- Cycle 007 timing telemetry records canonical `language` and `tone` metadata for question
  answering without logging private question or answer text.
- Cycle 008 reduced repeated lookup work while preserving localized Q&A, package-owned alias
  precedence, and safety behavior.

The current voice surface is still small and brittle. `PresenterVoiceSettings` is typed around
`en`/`zh` and `professional`/`conversational`/`concise`, while controller labels and Tk option
menus hard-code the same values. Regional inputs such as `zh-CN` or user-facing tone values such
as `friendly` are not normalized through one shared runtime boundary. If such values enter the
system, downstream code can silently treat the language as English, miss `localizedText["zh"]`,
or fail in controller label maps.

## User-Facing Need

The user-facing need is not a broad translation system yet. It is a reliable voice selection
experience:

- Operators should be able to pick a few more natural delivery styles without changing demo
  safety, matched controls, or provider setup.
- Common language inputs such as `English`, `en-US`, `zh-CN`, or `Chinese` should resolve to the
  same supported output families the app already has.
- Chinese package narration and Q&A should keep working when the operator or tests use regional
  language aliases.
- Controller voice labels should not drift from runtime behavior.
- Provider constraints should be visible and boring: unsupported languages fail early instead of
  producing English output by accident or reaching a missing TTS voice late in the demo.

## Sensible Next Languages

Recommended for Cycle 009:

- Keep canonical runtime language families to `en` and `zh`.
- Add normalization aliases for English: `en`, `en-US`, `en-GB`, `English`.
- Add normalization aliases for Chinese: `zh`, `zh-CN`, `zh-Hans`, `Chinese`.
- Consider `zh-SG` as an alias to `zh` only if the team is comfortable treating it as Simplified
  Chinese Mandarin output.
- Be cautious with `zh-TW` and `zh-Hant`. The current package text is Simplified Chinese and the
  local SAPI route uses Huihui, so advertising Traditional Chinese would overpromise. If accepted
  for compatibility, label it as the generic Chinese family and do not claim Traditional-script
  coverage.

Not recommended for Cycle 009:

- Do not add `es`, `ja`, `fr`, `de`, or other new canonical output languages yet. They require
  package-authored `localizedText`, localized Q&A, provider profiles, TTS acceptance, and manual
  review. Adding language enum values without content would make the UI look more capable than
  the product really is.

Sensible later order:

- Japanese (`ja`) and Spanish (`es`) are the strongest next true language candidates after this
  normalization cycle because they are common business-demo languages and have plausible OpenAI
  and Piper TTS paths.
- Add one true language at a time, starting with package content and provider acceptance, not just
  a selector value.

## Sensible Next Tones

Recommended for Cycle 009:

- `friendly`: warmer, reassuring, still accurate.
- `coach`: step-by-step guidance for users who want to learn the workflow.
- `formal`: polished, restrained, suitable for executive or customer-facing demos.

Keep existing tones unchanged:

- `professional`: default structured product-specialist delivery.
- `conversational`: natural and warmer.
- `concise`: shorter and transition-focused.

Useful tone aliases:

- `warm` -> `friendly`
- `mentor` or `guided` -> `coach`
- `structured` or `polished` -> `formal`

Not recommended now:

- Avoid `humorous`, `dramatic`, `urgent`, `salesy`, or emotion-heavy tones. They can obscure
  verified facts and safety boundaries during live meeting automation.
- Avoid free-form tone prompts in the controller until deterministic tone modes are stable.

## UI Implications

The controller should consume shared voice-choice metadata instead of duplicating label maps:

- Language selector can remain simple: `English`, `Chinese`.
- Tone selector should expand to `Professional`, `Conversational`, `Concise`, `Friendly`,
  `Coach`, and `Formal`.
- `render_voice_label()` should use the same shared labels as the option menus.
- The controller operator summary should show canonical, user-friendly labels such as
  `Chinese / Friendly`, regardless of whether the runtime input was `zh`, `zh-CN`, or `Chinese`.
- Unknown language or tone values should fail before a demo starts, not while rendering a status
  row or constructing a speech provider.

Do not redesign the Tk controller in this cycle. This is a selector and label plumbing change,
not a controller layout or workflow rewrite.

## CLI Implications

Current CLI commands load profiles and material packages but do not expose `--language` or
`--tone` flags for `demo` or `controller`. The narrow behavior-preserving scope should keep that
unchanged for Cycle 009.

Future CLI voice flags would be useful, especially for dry-run and manual acceptance:

- `ai-presenter demo --language zh-CN --tone friendly ...`
- `ai-presenter controller --language English --tone coach ...`

If flags are added later, they should call the same normalization functions as the controller.
Do not add a separate Typer-specific language/tone parser.

## Provider And TTS Risks

- OpenAI speech receives final text and can plausibly speak multiple languages, but the current
  provider has one configured voice and does not expose per-tone voice control. Tone should remain
  text/prompt-level for now.
- OpenAI dynamic narration instructions are currently provider-level and not clearly wired to
  controller `PresenterVoiceSettings`. Do not treat new controller tones as dynamic provider
  prompt support unless the runtime path actually passes voice instructions there.
- Piper is currently documented around `en_US-lessac-medium`. The Piper profile routes Chinese
  to Windows SAPI fallback rather than a Chinese Piper voice. New true languages would need voice
  downloads and profile configuration.
- Windows SAPI depends on installed local voices. The code expects English and Chinese routes
  such as Zira and Huihui, and tone control is limited to rate and volume. Missing voices should
  produce clear validation or synthesis errors.
- Regional aliases must normalize before localized package lookup. Otherwise `zh-CN` will miss
  `localizedText["zh"]`, `localizedAnswers["zh"]`, and package-owned Chinese behavior.
- Do not infer provider support from language labels. UI labels are not a substitute for
  `validate_profile_voice()` and actual audio acceptance.

## Behavior-Preserving Scope

Recommended Cycle 009 shape:

1. Add canonical normalization for presenter language and tone at `PresenterVoiceSettings`
   construction time.
2. Add shared language/tone option metadata and label helpers in `runtime.voice`.
3. Update controller and controller view-model label/option code to consume those shared helpers.
4. Add deterministic rendering descriptions for the three new tones.
5. Keep provider routing canonical: existing English/Chinese behavior should be unchanged after
   alias normalization.

Out of scope:

- No new TTS providers.
- No new package YAML localization.
- No new canonical non-English/non-Chinese languages.
- No OpenAI prompt-routing redesign.
- No safety policy changes.
- No question matching changes beyond preserving canonical language metadata.
- No controller layout redesign.
- No CLI flags in this cycle unless explicitly requested by coordination.

## Acceptance Criteria

1. Language normalization:
   - `PresenterVoiceSettings()` remains English / Professional.
   - `PresenterVoiceSettings(language="en-US")`, `en-GB`, and `English` store canonical
     `language == "en"`.
   - `PresenterVoiceSettings(language="zh-CN")`, `zh-Hans`, and `Chinese` store canonical
     `language == "zh"`.
   - Unknown languages such as `es` fail early with a clear error until true Spanish support is
     implemented.

2. Tone normalization:
   - Existing tones remain accepted and behavior-compatible.
   - `friendly`, `coach`, and `formal` are accepted canonical tones.
   - Aliases such as `warm`, `mentor`, and `structured` normalize to their canonical tones.
   - Unknown tones fail early with a clear error.

3. Rendering and labels:
   - `render_voice_instruction()` describes all canonical tones.
   - English deterministic answers visibly differ for the new tones without changing facts,
     entrypoint matches, or safety status.
   - Authored localized narration remains untouched except for the existing concise first-sentence
     behavior.
   - Controller and controller view-model labels render every supported tone without duplicate maps.

4. Provider compatibility:
   - `validate_profile_voice()` and `resolve_speech_provider_name()` continue to work with
     canonical `en`/`zh` after alias normalization.
   - Piper English remains Piper; Piper plus Chinese alias still routes to the existing Chinese
     SAPI fallback.
   - SAPI rate behavior remains modest and deterministic for supported tones.
   - Timing telemetry continues to log canonical language and tone values only.

5. Regression protection:
   - Existing localized Q&A and package alias tests keep passing.
   - Mojibake Chinese input remains unsupported.
   - Risky matched controls remain answer-only unless already safe under current rules.
   - Focused tests cover voice normalization, controller labels, provider routing, and tone
     rendering.
   - `ruff`, `mypy`, focused tests, full unit tests, and `git diff --check` pass for touched files.

## Risks

- Overpromising language support: adding visible language values without package content and TTS
  acceptance will make the product feel unreliable.
- Script mismatch: accepting Traditional Chinese aliases while outputting Simplified Chinese may
  confuse users unless the UI labels stay generic.
- Runtime drift: if labels, options, and normalization are not centralized, the controller can show
  a choice that runtime code cannot handle.
- Provider drift: SAPI/Piper/OpenAI have different tone affordances. Treat tone as presenter text
  style unless a provider path explicitly supports more.
- Localized content drift: regional language codes must reduce to existing package keys or package
  localization will be skipped.
- Encoding hazards: future aliases and localized content should use real UTF-8 strings only. Do
  not add terminal mojibake as supported aliases.

## Recommendation

Proceed with a narrow voice normalization and tone expansion cycle. The existing untracked design
and plan for `voice-language-tone-expansion` are aligned with the right product direction, with one
important demand-analysis caveat: true new languages beyond English and Chinese should be deferred
until content and provider support exist. Cycle 009 should make current language families less
brittle and make tone choice more expressive, while preserving every existing package, safety, TTS,
telemetry, and controller behavior boundary.

## Read-Only Commands Used

```powershell
git status --short
rg --files
Get-ChildItem -LiteralPath docs -Recurse -File | Select-Object -ExpandProperty FullName
rg -n "language|locale|tone|voice|tts|provider|narration|alias|question" README.md src packages profiles docs\agent-handoffs docs\superpowers\specs docs\superpowers\plans
Get-Content -LiteralPath docs\agent-handoffs\cycle-008-demand-analysis.md
Get-Content -LiteralPath docs\agent-handoffs\cycle-008-summary.md
Get-Content -LiteralPath docs\superpowers\specs\2026-05-16-localized-qa-aliases-design.md
rg -n "PresenterVoiceSettings|language:|tone:|Language|Tone|literal|Literal|supported|voice\.language|voice\.tone|localized|localizedText|localizedQuestions|localizedAnswers|questionAliases|narration" src tests packages profiles README.md docs\agent-handoffs docs\superpowers\specs docs\superpowers\plans
Get-Content -LiteralPath src\ai_presenter\runtime\voice.py
Get-Content -LiteralPath src\ai_presenter\runtime\controller.py
Get-Content -LiteralPath src\ai_presenter\runtime\narration.py
Get-Content -LiteralPath docs\superpowers\specs\2026-05-16-voice-language-tone-expansion-design.md
Get-Content -LiteralPath src\ai_presenter\runtime\controller_view_model.py
Get-Content -LiteralPath src\ai_presenter\runtime\factory.py
Get-Content -LiteralPath tests\unit\test_controller_view_model.py
Get-Content -LiteralPath src\ai_presenter\cli.py
Get-Content -LiteralPath src\ai_presenter\providers\windows_speech.py
Get-Content -LiteralPath src\ai_presenter\providers\piper_provider.py
Get-Content -LiteralPath src\ai_presenter\providers\openai_provider.py
Get-Content -LiteralPath profiles\ringcentral-video-piper-speaker.yaml
Get-Content -LiteralPath profiles\ringcentral-video-openai.example.yaml
Select-String -Path README.md -Pattern "controller|language|tone|Piper|OpenAI|speech|provider|profile" -Context 2,2
Get-Content -LiteralPath docs\superpowers\specs\2026-05-15-controller-app-selection-questions-design.md
Get-Content -LiteralPath docs\superpowers\specs\2026-05-15-piper-tts-design.md
Get-Content -LiteralPath docs\superpowers\specs\2026-05-15-native-chinese-narration-design.md
Get-Content -LiteralPath tests\unit\test_voice.py
Get-Content -LiteralPath src\ai_presenter\runtime\questions.py
Get-Content -LiteralPath src\ai_presenter\packages\models.py
Select-String -Path packages\ringcentral-video.yaml -Pattern "questionAliases:|localizedQuestions:|localizedAnswers:|localizedText:|demoFlows:|qa:" -Context 1,4
Get-Content -LiteralPath docs\agent-handoffs\cycle-004-demand-analysis.md
Get-Content -LiteralPath docs\agent-handoffs\cycle-007-summary.md
Get-Content -LiteralPath docs\agent-handoffs\cycle-006-summary.md
Get-Content -LiteralPath docs\runbooks\ringcentral-manual-acceptance.md
Get-Content -LiteralPath docs\superpowers\plans\2026-05-16-voice-language-tone-expansion.md
Test-Path -LiteralPath docs\agent-handoffs\cycle-009-demand-analysis.md
```
