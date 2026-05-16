# Q&A Matcher Candidate Precompute Design

Date: 2026-05-16

## Goal

Reduce repeated per-question matcher work by precomputing stable package Q&A and entrypoint fallback candidates while preserving current matching behavior exactly.

## Context

`runtime/questions.py` currently expands localized Q&A questions and tokenizes Q&A and entrypoint fields during each `answer_question()` call. That is acceptable for small packages but creates unnecessary repeated work during live controller use, where operators may ask several questions against the same loaded package.

`MaterialPackage` already owns private runtime indexes for entrypoint lookup, demo flow lookup, and normalized package-owned aliases. Extending that pattern keeps the optimization local and avoids global caches.

## Design

Add two runtime-only candidate types in `src/ai_presenter/packages/models.py`:

- `QuestionAnswerMatchCandidate`
- `EntrypointMatchCandidate`

Store them in `MaterialPackage` private attrs and expose read-only tuple properties. Build them during model validation from the already-validated package content.

Update `src/ai_presenter/runtime/questions.py`:

- `_match_qa()` consumes `package.qa_question_candidates`.
- `_match_qa()` still performs substring matching first, then token overlap fallback.
- `_match_entrypoint()` consumes `package.entrypoint_match_candidates`.
- `_score_entrypoint_match()` consumes precomputed token sets.

The live query still gets normalized and tokenized per call.

## Behavior Contract

No user-visible behavior should change:

- Q&A match before entrypoint match.
- Package aliases before legacy aliases.
- Longest alias wins.
- First package order wins ties.
- Localized answers remain exact for `voice.language`.
- Tone rendering remains only for fallback answers.
- Risky `can_operate` logic remains unchanged.
- Logs remain privacy-safe.

## Serialization

Matcher candidates are runtime indexes only. They must not appear in `model_dump(by_alias=True)` and must not be encoded into package YAML.

## Testing

Add structural tests for candidate construction, order, identity, frozenset token fields, model dump non-leakage, and `with_demo_flow()` index rebuild identity.

Use existing `tests/unit/test_questions.py` as the main behavior regression suite.

Avoid wall-clock assertions.

## Out Of Scope

- No semantic search.
- No global or LRU caches.
- No package YAML changes.
- No answer text changes.
- No route safety policy changes.
- No acceptance evidence changes.
