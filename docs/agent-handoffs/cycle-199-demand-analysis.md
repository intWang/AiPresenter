# Cycle 199 Demand Analysis: CLI Voice Discoverability

Date: 2026-05-17

## Scope

Evaluate a narrow CLI discoverability improvement for `ai-presenter voices`
after the language/provider lifecycle matrix in
`docs/knowledge/language-lifecycle.md`.

The problem is not runtime support itself. The problem is operator
interpretation: the `voices` catalog can look like all listed languages are
ready for the selected environment, while language readiness has separate
layers:

- Runtime presenter choices selected by `--language`.
- Selected profile/provider compatibility checked with `--profile`.
- Local asset availability such as SAPI/Piper voices.
- Package localization checked separately by `localization-report` or
  `doctor --require-localization`.
- Live acceptance evidence recorded separately.

## User And Operator Value

Operators should be able to run `ai-presenter voices` and immediately
understand that the language list is the runtime choice catalog, not a promise
that every language is supported by their current profile, local machine, or
live RingCentral setup.

Operators using local profiles should not infer that Spanish or Japanese are
local SAPI/Piper-ready just because they appear in the runtime catalog. They
should know to run `ai-presenter voices --profile <profile>` or
`doctor --language <lang>` before a demo.

## Recommendation

Add a short `Language readiness:` section in `ai-presenter voices` output
immediately after the language alias catalog and before tones:

- `--language selects a runtime presenter voice.`
- `--profile checks speech provider compatibility and local voice assets.`
- `Package localization and live acceptance are separate checks.`

Keep the command compact, ASCII-safe, and aligned with the lifecycle matrix
without turning `voices` into a full diagnostics command.

## Acceptance Criteria

- `ai-presenter voices` still lists all runtime presenter language aliases and
  tone aliases.
- `ai-presenter voices` includes a concise `Language readiness:` section.
- The readiness section distinguishes runtime `--language` selection from
  `--profile` compatibility and local asset checks.
- The readiness section says package localization and live acceptance are
  separate checks.
- `ai-presenter voices --profile ringcentral-video-bind-speaker` still reports
  supported and unsupported languages for the local Windows SAPI profile.
- `ai-presenter voices --profile profiles/ringcentral-video-openai.example.yaml --language es`
  still reports Spanish supported via OpenAI.
- Output remains ASCII-safe for legacy Windows console rendering.
- Existing `demo`, `controller`, `doctor`, and `localization-report` behavior
  is unchanged.

## Non-Goals

- Do not add new runtime languages.
- Do not change provider routing or `validate_profile_voice(...)`.
- Do not add Spanish local SAPI/Piper support.
- Do not change package localization coverage, aliases, Q&A, demo flows, or
  lifecycle matrix semantics.
- Do not make `voices` load material packages or perform localization checks.
- Do not make `voices` create or record live acceptance evidence.
- Do not change privacy, safety, question routing, operation eligibility, or
  controller behavior.

## Privacy And Routing Constraints

`voices` should remain a metadata-only CLI surface. It may inspect the selected
profile and local voice assets, but it must not launch RingCentral, inspect
meeting content, run automation, send audio, call OpenAI, or collect
screenshots.

Local asset checks should stay limited to provider prerequisites such as
installed SAPI voices or Piper assets. They must not imply live demo readiness.
Live acceptance remains a separate dated evidence process in the RingCentral
runbook/knowledge docs.

## Verification

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests/unit/test_cli.py::test_voices_catalog_explains_language_readiness_boundaries tests/unit/test_cli.py::test_voices_catalog_output_is_ascii_safe_for_legacy_windows_console tests/unit/test_cli.py::test_voices_lists_language_tone_choices tests/unit/test_cli.py::test_voices_profile_reports_supported_and_unsupported_languages
git diff --check
```
