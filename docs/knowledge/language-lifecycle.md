# AiPresenter Language Lifecycle

Date: 2026-05-16

This note defines the difference between package-local language coverage and runtime presenter support. It exists because a language can have package text, Q&A, and passing localization reports before AiPresenter can safely run or speak that language in a live demo.

## Current Language State Matrix

This matrix separates package-localization complete status, runtime presenter
language support, provider compatibility, local voice assets, and live
acceptance evidence. `--localization-language` checks package text;
`--language` selects runtime presenter voice.

| Runtime key | Label | Aliases | Package localization state | Runtime presenter language | Provider compatibility | Local voice assets | Live acceptance evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `en` | English | `en`, `en-us`, `en-gb`, `english` | RingCentral source language and fallback package text. | English is the default runtime voice language. | Supports normal configured speech routes; direct `windows-sapi-zh` resolves back to `windows-sapi-en`. | Piper and English SAPI assets are local-profile dependent. | Live acceptance requires a dated acceptance run for the selected profile, speech route, flow, environment, result, cleanup, and privacy notes. |
| `zh` | Chinese | `zh`, `zh-cn`, `zh-hans`, `zh-tw`, `zh-hant`, `chinese`, `中文` | RingCentral required package localization is package-localization complete for demo narration and Q&A. | Runtime presenter language supported. | Chinese can use OpenAI speech or `windows-sapi-zh`; local fallback routes `piper`, `windows-sapi`, and `windows-sapi-en` to `windows-sapi-zh`. | `windows-sapi-zh` still depends on an installed compatible Chinese SAPI voice such as Huihui. | Live acceptance requires a dated acceptance run before claiming Chinese live readiness. |
| `ja` | Japanese | `ja`, `ja-jp`, `japanese`, `日本語` | RingCentral required package localization is package-localization complete for demo narration and Q&A. | Runtime presenter language supported. | Japanese requires OpenAI speech. | Local SAPI/Piper Japanese remains future work unless a later provider slice implements and tests it. | Live acceptance requires a dated acceptance run before claiming Japanese live readiness. |
| `es` | Spanish | `es`, `es-es`, `es-mx`, `es-419`, `es-la`, `spanish`, `latam-spanish`, `latin-american-spanish`, `español`, `espanol` | RingCentral required package localization is package-localization complete for demo narration and Q&A; optional entrypoint display metadata remains partial. | Runtime presenter language supported. | Spanish requires OpenAI speech. | local SAPI/Piper Spanish remains future work; local fake, Piper, and Windows SAPI profiles must reject `--language es`. | Spanish runtime support is not live RingCentral acceptance; live acceptance requires a dated acceptance run. |
| `fr` package seed | French | `fr` as a package-local lookup key only. | French package-local seed covers `meeting-basics-demo` and `vbg-blur-demo` narration plus one background privacy Q&A; required package localization is incomplete. | French remains package-only; presenter runtime does not support `--language fr`. | Provider compatibility is absent until a separate runtime promotion cycle. | Voice assets are absent until a provider slice adds and tests them. | Package-local French text is never live acceptance evidence. |
| package-only future key | Not a runtime label | Raw package key, for example `de`, when it is not a known presenter language alias. | May be package-localization complete through package text and `localization-report --require-complete`. | Not a runtime presenter language until `voice.py`, CLI checks, providers, tests, and docs are promoted together. | Provider compatibility is absent until runtime support exists. | Voice assets are absent until a provider slice adds and tests them. | Package-only text is never live acceptance evidence. |

## Lifecycle Gates

1. Package seed

   The package contains some language-specific text, such as
   `localizedText.es`, `localizedQuestions.es`, `localizedAnswers.es`,
   `questionAliases.es`, `localizedTitles.es`, or `localizedPurposes.es`.

   Evidence:

   - `ai-presenter localization-report --package ringcentral-video --language es`
   - Focused package tests for the touched demo flow, Q&A, aliases, or
     entrypoint display metadata.

   Not evidence:

   - Runtime language support.
   - Voice availability.
   - Controller/demo acceptance for `--language es`.

2. Package localization complete

   Every required demo narration step, Q&A question, and Q&A answer has nonblank text for the language. Entrypoint aliases and localized entrypoint display metadata are still informational unless a cycle explicitly scopes them.

   Evidence:

   - `ai-presenter localization-report --package ringcentral-video --language <lang> --require-complete`

   Important boundary:

   - Passing this command means required package localization is complete.
   - It does not mean `demo --language <lang>` or `controller --language <lang>` is supported.
   - Optional `localizedTitles.<lang>` and `localizedPurposes.<lang>` counts
     in `localization-report` are author diagnostics only. They are not part of
     `--require-complete`.

3. Entrypoint display metadata inspection

   `localizedTitles.<lang>` and `localizedPurposes.<lang>` are optional
   package-local display metadata for entrypoint answer rendering and
   inspection. They are useful when localized answers need a localized
   entrypoint name or purpose line.

   They do not affect:

   - matching candidates;
   - alias ordering;
   - Q&A precedence;
   - safety gating;
   - controller interrupts;
   - provider routing;
   - voice assets;
   - live acceptance.

   Evidence:

   - `ai-presenter entrypoints --package ringcentral-video --language <lang>`

   For Spanish inputs such as `es`, `Spanish`, and `es-MX`, the command
   displays `Language: es`. Each entrypoint line marks the title source with
   `(title: localized)` or `(title: fallback)`, and the following `purpose:`
   line ends in `(localized)` or `(fallback)`.

   Important boundary:

   - `entrypoints --language <lang>` is package-local inspection. For known presenter
     language aliases such as `Spanish`, `es-MX`, and `zh-CN`, the command
     normalizes to canonical package keys before package-local inspection.
   - `localization-report --language <lang>` uses the same package-local
     language key resolution.
   - Unknown package-only keys remain raw package metadata lookup keys, so
     future package-local languages are not blocked by runtime voice support.
   - The command prints `Language: <key>` using the resolved package key.
   - `localized` source markers mean nonblank package-local display copy was
     found for that field.
   - `fallback` source markers mean canonical title or purpose copy was shown.
   - These markers are display-source labels only. They are not evidence of
     runtime Spanish readiness, matcher expansion, provider compatibility,
     voice asset availability, controller/demo execution, or live RingCentral
     Video acceptance.

