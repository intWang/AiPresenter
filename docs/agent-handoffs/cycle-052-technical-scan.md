# Cycle 052 Technical Scan

## Selected Slice

Centralize Q&A prompt normalization at package-index build time and reuse that normalized key in runtime matching and diagnostics.

## Touchpoints

- `MaterialPackage._build_qa_question_candidates()` builds runtime Q&A candidates.
- `MaterialPackage.qa_questions_by_normalized` powers exact Q&A lookup.
- `answer_question()` currently normalizes user input before `_match_qa()`.
- Duplicate Q&A and Q&A/alias overlap diagnostics consume `candidate.normalized_question`.

## Implementation Shape

- Add `normalize_question_prompt(text)` returning `text.strip().casefold()`.
- Use it for every Q&A candidate normalized key.
- Skip candidates whose normalized prompt is blank.
- Use the same helper for runtime user-question normalization.
- Let `qa alias overlap` group by `candidate.normalized_question`; remove its one-off local normalizer.

## Edge Cases

- Preserve raw `QuestionAnswerMatchCandidate.question` for labels and language detection.
- Do not de-duplicate nonblank same-item prompts.
- Preserve first-declared exact Q&A winner through `setdefault`.
- Keep localization status item-based, not runtime-prompt-based.
