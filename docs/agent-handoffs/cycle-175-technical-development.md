# Cycle 175 Technical Development: Chinese Presenter Meta Guard

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`
Role: Cycle175 technical-development handoff

## Scope And Boundary

This handoff documents the current Cycle175 implementation diff. Per assignment, this pass writes only:

- `docs/agent-handoffs/cycle-175-technical-development.md`

No source, test, package YAML, staging, or commit changes were made by this handoff. The workspace already contained Cycle175 source/test edits plus a dirty `.coverage` file before this doc was written.

## Problem

Cycle174 separated English Presenter expression requests from RingCentralVideo control routing. Prompts like `Answer in Chinese`, `Be more concise`, or `Make the presenter friendlier` became answer-only Presenter settings guidance instead of fuzzy matching to app controls.

The remaining gap was the same user intent expressed in Chinese. A Chinese user can ask AiPresenter to answer in Chinese, speak more slowly, be more concise, use a friendlier or more careful tone, or explain from a beginner level. Those pure Presenter meta requests should not open, operate, or route to RingCentralVideo controls.

The tricky part is that Chinese meta modifiers can also prefix real RingCentralVideo questions. For example, a prompt can ask for a careful tone while asking whether meeting information shows encryption status. The matcher must keep safety Q&A and explicit app intents intact while preventing pure style/language prompts from falling into broad route fallback.

## Implementation Summary

The current Cycle175 diff updates `src/ai_presenter/runtime/questions.py` in three narrow places:

- Extends `_PRESENTER_META_REQUEST_FRAGMENTS` with high-confidence Chinese phrase fragments for language, tone, pacing, concision, simplicity, and beginner guidance.
- Adds `_match_contained_qa_question(...)` and calls it inside `_match_qa(...)` after existing safety-specific Q&A helpers and before meeting-info/title/package-alias guards.
- Adds bare Chinese safety/status words to `_BROAD_QA_FRAGMENT_TOKENS` so one-word prompts such as `安全`, `隐私`, `状态`, and `确认` do not match broad Q&A fragments.

The tests in `tests/unit/test_questions.py` add focused coverage for:

- pure Chinese Presenter meta requests staying answer-only and no-interrupt;
- Chinese meta modifiers preserving meeting-info privacy, encryption status, host-controls, notes safety, Chat, and Network quality behavior;
- bare Chinese safety/status words not becoming Presenter meta or encryption/security answers;
- mojibake Chinese meta text not matching the new guard.

## Files Touched

Current Cycle175 working diff before this handoff:

- `src/ai_presenter/runtime/questions.py` - matcher implementation.
- `tests/unit/test_questions.py` - focused regression tests.
- `.coverage` - dirty binary coverage artifact already present in the working tree; not part of the matcher logic.

Handoff docs already present:

- `docs/agent-handoffs/cycle-175-demand-analysis.md`
- `docs/agent-handoffs/cycle-175-experience.md` - appeared during this handoff's final boundary check and was read, not modified.
- `docs/agent-handoffs/cycle-175-risk-scan.md`
- `docs/agent-handoffs/cycle-175-technical-scan.md`

This pass changed only:

- `docs/agent-handoffs/cycle-175-technical-development.md`

## Exact Matcher Behavior

`_answer_question(...)` still follows the established route order:

1. Normalize the user prompt with `normalize_question_prompt(...)`.
2. Run `_match_qa(...)`.
3. If Q&A matches, return the Q&A answer and its related entrypoint/can-operate state.
4. Check `_is_presenter_meta_request(...)`.
5. For meta prompts, use `_match_explicit_entrypoint(...)` only.
6. For non-meta prompts, use full `_match_entrypoint(...)`.
7. If no entrypoint matches and the prompt is meta, return the existing `Presenter settings:` answer with no `entrypoint_id` and `can_operate=False`.

The new Chinese Presenter meta fragments are phrase-level only:

- `可以用中文说吗`
- `能用中文说吗`
- `我是初学者`
- `我是新手`
- `用中文回答`
- `用友好的语气回答`
- `用谨慎的语气回答`
- `请讲中文`
- `请讲慢一点`
- `请讲简单一点`
- `请说中文`
- `请说慢一点`
- `请用中文回答`
- `请用更友好的语气回答`
- `请用谨慎的语气回答`
- `请简洁一点`
- `解释慢一点`
- `从基础讲起`
- `回答简洁一点`

The implementation does not add bare triggers such as `中文`, `语气`, `简单`, `新手`, `安全`, `隐私`, `状态`, or `确认` to the Presenter meta fragment list.

Contained Q&A matching now runs before alias guards in `_match_qa(...)`. It returns a Q&A item when a candidate's normalized authored question is contained inside the longer user prompt, is not exactly equal to the whole prompt, and passes `_is_specific_question_fragment(...)`. Specific means at least two meaningful Latin tokens or CJK text with length at least six. This protects prefixed localized Q&A such as a Chinese encryption-status question with a tone modifier before a package alias like meeting information can stop Q&A matching.

Bare Chinese safety/status words are now broad QA fragment blockers:

- `安全`
- `状态`
- `确认`
- `隐私`

When one of those words is the whole normalized question, `_can_match_qa_fragment(...)` returns `False`, preventing broad fragment matching to security/privacy Q&A. They still do not become Presenter meta prompts.

## Why Route Order Is Safe

Q&A-first remains the primary safety boundary. Exact Q&A, recording safety, notes/transcript safety, and meeting-info privacy still run before the Presenter meta guard.

The contained-QA step is placed inside `_match_qa(...)`, before meeting-info location, title, and package-alias guards. That is safe because it only accepts authored Q&A candidates that are fully contained in the user prompt and specific enough to avoid one-word CJK matches.

Meta prompts do not use broad token fallback. Once `_is_presenter_meta_request(...)` is true, `_answer_question(...)` calls `_match_explicit_entrypoint(...)`, which can still preserve explicit RingCentralVideo intent through package aliases, meeting-info location lookup, or entrypoint titles. If none of those explicit routes match, the prompt returns the non-operable Presenter settings answer.

This means pure style/language requests do not operate the meeting UI, while mixed prompts that mention real app surfaces still route through Q&A or explicit entrypoint matching.

## Verification

Focused verification run by this handoff:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -B -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests\unit\test_questions.py::test_chinese_presenter_meta_requests_do_not_route_to_ringcentral_controls tests\unit\test_questions.py::test_chinese_presenter_meta_modifiers_do_not_steal_ringcentral_intents tests\unit\test_questions.py::test_chinese_bare_safety_words_do_not_match_presenter_meta_or_security tests\unit\test_questions.py::test_chinese_presenter_meta_mojibake_does_not_match
```