4. Diagnostics-ready package inspection

   `doctor --require-localization --localization-language <lang>` can inspect package text for languages that are not runtime presenter languages.

   Evidence:

   - The `localization` check reports package completeness or incompleteness.
   - The separate `runtime language support` check reports whether the presenter runtime accepts the same language.

   Important boundary:

   - A package-only language can have `[OK] localization` and `[FAIL] runtime language support` at the same time.

5. Runtime voice readiness

   A language becomes usable by the presenter runtime only after a separate promotion cycle owns the runtime surface:

   - presenter language normalization and labels;
   - voice/provider routing;
   - `voices` catalog behavior;
   - profiles or profile-compatible voice assets;
   - controller/demo language choices;
   - doctor and CLI tests;
   - documented setup and fallback behavior.

   Package-local text alone must not add the language to these surfaces.

6. Live acceptance

   A language is ready for live demos only after a manual or automated acceptance pass proves the selected profile, speech route, and RingCentral Video flow work together in the target environment.

   Evidence should live in the relevant runbook or RingCentral knowledge package, not only in localization tests.

## Current Spanish State

As of 2026-05-16, Spanish is required-package-localization complete,
query-ready, and promoted to a limited runtime presenter language for
OpenAI-backed speech only:

- `localization-report --package ringcentral-video --language es --require-complete`
  reports `51/51` demo steps, `16/16` Q&A questions, and `16/16` Q&A answers.
- `questionAliases.es` is present on `26/27` RingCentral Video entrypoints with
  `69` aliases.
- Optional entrypoint display metadata is partial:
  `localizedTitles.es` is present on `8/27` entrypoints and
  `localizedPurposes.es` is present on `8/27` entrypoints.
- Spanish package Q&A and package-owned aliases use Latin-diacritic-insensitive
  match keys, so unaccented prompts such as `Donde esta el menu de camara?`
  can still route to curated package knowledge.
- The normalizer strips combining marks only after Latin base characters using
  canonical decomposition. It must not be treated as Japanese width folding,
  transliteration, stemming, semantic matching, or provider compatibility.
- `doctor --require-localization --localization-language es` may inspect
  Spanish package content independently from runtime voice checks. The
  `runtime language support` check can report `[OK]` because the presenter
  runtime recognizes `es`; profile/provider compatibility is checked separately
  when `--language es` selects a Spanish runtime voice.
- `demo --language es` and `controller --language es` are supported only with
  OpenAI speech profiles, such as `profiles/ringcentral-video-openai.example.yaml`.
- Fake, Piper, `windows-sapi`, `windows-sapi-en`, and `windows-sapi-zh` profiles
  must reject Spanish with a profile voice compatibility error.
- Spanish local SAPI/Piper support and live RingCentral Video acceptance remain
  future work until a dated acceptance run proves them.

## Current French State

As of 2026-05-17, French is a French package-local seed, not a runtime
presenter language:

- `localization-report --package ringcentral-video --language fr` reports
  `7/51` demo steps, `1/16` Q&A questions, and `1/16` Q&A answers.
- The seeded flows are `meeting-basics-demo`, covering microphone,
  participants, and chat narration, plus `vbg-blur-demo`, covering Settings,
  Background, Blur, and Stop video narration for background privacy.
- The seeded Q&A is the background privacy answer for Settings, Background, and
  Blur.
- `questionAliases.fr` is present on `1/27` RingCentral Video entrypoints with
  `2` aliases.
- `localization-report --package ringcentral-video --language fr --require-complete`
  must fail until every required demo narration step, Q&A question, and Q&A
  answer has French text.
- French remains package-only: the presenter runtime does not support
  `--language fr`, and `demo --language fr` or `controller --language fr` must
  reject before runtime starts.
- French package text is not OpenAI speech readiness, local voice asset
  readiness, provider compatibility, query readiness for all RingCentral
  surfaces, or live RingCentral acceptance.

## Future Cycle Rules

- Use `--localization-language` for package coverage checks when the language may not be runtime-supported.
- Use `--language` for runtime presenter voice selection.
- Do not describe a language as runnable by the presenter, ready for voice output, ready for live demos, or accepted because package localization is complete.
- Do not describe Spanish as fully localized across entrypoints while
  `localizedTitles.es` and `localizedPurposes.es` are partial.
- Do not describe Spanish local SAPI/Piper, voice assets, or live RingCentral
  Video acceptance as ready without a separate implementation and dated
  acceptance record.
- Do not describe package query routing as runtime language support. A supported
  runtime voice may answer a Spanish-looking prompt through package aliases, but
  that is not the same as `--language es`.
- Do not describe OpenAI-backed Spanish runtime support as local voice readiness
  or live RingCentral Video acceptance.
- Keep RingCentral UI labels literal inside localized narration when the user must find those labels in the product.
- Keep privacy and state-changing controls confirmation-bound in every language.
- Do not stage generated artifacts such as `.coverage` in language lifecycle or localization commits.
