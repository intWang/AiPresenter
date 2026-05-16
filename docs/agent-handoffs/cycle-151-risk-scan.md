# Cycle 151 Risk Scan: Language Tone Alias Expansion Boundary

Date: 2026-05-17
Cycle: 151
Scope: documentation-only risk scan for future `tone`, `language`, and
alias expansion wording.
Do not modify source, tests, package YAML, generated artifacts, `.coverage`, or
acceptance evidence records for this task.

## Read Basis

- `docs/agent-handoffs/cycle-145-risk-scan.md`
- `docs/agent-handoffs/cycle-150-risk-scan.md`
- `docs/knowledge/language-lifecycle.md`
- `README.md`
- `src/ai_presenter/runtime/voice.py`
- `tests/unit/test_cli.py` around `voices`, `localization-report`,
  `entrypoints --language`, and `doctor --require-localization`

## Risk Summary

Language, tone, and alias additions sit close to runtime and acceptance
language, so they are easy places to overclaim. A new alias can mean only that
input normalization maps one spelling to an existing canonical value. A new
tone can mean only that narration text receives a different style instruction
or local prefix. A new package-local language key can mean only that package
text or metadata exists for inspection.

Those facts do not automatically prove provider compatibility, profile
support, local SAPI voice availability, Piper model availability, controller or
demo execution, RingCentral acceptance, or complete product localization.

The current Spanish state is a useful model: Spanish package localization is
complete for required demo and Q&A text and Spanish is a limited runtime
presenter language only for OpenAI-backed speech. Fake, Piper, `windows-sapi`,
`windows-sapi-en`, and `windows-sapi-zh` profiles still reject Spanish. Spanish
local SAPI/Piper support and live RingCentral Video acceptance remain future
work until separately implemented and recorded.

## No-Go Claims

Do not claim or imply:

- Adding a language alias means the speech provider supports that language.
- Adding a language label means profiles can run demos or controllers in that
  language.
- Adding package text, Q&A, display metadata, or aliases means runtime presenter
  language support exists.
- Passing `localization-report --require-complete` means voice output is ready.
- Passing package-local inspection means local SAPI or Piper assets are ready.
- `voices` listing a language or tone means every profile supports it.
- `voices --profile ... --language ...` success is live RingCentral acceptance.
- OpenAI-backed runtime support means local SAPI/Piper readiness.
- OpenAI-backed runtime support means live RingCentral Video acceptance.
- A tone alias such as `warm`, `mentor`, `executive`, `calm`, or `privacy`
  creates provider support or changes profile compatibility.
- `entrypoints --language <lang>` validates runtime voices, matcher expansion,
  provider routing, or live behavior.
- Optional `localizedTitles.<lang>` or `localizedPurposes.<lang>` coverage means
  the language is fully localized.
- Package query routing through aliases is equivalent to `demo --language
  <lang>` or `controller --language <lang>` support.
- Runtime language support proves translated RingCentral UI labels, complete
  local product localization, privacy-safe live behavior, or accepted cleanup.
- Doctor output, CLI guards, or unit tests create a dated acceptance record.

Avoid wording such as `ready for Spanish`, `fully localized`, `provider-ready`,
`SAPI supported`, `Piper supported`, `accepted live`, `validated in
RingCentral`, `all profiles support`, or `alias unlocks runtime support` unless
the sentence names the exact scoped evidence and excludes broader readiness.

## Safe Wording

Preferred language:

- "The alias normalizes user input to the canonical presenter language or tone."
- "The language key is available for package-local inspection."
- "`localization-report --require-complete` confirms required package text
  coverage only."
- "`entrypoints --language <lang>` reports display-source labels; it does not
  inspect runtime voice routes."
- "`voices` lists canonical languages, tones, and aliases separately from
  per-profile compatibility."
- "`voices --profile ... --language ...` checks the selected profile's voice
  route; it is not live RingCentral acceptance."
- "`doctor --require-localization --localization-language <lang>` separates
  package localization from runtime language support."
- "A package-only language can have `[OK] localization` and `[FAIL] runtime
  language support` at the same time."
- "Spanish runtime presenter support is currently limited to OpenAI-backed
  speech profiles."
- "Spanish local SAPI/Piper support and live RingCentral Video acceptance remain
  future work until a separate implementation and dated acceptance record prove
  them."

Use narrow verbs such as `normalizes`, `lists`, `reports`, `inspects`, and
`checks`. Reserve `supports`, `ready`, `accepted`, and `validated` for sentences
that identify the exact provider, profile, command, and evidence source.

## Test Risk

Risk is medium-high when tests use positive labels such as `supported` without
pinning the surface being tested.

Safe test assertions:

- `voices` catalog output can assert that language and tone aliases are listed.
- `voices --profile ringcentral-video` can assert unsupported languages for the
  fake provider.
- `voices --profile profiles/ringcentral-video-openai.example.yaml --language
  es` can assert selected voice support via `openai` only.
- `entrypoints --language Spanish` and `entrypoints --language es-MX` can assert
  `Language: es` plus localized/fallback display markers.
- `entrypoints --language` should keep tests that fail if runtime voice
  resolution, profile validation, provider routing, or asset checks are called.
- `localization-report --language de` can assert unknown package-only keys stay
  raw and do not raise `Unsupported presenter language`.
- `doctor --require-localization --localization-language de` can assert package
  localization passes while runtime language support fails.
- Documentation guard tests can assert the presence of boundary wording such as
  `not evidence of runtime Spanish readiness`, `provider availability`,
  `provider compatibility`, and `live RingCentral Video acceptance`.

No-go test assertions:

- Do not assert that adding an alias makes a language runtime-selectable.
- Do not use `Localization coverage incomplete` absence as proof of full
  product localization.
- Do not use `Selected voice supported via openai` as proof of local SAPI/Piper
  readiness.
- Do not relax Spanish rejection for fake, Piper, `windows-sapi`,
  `windows-sapi-en`, or `windows-sapi-zh` profiles without a scoped promotion.
- Do not add live RingCentral automation, screenshots, provider calls, SAPI
  inspection, Piper downloads, or acceptance-run updates to alias or wording
  tests.
- Do not assert broad negatives such as no `fallback`, no `unknown`, no
  `unsupported`, or no `runtime` in docs or CLI output. Those terms are useful
  boundary markers.

The most subtle failure mode is a test name or assertion that celebrates an
alias as "support." Prefer names that include the surface, such as package key
resolution, catalog listing, profile voice compatibility, or live acceptance.

## Go/No-Go Recommendation

Go for narrow additions that keep each surface explicit:

- aliases normalize input;
- tones change instruction style;
- package-local language keys inspect package content;
- profile checks decide runtime voice compatibility;
- asset checks decide local SAPI/Piper readiness;
- dated acceptance records decide live RingCentral acceptance.

No-go if wording or tests collapse those gates into one success state. No-go if
new language or alias copy implies provider support, runtime readiness, local
voice asset availability, live RingCentral acceptance, or complete local
product localization without separate scoped evidence.

The safe success state is modest and clear: future language, tone, and alias
work may improve discoverability and package inspection while preserving the
line between text coverage, runtime voice support, local asset readiness, and
live acceptance.
