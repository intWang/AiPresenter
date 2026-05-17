# Cycle 171 Final Privacy Matcher Review

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`
Role: Cycle171 final privacy matcher review

## Scope

Reviewed the current dirty diff only after the main session added `_match_meeting_info_privacy_qa()` before the generic
Q&A loops.

This pass wrote only:

- `docs/agent-handoffs/cycle-171-final-privacy-matcher-review.md`

This pass did not edit code, tests, package YAML, `.coverage`, staging, or commits. The pre-existing dirty tree was
left untouched.

## Verdict

Blocking finding remains.

The previous English adjacent private Meeting information misses are fixed. Read-only probes now route these prompts to
the Meeting information privacy Q&A with `can_operate=False` and no interrupt:

- `Please read the meeting link`
- `Can you share the meeting ID?`
- `Share meeting ID`
- `Paste meeting ID`
- `Read meeting URL`
- `Could you copy the meeting link?`
- `Copy host information`
- `Share host details`
- `Paste meeting link`

The intended plain/location entrypoint behavior is also preserved for:

- `meeting information`
- `where is meeting information`
- `where is meeting link`
- `Where is the meeting link?`

The bare broad-word guard still works for `status`, and `copy status` / `share status` route to the encryption-status
Q&A.

However, localized Chinese action forms containing the exact private Meeting information fragments still miss the new
privacy matcher.

## Blocking Findings

### P1: Chinese copy/share/read Meeting information prompts bypass the privacy Q&A

Locations:

- `src/ai_presenter/runtime/questions.py:47`
- `src/ai_presenter/runtime/questions.py:417`
- `src/ai_presenter/runtime/questions.py:431`
- `src/ai_presenter/runtime/questions.py:452`
- `src/ai_presenter/runtime/questions.py:463`
- `packages/ringcentral-video.yaml:1773`
- `tests/unit/test_questions.py:798`
- `tests/unit/test_questions.py:2822`

`_match_meeting_info_privacy_qa()` recognizes Chinese private-content fragments, `会议号` and `会议链接`, but
`_PRIVATE_MEETING_INFO_ACTION_TOKENS` contains only English action words: `copy`, `paste`, `read`, and `share`.

As a result, bare Chinese fragments such as `会议链接` still route to the localized privacy Q&A, but natural Chinese
action requests fall through to the generic Meeting information entrypoint answer:

| Prompt | Current result |
| --- | --- |
| `复制会议号` | generic `Meeting information:` entrypoint answer |
| `复制会议链接` | generic `Meeting information:` entrypoint answer |
| `请复制会议号` | generic `Meeting information:` entrypoint answer |
| `请分享会议链接` | generic `Meeting information:` entrypoint answer |
| `读会议号` | generic `Meeting information:` entrypoint answer |

These responses remain non-operable and do not expose an exact ID or link, but they lose the intended privacy copy:
`会议号和会议链接属于私人会议详情...`. They also return the thinner English entrypoint answer under a Chinese voice.

The current tests cover the English action forms in `test_ringcentral_english_meeting_info_privacy_questions_stay_qa_first`
and the bare Chinese `会议链接` short question, but they do not cover localized action-plus-fragment prompts.

Suggested fix direction: extend the dedicated matcher with localized private-action terms for at least Chinese
`复制`, `粘贴`, `读`, `朗读`, and `分享`, then add regression rows for the prompts above. Expected assertions should match
the English privacy rows: entrypoint `ringcentral.video.top.meeting-info`, `can_operate=False`, no interrupt, localized
privacy wording present, generic `Meeting information:` absent, and no exact URL/domain/sample ID.

## Non-blocking Findings

### P3: `Share status` and `Share security` still depend on token-overlap routing

Locations:

- `packages/ringcentral-video.yaml:1805`
- `packages/ringcentral-video.yaml:1807`
- `tests/unit/test_questions.py:874`
- `tests/unit/test_questions.py:876`

The dirty tests now cover `Share status`, `Share security`, `Share secure`, `Share verify`, `Copy status`,
`Copy security`, `Copy secure`, and `Copy verify`. They all route answer-only to the encryption-status Q&A in current
probes.

`Share status` and `Share security` are still not exact package prompts, so they depend on broad token overlap with
nearby encryption/security Q&A prompts. This is acceptable for the current diff because tests pin the behavior, but it
remains brittle if future Q&A items reuse `share`, `status`, or `security`.

## Reviewed Diff

- `src/ai_presenter/runtime/questions.py`
  - Adds `_BROAD_QA_FRAGMENT_TOKENS`.
  - Adds Meeting information privacy constants.
  - Adds `_match_meeting_info_privacy_qa()` before generic Q&A candidate loops.
  - Keeps location lookup terms on the entrypoint answer.
  - Adds `_is_package_entrypoint_alias_lookup()` so package aliases can stop broad Q&A shadowing while allowing
    private Meeting information action prompts through to the dedicated matcher.
- `packages/ringcentral-video.yaml`
  - Adds exact English Meeting information privacy prompts.
  - Adds encryption-status copy/share prompts.
- `tests/unit/test_questions.py`
  - Extends English Meeting information privacy coverage.
  - Adds bare broad-word no-match coverage.
  - Extends encryption-status answer-only coverage.
  - Covers bare Chinese `会议链接`, but not Chinese action forms like `复制会议链接`.
- `tests/unit/test_cli.py` and `tests/unit/test_diagnostics.py`
  - Update Q&A prompt-count expectations from `200` to `220`.

## Verification

The user reported focused verification as:

- `80 passed in 15.98s`

I did not rerun pytest because this review is scoped to one document and the repository pytest configuration can write
coverage artifacts. Read-only checks/probes run during this review:

- `git status --short`
- `git diff --name-status`
- `git diff --stat`
- `git diff -- src/ai_presenter/runtime/questions.py`
- `git diff -- tests/unit/test_questions.py`
- `git diff -- packages/ringcentral-video.yaml`
- `git diff -- tests/unit/test_cli.py tests/unit/test_diagnostics.py`
- `git diff --check -- src/ai_presenter/runtime/questions.py packages/ringcentral-video.yaml tests/unit/test_questions.py tests/unit/test_cli.py tests/unit/test_diagnostics.py`
- `.\.venv\Scripts\python.exe -B -` read-only route probes with `PYTHONDONTWRITEBYTECODE=1`, `PYTHONPATH=src`, and
  `PYTHONIOENCODING=utf-8`

`git diff --check` reported only existing LF-to-CRLF working-copy warnings for the touched files.

## Status

Blocking status: one localized matcher issue remains.

Doc path:

- `docs/agent-handoffs/cycle-171-final-privacy-matcher-review.md`
