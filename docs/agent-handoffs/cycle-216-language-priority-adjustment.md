# Cycle 216 Language Priority Adjustment

Date: 2026-05-18
Cycle: 216
Role: User-directed roadmap correction

## User Direction

French is not a priority support direction. Future optimization should focus on
deepening Chinese and English.

## Decision

- Treat English and Chinese as the active optimization priority.
- Keep the existing French package-local seed as boundary coverage only.
- Do not continue French Q&A, narration, alias, or runtime promotion work by
  default.
- Reopen French only when the user explicitly asks for it.

## Preferred Next Slices

- Chinese question input and answer quality for high-frequency RingCentral
  Video prompts.
- Authored Chinese safety Q&A parity with English for privacy-sensitive
  surfaces.
- English narration polish and operator-facing copy for RingCentral demos.
- Chinese voice readiness and live acceptance evidence for the supported
  OpenAI and Windows SAPI paths.

## Verification Anchor

`tests/unit/test_material_packages.py::test_language_lifecycle_prioritizes_english_and_chinese_over_french`
guards this roadmap statement in `docs/knowledge/language-lifecycle.md`.
