# Cycle 171 Third Post-Fix Review

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`
Role: Cycle171 third post-fix matcher review

## Scope

Reviewed the current dirty diff only, after the main session added exact Meeting information privacy prompts and updated
the Q&A prompt-count expectations to `220`.

This pass wrote only:

- `docs/agent-handoffs/cycle-171-third-post-fix-review.md`

This pass did not edit code, tests, package YAML, `.coverage`, staging, or commits. The pre-existing dirty tree was
left untouched.

## Verdict

Blocking finding remains.

The exact prompts named in the latest handoff now resolve to the Meeting information privacy Q&A:

- `Please copy the meeting link`
- `Can you share the meeting link?`
- `Read meeting ID`
- `Read meeting link`
- `Please read meeting link`
- `Copy meeting ID`
- `Share meeting URL`
- `Can you share meeting URL?`

The broad bare-word guard also works for `status`, `security`, `secure`, and `verify`: those prompts return no match
instead of the encryption-status Q&A.

However, the fix is still exact-prompt shaped. Nearby private Meeting information requests can still route to generic
Meeting information copy, sibling privacy Q&A, or no match.

## Blocking Findings

### P1: Natural private Meeting information variants still miss the Meeting information privacy Q&A

Locations:

- `src/ai_presenter/runtime/questions.py:326`
- `src/ai_presenter/runtime/questions.py:329`
- `src/ai_presenter/runtime/questions.py:336`
- `src/ai_presenter/runtime/questions.py:344`
- `src/ai_presenter/runtime/questions.py:409`
- `src/ai_presenter/runtime/questions.py:420`
- `packages/ringcentral-video.yaml:1737`
- `packages/ringcentral-video.yaml:1740`
- `packages/ringcentral-video.yaml:1767`
- `tests/unit/test_questions.py:756`
- `tests/unit/test_questions.py:793`

`_is_package_entrypoint_alias_lookup()` now lets Meeting information aliases through when the prompt contains private
action tokens, and the package adds exact Q&A prompts for the named failures. That fixes those exact strings, but it
does not bind private meeting ID/link/URL requests to the Meeting information privacy Q&A before the generic substring
and token-scoring passes run.

Read-only probes against the current dirty tree:

| Prompt | Current result |
| --- | --- |
| `Please read the meeting link` | Invite privacy Q&A |
| `Can you share the meeting ID?` | Screen sharing privacy Q&A |
| `Share meeting ID` | generic `Meeting information:` entrypoint answer |
| `Paste meeting ID` | generic `Meeting information:` entrypoint answer |
| `Read meeting URL` | no matching control |

These responses are non-operable and did not create interrupt steps, so they do not immediately expose exact meeting
values. They still miss the intended safety answer: `Meeting IDs and links are private meeting details...`.

The most important root cause is that the implementation allows private Meeting information prompts past the alias
guard, but then relies on exact YAML prompts, raw substring checks, and broad token scoring. A small stopword insertion
like `the` in `Please read the meeting link` prevents the new exact prompt `Please read meeting link` from matching,
and token scoring can then choose older Invite or Screen sharing privacy items.

Suggested fix direction: add a dedicated Meeting information privacy matcher before the generic Q&A candidate loops.
It should route private action/content forms for meeting ID, link, URL, dial-in, host, information, or details directly
to the Q&A related to `ringcentral.video.top.meeting-info`, while preserving location prompts such as
`where is the meeting link` on the generic Meeting information entrypoint answer.

Suggested regression coverage:

- `Please read the meeting link`
- `Can you share the meeting ID?`
- `Share meeting ID`
- `Paste meeting ID`
- `Read meeting URL`

Expected assertions: `entrypoint_id == "ringcentral.video.top.meeting-info"`, `can_operate is False`, no interrupt,
Meeting information privacy wording present, generic `Meeting information:`, `Invite participants:`, and
`Screen sharing:` wording absent, and no exact URL/domain/sample ID.

## Non-blocking Findings

### P3: `Share status` and `Share security` still rely on token overlap

Locations:

- `packages/ringcentral-video.yaml:1785`
- `packages/ringcentral-video.yaml:1804`
- `packages/ringcentral-video.yaml:1810`
- `tests/unit/test_questions.py:842`
- `tests/unit/test_questions.py:867`
- `tests/unit/test_questions.py:874`

The broad status/security guard is working for bare `status`, `security`, `secure`, and `verify`. The action prompts
`Share status` and `Share security` also route to the encryption-status Q&A, but they are not exact package prompts in
the dirty YAML. They currently work through token overlap with broader prompts such as `Share meeting security status`.

That behavior is acceptable in the current diff, but it remains fragile if another Q&A later shares those broad tokens.
Either add exact prompts for `Share status` and `Share security`, or document in the tests that those two cases
intentionally validate token-overlap routing.

## Reviewed Diff

- `src/ai_presenter/runtime/questions.py`
  - Adds `_BROAD_QA_FRAGMENT_TOKENS`.
  - Adds Meeting information constants and `_is_package_entrypoint_alias_lookup()`.
  - Moves package entrypoint alias lookup before generic Q&A matching, with a Meeting information exception for private
    actions and exact sensitive aliases.
- `packages/ringcentral-video.yaml`
  - Adds exact Meeting information privacy prompts for the latest named cases.
  - Adds additional Meeting information information/details prompts and encryption-status copy/share prompts.
- `tests/unit/test_questions.py`
  - Extends Meeting information privacy coverage for the named exact prompts.
  - Adds bare broad-word no-match coverage.
  - Extends encryption-status answer-only coverage.
- `tests/unit/test_cli.py` and `tests/unit/test_diagnostics.py`
  - Update Q&A prompt-count expectations from `200` to `220`.

## Verification

The user reported focused verification as:

- `78 passed in 15.16s`

I did not rerun pytest because the repository pytest configuration writes coverage by default and this review was
explicitly scoped not to edit `.coverage`.

Read-only checks run during this review:

- `git status --short`
- `git diff --stat`
- `git diff --name-only`
- `git diff -- src/ai_presenter/runtime/questions.py`
- `git diff -- tests/unit/test_questions.py`
- `git diff -- packages/ringcentral-video.yaml`
- `git diff -- tests/unit/test_cli.py tests/unit/test_diagnostics.py`
- `git diff --check -- src/ai_presenter/runtime/questions.py packages/ringcentral-video.yaml tests/unit/test_questions.py tests/unit/test_cli.py tests/unit/test_diagnostics.py`
- Read-only `python -B` probes with `PYTHONDONTWRITEBYTECODE=1` and `PYTHONPATH=src`

`git diff --check` reported only the existing LF-to-CRLF warnings for the touched files.

## Status

Blocking status: one blocking matcher issue remains.

Doc path:

- `docs/agent-handoffs/cycle-171-third-post-fix-review.md`
