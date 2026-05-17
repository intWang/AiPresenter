# Cycle 171 Final Matcher Review

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`
Role: Cycle171 final matcher review

## Scope

Reviewed the dirty diff for the Cycle171 matcher changes after the plain
`meeting information` prompt was swallowed by Meeting information privacy Q&A.

This pass wrote only:

- `docs/agent-handoffs/cycle-171-final-review.md`

This pass did not edit code, tests, package YAML, `.coverage`, staging, or
commits. The pre-existing dirty tree, including the deleted `.coverage`, was
left untouched.

## Verdict

Blocking finding found.

The early `_match_package_entrypoint_alias(package, normalized_question)` guard
does preserve exact package entrypoint aliases such as `meeting information`.
However, because it now runs before fragment and reverse-substring Q&A matching,
it also blocks natural prefixed variants of the newly added sensitive prompts.
Those variants fall through to the generic answer-only entrypoint response
instead of the privacy Q&A.

## Blocking Findings

### P1: Prefixed sensitive Meeting information requests bypass privacy Q&A

Location:

- `src/ai_presenter/runtime/questions.py:318`
- `src/ai_presenter/runtime/questions.py:321`
- `src/ai_presenter/runtime/questions.py:328`
- `packages/ringcentral-video.yaml:1753`

The moved package-alias guard now returns `None` from `_match_qa` before the
candidate loop can evaluate Q&A prompts such as `Read meeting information
aloud`, `Copy meeting information`, and `Share meeting details`.

That fixes the bare alias `meeting information`, but it creates a regression
for common polite/prefixed forms that contain the same alias:

| Prompt | Current result |
| --- | --- |
| `Copy meeting information` | Meeting information privacy Q&A |
| `Could you copy meeting information?` | generic `Meeting information:` entrypoint answer |
| `Please share meeting details` | generic `Meeting information:` entrypoint answer |
| `Can you read meeting information aloud?` | generic `Meeting information:` entrypoint answer |

These prompts remain non-operable and do not expose exact URLs or IDs today,
but they no longer receive the safety copy that says AiPresenter should not
copy, read aloud, or expose meeting IDs, links, dial-in details, or host
information without explicit verified content. This is exactly the class of
action-like sensitive forms added in the package diff, so the final matcher
should not rely on exact-prompt phrasing only.

Suggested fix direction: keep exact package aliases routing to entrypoint
answers, but allow privacy/safety Q&A prompts related to the same entrypoint to
match when the user prompt contains action/context words around the alias. One
way is to move the package-alias guard after an allowlisted safety-Q&A candidate
pass, or make the guard ignore related-entrypoint Q&A candidates that contain
action verbs like read/copy/share.

Suggested regression coverage:

- `Could you copy meeting information?`
- `Please share meeting details`
- `Can you read meeting information aloud?`
- `Could you copy the meeting link?`

Expected: route to `ringcentral.video.top.meeting-info`, `can_operate is
False`, no interrupt, privacy Q&A wording, no `Meeting information:` fallback,
no exact URL/domain/sample ID, and no copied/read/shared outcome claim.

## Non-blocking Findings

### P3: `Share status` and `Share security` are tested but not package prompts

Location:

- `tests/unit/test_questions.py:855`
- `packages/ringcentral-video.yaml:1797`

The test matrix expects `Share status` and `Share security` to route to the
encryption-status Q&A, but the YAML adds `Share secure` and `Share verify`, not
those exact two prompts. The current route works through token overlap, not an
explicit package prompt. That is acceptable for the current matcher, but it is
fragile: another Q&A item with `share` plus a status/security token could
change the best-match result later.

Suggested hardening: either add exact package prompts for `Share status` and
`Share security`, or make the test clearly document that these are intentional
token-overlap cases.

### P3: Broad-token guard only protects exact bare words

Location:

- `src/ai_presenter/runtime/questions.py:42`
- `src/ai_presenter/runtime/questions.py:513`

`_BROAD_QA_FRAGMENT_TOKENS` blocks exact bare `secure`, `security`, `status`,
and `verify` on the fragment path. That is enough for the current failing class
because token-overlap matching still requires two overlapping meaningful
tokens, and there are no exact one-word Q&A prompts for those words.

Future one-word Q&A prompts would bypass this guard through the exact-match map
at `src/ai_presenter/runtime/questions.py:303`. That may be intentional, but
it is worth documenting if one-word Q&A prompts are ever introduced.

## Reviewed Diff

- `src/ai_presenter/runtime/questions.py`
  - Adds `_BROAD_QA_FRAGMENT_TOKENS = {"secure", "security", "status", "verify"}`.
  - Moves the package entrypoint alias guard before fragment Q&A matching.
  - Rejects exact broad bare words from Q&A fragment matching.
- `packages/ringcentral-video.yaml`
  - Adds Meeting information privacy prompts for read/copy/share
    information/details forms.
  - Adds encryption-status prompts for share/copy secure/verify/status/security
    forms.
- `tests/unit/test_questions.py`
  - Adds exact privacy prompt coverage, bare broad-word no-match coverage, and
    encryption-status action prompt coverage.
- `tests/unit/test_cli.py` and `tests/unit/test_diagnostics.py`
  - Update Q&A prompt-count expectations from `200` to `212`.

## Verification

I did not rerun pytest because the requested scope was review plus this one doc
write, and the user already reported focused verification as:

- `meeting_info_privacy_questions_are_answer_only`
- `english_meeting_info_privacy_questions_stay_qa_first`
- `bare_status_words`
- `encryption_status`
- Result: `62 passed in 12.32s`

Read-only probes were run with `PYTHONDONTWRITEBYTECODE=1`, `python -B`, and
`PYTHONPATH=src` through the existing `.venv`. They confirmed:

- `meeting information` now routes to the generic `Meeting information:`
  entrypoint answer.
- Exact `Copy meeting information` routes to the privacy Q&A.
- Prefixed variants like `Could you copy meeting information?`,
  `Please share meeting details`, and `Can you read meeting information aloud?`
  route to the generic `Meeting information:` entrypoint answer.
- `Please copy status`, `Could you copy status?`, and `Can you share secure?`
  route to the encryption-status Q&A.

## Status

Blocking status: one blocking matcher regression remains.

Doc path:

- `docs/agent-handoffs/cycle-171-final-review.md`