Result:

```text
17 passed in 4.47s
```

Status check before writing this doc still showed only the pre-existing implementation/coverage/docs state:

```text
 M .coverage
 M src/ai_presenter/runtime/questions.py
 M tests/unit/test_questions.py
?? docs/agent-handoffs/cycle-175-demand-analysis.md
?? docs/agent-handoffs/cycle-175-risk-scan.md
?? docs/agent-handoffs/cycle-175-technical-scan.md
```

No broader unit suite, ruff check, package diagnostics, or live RingCentral acceptance was run by this handoff.

## Known Limits And Future Work

- The Presenter meta response remains the existing English `Presenter settings:` text rendered through current voice text handling. This slice does not implement persistent language, tone, pacing, or guidance-depth state changes.
- The Chinese fragment list is intentionally conservative. Additional natural phrases such as English-language requests written in Chinese can be added later only with negative tests for meeting-info privacy, security, Chat, Participants, notes/transcript, recording, invite, share, and leave behavior.
- The contained-QA matcher is generic and depends on authored Q&A specificity. Future package growth should keep Q&A prompts specific and review any new short CJK Q&A prompts carefully.
- Bare safety/status words are blocked only for broad Q&A fragment matching. They still fall through to the normal no-match answer unless future UX work designs clarification prompts.
- Mojibake is still rejected rather than repaired. Do not add mojibake variants as supported phrases.
- `.coverage` remains dirty in the working tree and should not be staged unless a later owner intentionally refreshes coverage.

## Status

Status: Cycle175 technical-development handoff complete. The current implementation is documented, focused tests passed, and no source/tests were modified by this handoff.

Changed file path:

- `docs/agent-handoffs/cycle-175-technical-development.md`
