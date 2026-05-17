# Cycle 171 Post-Fix Final Review

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`
Role: Cycle171 post-fix final matcher review

## Scope

Reviewed the dirty diff after the main session replaced the generic early package-alias guard with
`_is_package_entrypoint_alias_lookup()`.

This pass wrote only:

- `docs/agent-handoffs/cycle-171-post-fix-review.md`

This pass did not edit code, tests, package YAML, `.coverage`, staging, or commits. The pre-existing dirty tree,
including the deleted `.coverage`, was left untouched.

## Verdict

Blocking finding remains.

The new guard correctly stops treating all Meeting information alias matches as immediate entrypoint lookups. It also
fixes the reported bare Chinese sensitive aliases and the covered English `meeting information` / `meeting details`
privacy forms.

However, allowing a Meeting information alias prompt through the guard does not force it to resolve to the Meeting
information privacy Q&A. The later generic Q&A and entrypoint matchers can still choose Invite, Screen sharing, or the
generic `Meeting information:` entrypoint answer for nearby sensitive link/ID action prompts.

## Blocking Findings

### P1: Link/ID action variants still miss the Meeting information privacy Q&A

Locations:

- `src/ai_presenter/runtime/questions.py:329`
- `src/ai_presenter/runtime/questions.py:336`
- `src/ai_presenter/runtime/questions.py:344`
- `src/ai_presenter/runtime/questions.py:409`
- `src/ai_presenter/runtime/questions.py:420`
- `packages/ringcentral-video.yaml:1753`
- `tests/unit/test_questions.py:772`

`_is_package_entrypoint_alias_lookup()` now returns `False` for Meeting information prompts that include private action
tokens such as `copy`, `paste`, `read`, or `share`, and for exact sensitive aliases such as `meeting id` and
`meeting link`. That is necessary, but the subsequent candidate loop and token scoring still decide the final Q&A match.

Observed read-only probes:

| Prompt | Current result |
| --- | --- |
| `Share meeting link` | generic `Meeting information:` entrypoint answer |
| `Can you share the meeting link?` | Screen sharing privacy Q&A |
| `Could you share the meeting link?` | Screen sharing privacy Q&A |
| `Please copy the meeting link` | Invite privacy Q&A |
| `Read meeting link` | Invite privacy Q&A |
| `Copy meeting ID` | generic `Meeting information:` entrypoint answer |
| `Read meeting ID` | generic `Meeting information:` entrypoint answer |
| `Paste meeting ID` | generic `Meeting information:` entrypoint answer |

These remain non-operable and do not expose exact meeting URLs or IDs, but they do not receive the intended Meeting
information safety copy: `Meeting IDs and links are private meeting details...`. This is the same user-facing class as
the fixed prefixed sensitive forms, and `share` is explicitly included in the new private action token allow-through.

Root cause: the guard only prevents early alias blocking. It does not prioritize the related Meeting information safety
Q&A once the prompt is known to contain a private Meeting information action or exact sensitive alias. As a result:

- `Can you share the meeting link?` ties `Can you share system audio?` before Meeting information candidates because of
  generic tokens like `share` and `you`.
- `Please copy the meeting link` and `Read meeting link` can tie earlier Invite Q&A prompts through `copy/read` plus
  `link`.
- Short `meeting ID` action forms often have no exact package Q&A prompt and fall through to the entrypoint answer.

Suggested fix direction: add a dedicated Meeting information privacy safety matcher before generic fragment/token Q&A
matching, or make `_is_package_entrypoint_alias_lookup()` return a richer classification so `_match_qa()` can route
private Meeting information action/alias prompts directly to the Q&A related to
`ringcentral.video.top.meeting-info`. Add regression coverage for the examples above, plus expected assertions for:

- `entrypoint_id == "ringcentral.video.top.meeting-info"`
- `can_operate is False`
- no interrupt step
- privacy Q&A wording present
- `Meeting information:` fallback absent
- no exact URL/domain/sample ID

## Non-blocking Findings

### P3: Some encryption-status assertions still rely on token overlap, not package prompts

Locations:

- `tests/unit/test_questions.py:859`
- `tests/unit/test_questions.py:860`
- `packages/ringcentral-video.yaml:1796`
- `packages/ringcentral-video.yaml:1797`

The tests cover `Share status` and `Share security`, but the YAML adds `Share meeting security status`, `Share secure`,
and `Share verify`, not exact prompts for `Share status` or `Share security`. The current behavior works through token
overlap. That is acceptable for now, but it is fragile if another Q&A later shares those broad words.

Suggested hardening: either add exact package prompts for `Share status` and `Share security`, or make the test names /
comments explicit that those two cases intentionally validate token-overlap routing.

## Reviewed Diff

- `src/ai_presenter/runtime/questions.py`
  - Adds `_BROAD_QA_FRAGMENT_TOKENS`.
  - Adds `_is_package_entrypoint_alias_lookup()`.
  - Allows private Meeting information action tokens and exact sensitive aliases past the package-alias guard.
  - Keeps location and non-sensitive Meeting information alias lookups on the entrypoint-answer path.
- `packages/ringcentral-video.yaml`
  - Adds Meeting information privacy prompts for read/copy/share information/details forms.
  - Adds encryption-status prompts for copy/share secure/status/verify forms.
- `tests/unit/test_questions.py`
  - Adds focused coverage for the fixed prefixed Meeting information forms, Chinese bare meeting link, broad bare words,
    encryption status, and existing alias lookup behavior.
- `tests/unit/test_cli.py` and `tests/unit/test_diagnostics.py`
  - Update Q&A prompt-count expectations from `200` to `212`.

## Verification

I did not rerun pytest because the requested scope was review plus this one doc write, and rerunning the suite could
touch artifacts outside the allowed write path. The main session reported focused verification as:

- English Meeting information privacy
- Meeting information alias lookup
- Chinese meeting link
- Encryption status
- Bare broad words
- Tone-invariant behavior
- Result: `79 passed in 15.81s`

Read-only checks run during this review:

- `git diff --stat`
- `git diff --no-ext-diff --unified=80 -- src/ai_presenter/runtime/questions.py`
- `git diff --no-ext-diff --unified=80 -- packages/ringcentral-video.yaml tests/unit/test_cli.py tests/unit/test_diagnostics.py`
- `git diff --no-ext-diff --unified=80 -- tests/unit/test_questions.py`
- `git diff --check -- src/ai_presenter/runtime/questions.py packages/ringcentral-video.yaml tests/unit/test_questions.py tests/unit/test_cli.py tests/unit/test_diagnostics.py`
- Read-only `python -B` probes with `PYTHONDONTWRITEBYTECODE=1` and `PYTHONPATH=src`

`git diff --check` reported only the existing LF-to-CRLF warnings for touched files.

## Status

Blocking status: one blocking matcher regression remains.

Doc path:

- `docs/agent-handoffs/cycle-171-post-fix-review.md`
