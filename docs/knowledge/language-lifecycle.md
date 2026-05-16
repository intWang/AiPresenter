# AiPresenter Language Lifecycle

Date: 2026-05-16

This note defines the difference between package-local language coverage and runtime presenter support. It exists because a language can have package text, Q&A, and passing localization reports before AiPresenter can safely run or speak that language in a live demo.

## Lifecycle Gates

1. Package seed

   The package contains some language-specific text, such as `localizedText.es`, `localizedQuestions.es`, `localizedAnswers.es`, or `questionAliases.es`.

   Evidence:

   - `ai-presenter localization-report --package ringcentral-video --language es`
   - Focused package tests for the touched demo flow, Q&A, or aliases.

   Not evidence:

   - Runtime language support.
   - Voice availability.
   - Controller/demo acceptance for `--language es`.

2. Package localization complete

   Every required demo narration step, Q&A question, and Q&A answer has nonblank text for the language. Entrypoint aliases are still informational unless a cycle explicitly scopes alias expansion.

   Evidence:

   - `ai-presenter localization-report --package ringcentral-video --language <lang> --require-complete`

   Important boundary:

   - Passing this command means package content is complete.
   - It does not mean `demo --language <lang>` or `controller --language <lang>` is supported.

3. Diagnostics-ready package inspection

   `doctor --require-localization --localization-language <lang>` can inspect package text for languages that are not runtime presenter languages.

   Evidence:

   - The `localization` check reports package completeness or incompleteness.
   - The separate `runtime language support` check reports whether the presenter runtime accepts the same language.

   Important boundary:

   - A package-only language can have `[OK] localization` and `[FAIL] runtime language support` at the same time.

4. Runtime voice readiness

   A language becomes usable by the presenter runtime only after a separate promotion cycle owns the runtime surface:

   - presenter language normalization and labels;
   - voice/provider routing;
   - `voices` catalog behavior;
   - profiles or profile-compatible voice assets;
   - controller/demo language choices;
   - doctor and CLI tests;
   - documented setup and fallback behavior.

   Package-local text alone must not add the language to these surfaces.

5. Live acceptance

   A language is ready for live demos only after a manual or automated acceptance pass proves the selected profile, speech route, and RingCentral Video flow work together in the target environment.

   Evidence should live in the relevant runbook or RingCentral knowledge package, not only in localization tests.

## Current Spanish State

As of Cycle 128, Spanish is package-local complete, query-ready, and promoted
to a limited runtime presenter language for OpenAI-backed speech only:

- `localization-report --package ringcentral-video --language es --require-complete`
  reports `51/51` demo steps, `12/12` Q&A questions, and `12/12` Q&A answers.
- `questionAliases.es` is present on `26/27` RingCentral Video entrypoints with
  `69` aliases.
- Spanish package Q&A and package-owned aliases use Latin-diacritic-insensitive
  match keys, so unaccented prompts such as `Donde esta el menu de camara?`
  can still route to curated package knowledge.
- The normalizer strips combining marks only after Latin base characters using
  canonical decomposition. It must not be treated as Japanese width folding,
  transliteration, stemming, semantic matching, or provider compatibility.
- `doctor --require-localization --localization-language es` may inspect
  Spanish package content and should report `[OK] localization` plus `[OK]
  runtime language support`.
- `demo --language es` and `controller --language es` are supported only with
  OpenAI speech profiles, such as `profiles/ringcentral-video-openai.example.yaml`.
- Fake, Piper, `windows-sapi`, `windows-sapi-en`, and `windows-sapi-zh` profiles
  must reject Spanish with a profile voice compatibility error.
- Spanish local SAPI/Piper support and live RingCentral Video acceptance remain
  future work until a dated acceptance run proves them.

## Future Cycle Rules

- Use `--localization-language` for package coverage checks when the language may not be runtime-supported.
- Use `--language` for runtime presenter voice selection.
- Do not describe a language as runnable by the presenter, ready for voice output, ready for live demos, or accepted because package localization is complete.
- Do not describe package query routing as runtime language support. A supported
  runtime voice may answer a Spanish-looking prompt through package aliases, but
  that is not the same as `--language es`.
- Do not describe OpenAI-backed Spanish runtime support as local voice readiness
  or live RingCentral Video acceptance.
- Keep RingCentral UI labels literal inside localized narration when the user must find those labels in the product.
- Keep privacy and state-changing controls confirmation-bound in every language.
- Do not stage generated artifacts such as `.coverage` in language lifecycle or localization commits.
