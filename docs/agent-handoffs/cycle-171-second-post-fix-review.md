# Cycle 171 Second Post-Fix Review

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`
Role: Cycle171 second post-fix matcher review

## Scope

Reviewed the current dirty diff after the main session added exact Meeting information prompts, updated the Q&A count
expectations to `215`, and refined `_is_package_entrypoint_alias_lookup()`.

This pass wrote only:

- `docs/agent-handoffs/cycle-171-second-post-fix-review.md`

This pass did not edit code, tests, package YAML, `.coverage`, staging, or commits. The pre-existing dirty tree was left
untouched.

## Verdict

Blocking finding remains.

The new exact prompts fix the named cases from the handoff: `Can you share the meeting link?`,
`Please copy the meeting link`, and `Read meeting ID` now resolve to the Meeting information privacy Q&A. The broad bare
status/security guard also works for the four covered terms: `status`, `security`, `secure`, and `verify` return no
Q&A match.

However, the fix is still exact-prompt shaped. Several adjacent private Meeting information action prompts still route
to the generic Meeting information entrypoint answer, Invite/Share privacy Q&A, or no match instead of the Meeting
information privacy Q&A.

## Blocking Findings

### P1: Adjacent private Meeting information prompts still miss the privacy Q&A

Locations:

- `src/ai_presenter/runtime/questions.py:326`
- `src/ai_presenter/runtime/questions.py:329`
- `src/ai_presenter/runtime/questions.py:336`
- `src/ai_presenter/runtime/questions.py:344`
- `src/ai_presenter/runtime/questions.py:409`
- `src/ai_presenter/runtime/questions.py:420`
- `packages/ringcentral-video.yaml:1737`
- `packages/ringcentral-video.yaml:1740`
- `packages/ringcentral-video.yaml:1762`
- `tests/unit/test_questions.py:756`
- `tests/unit/test_questions.py:799`

`_is_package_entrypoint_alias_lookup()` now allows Meeting information aliases through when the normalized prompt has a
private action token or is an exact sensitive alias. That gets the request past the early alias guard, but it does not
force a Meeting information privacy Q&A match. After that, the generic Q&A substring/token loop and final entrypoint
matcher can still choose unrelated or generic answers.

Read-only probes against the current dirty tree:

| Prompt | Current result |
| --- | --- |
| `Copy meeting ID` | generic `Meeting information:` entrypoint answer |
| `Please copy meeting ID` | generic `Meeting information:` entrypoint answer |
| `Paste meeting ID` | generic `Meeting information:` entrypoint answer |
| `Share meeting ID` | generic `Meeting information:` entrypoint answer |
| `Read meeting link` | Invite privacy Q&A |
| `Please read the meeting link` | Invite privacy Q&A |
| `Can you share the meeting ID?` | Screen sharing privacy Q&A |
| `Share meeting URL` | generic `Screen sharing:` entrypoint answer |
| `Please share meeting URL` | generic `Screen sharing:` entrypoint answer |
| `Read meeting URL` | no matching control |

The observed responses were non-operable and did not create interrupt steps, but they still miss the intended privacy
copy: `Meeting IDs and links are private meeting details...`. The `Share meeting URL` cases are especially misleading
because a private meeting URL request receives screen-sharing copy.

Root cause:

- `_PRIVATE_MEETING_INFO_ALIAS_FRAGMENTS` covers `meeting id`, `meeting link`, and the Chinese equivalents, but not
  `meeting url`.
- Allow-through in `_is_package_entrypoint_alias_lookup()` only removes the early alias block. It does not bind the
  request to the Q&A related to `ringcentral.video.top.meeting-info`.
- The tests now cover important exact prompts, but they do not cover shorter or newly prefixed private variants such as
  `Copy meeting ID`, `Share meeting ID`, `Read meeting link`, or `Share meeting URL`.

Suggested fix direction: add a dedicated Meeting information privacy matcher before the generic Q&A substring/token
loops. It should route private action/content forms directly to `_qa_by_related_entrypoint(package,
_MEETING_INFO_ENTRYPOINT_ID)`, while continuing to let location queries such as `Where is the meeting link?` use the
entrypoint answer. Add regression coverage for the probes above with assertions that:

- `entrypoint_id == "ringcentral.video.top.meeting-info"`
- `can_operate is False`
- no interrupt step is created
- Meeting information privacy wording is present
- generic `Meeting information:`, `Invite participants:`, and `Screen sharing:` fallback wording is absent

## Non-blocking Findings

### P3: `Share status` and `Share security` still rely on token scoring, not exact prompts

Locations:

- `packages/ringcentral-video.yaml:1799`
- `packages/ringcentral-video.yaml:1802`
- `packages/ringcentral-video.yaml:1803`
- `tests/unit/test_questions.py:861`
- `tests/unit/test_questions.py:862`
- `tests/unit/test_questions.py:863`

The broad bare-word guard is working for `status`, `security`, `secure`, and `verify`. The action phrases
`Share status` and `Share security` also currently resolve to the encryption-status Q&A, but they do so through token
overlap with broader prompts such as `Share meeting security status`; they are not exact package prompts. This is
acceptable as a behavior check, but it is more brittle than the exact prompt additions used for Meeting information.

Suggested hardening: either add exact package prompts for `Share status` and `Share security`, or rename/comment the
test cases to make clear that those two examples intentionally validate token-overlap routing.

## Reviewed Diff

- `src/ai_presenter/runtime/questions.py`
  - Adds `_BROAD_QA_FRAGMENT_TOKENS`.
  - Adds Meeting information constants and `_is_package_entrypoint_alias_lookup()`.
  - Moves package alias lookup ahead of generic Q&A matching with a Meeting information exception for private actions
    and exact sensitive aliases.
- `packages/ringcentral-video.yaml`
  - Adds exact Meeting information privacy prompts, including the three named by the main session.
  - Adds encryption-status prompts for copy/share secure/status/verify forms.
- `tests/unit/test_questions.py`
  - Extends Meeting information privacy assertions.
  - Adds bare broad-word guard coverage.
  - Extends encryption-status assertions.
- `tests/unit/test_cli.py` and `tests/unit/test_diagnostics.py`
  - Update Q&A prompt-count expectations from `200` to `215`.

## Verification

Main session reported focused Meeting information verification as:

- `35 passed`

I did not rerun pytest because the main session was rerunning count tests and this review was scoped to one document.

Read-only checks run during this review:

- `git status --short`
- `git diff --stat`
- `git diff -- src/ai_presenter/runtime/questions.py`
- `git diff -- packages/ringcentral-video.yaml`
- `git diff -- tests/unit/test_questions.py`
- `git diff -- tests/unit/test_cli.py tests/unit/test_diagnostics.py`
- `git diff --check -- src/ai_presenter/runtime/questions.py packages/ringcentral-video.yaml tests/unit/test_questions.py tests/unit/test_cli.py tests/unit/test_diagnostics.py`
- `python -B` probes with `PYTHONDONTWRITEBYTECODE=1` and `PYTHONPATH=src`

`git diff --check` reported only the existing LF-to-CRLF warnings for touched files.

## Status

Blocking status: one blocking matcher issue remains.

Doc path:

- `docs/agent-handoffs/cycle-171-second-post-fix-review.md`
