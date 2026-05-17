# Cycle 171 Chinese Privacy Matcher Review

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`
Role: Cycle171 Chinese privacy matcher final review

## Scope

Reviewed the current dirty diff only. This pass wrote only this handoff:

- `docs/agent-handoffs/cycle-171-chinese-privacy-review.md`

This pass did not edit code, tests, package YAML, `.coverage`, staging, or commits. The pre-existing dirty tree was left
untouched.

## Verdict

The named Chinese action-form blocker is fixed for the prompts covered by the main session:

| Prompt | Current route |
| --- | --- |
| `复制会议链接` | Meeting information privacy Q&A |
| `请分享会议链接` | Meeting information privacy Q&A |
| `读出会议号` | Meeting information privacy Q&A |
| `复制会议号` | Meeting information privacy Q&A |

These responses return `entrypoint_id=ringcentral.video.top.meeting-info`, `can_operate=False`, no interrupt, localized
Chinese privacy wording containing `私人会议详情`, and no generic `Meeting information:` entrypoint label.

The location boundary is also preserved. `会议号在哪里`, `会议链接在哪里`, and mixed action/location probes such as
`分享会议链接在哪里` still return the generic Meeting information entrypoint answer instead of the privacy Q&A.

Blocking status: one adjacent localized parity gap remains.

## Blocking Findings

### P1: Chinese paste Meeting information prompts still bypass the privacy Q&A

Locations:

- `src/ai_presenter/runtime/questions.py:47`
- `src/ai_presenter/runtime/questions.py:427`
- `tests/unit/test_questions.py:2838`

`_PRIVATE_MEETING_INFO_ACTION_TOKENS` now includes Chinese `复制`, `分享`, `读`, `读出`, and `朗读`, which fixes the latest
named copy/share/read cases. It still omits Chinese paste terms such as `粘贴`, even though the English matcher treats
`paste` as a private Meeting information action.

Read-only probes show these Chinese paste requests still fall through to the generic entrypoint answer:

| Prompt | Current result |
| --- | --- |
| `粘贴会议链接` | generic `Meeting information:` entrypoint answer |
| `请粘贴会议链接` | generic `Meeting information:` entrypoint answer |
| `粘贴会议号` | generic `Meeting information:` entrypoint answer |

These responses remain non-operable and do not expose an exact meeting ID or link, but they miss the same localized
privacy copy that the fixed Chinese action forms now receive. Given English `paste meeting link` already belongs to the
private-action set, Chinese paste should have the same routing.

Suggested fix direction: add Chinese paste tokens such as `粘贴` to `_PRIVATE_MEETING_INFO_ACTION_TOKENS`, and add
regression rows for `粘贴会议链接`, `请粘贴会议链接`, and `粘贴会议号` with the same assertions as the new Chinese action tests:
Meeting information privacy Q&A, `can_operate=False`, no interrupt, localized `私人会议详情` wording present, and generic
`Meeting information:` absent.

## Non-blocking Findings

None for the named Chinese copy/share/read fix or the location-prompt boundary.

Workspace note: `.coverage` is currently deleted in the dirty tree, and `packages/ringcentral-video.yaml`,
`src/ai_presenter/runtime/questions.py`, `tests/unit/test_cli.py`, `tests/unit/test_diagnostics.py`, and
`tests/unit/test_questions.py` are modified. Those were pre-existing changes for this review and were not altered here.

## Reviewed Diff

- `src/ai_presenter/runtime/questions.py`
  - Adds Meeting information privacy constants and a dedicated `_match_meeting_info_privacy_qa()` path before generic
    Q&A candidate loops.
  - Adds Chinese action tokens for copy/share/read-style private Meeting information requests.
  - Preserves location prompts by returning `None` from the privacy matcher when location terms such as `哪里`/`在哪`
    are present.
- `tests/unit/test_questions.py`
  - Adds regression coverage for `复制会议链接`, `请分享会议链接`, `读出会议号`, and `复制会议号`.
  - Existing Chinese location coverage still asserts `会议号在哪里` routes to the Meeting information entrypoint.
- `packages/ringcentral-video.yaml`
  - No Chinese paste prompt coverage was added; English paste remains covered by `Can you paste the meeting link?`.

## Verification

The user reported focused meeting-info verification as:

- `49 passed in 9.77s`

Additional read-only checks run in this review:

- `git status --short`
- `git diff --stat`
- `git diff -- src/ai_presenter/runtime/questions.py`
- `git diff -- tests/unit/test_questions.py`
- `git diff -- packages/ringcentral-video.yaml`
- `git diff -- tests/unit/test_cli.py tests/unit/test_diagnostics.py`
- `.\.venv\Scripts\python.exe -B -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests\unit\test_questions.py::test_chinese_meeting_info_action_requests_use_privacy_qa tests\unit\test_questions.py::test_chinese_meeting_link_short_question_uses_privacy_qa tests\unit\test_questions.py::test_meeting_info_privacy_questions_are_answer_only`
  - Result: `12 passed in 2.83s`
- `.\.venv\Scripts\python.exe -B -` read-only route probes with `PYTHONDONTWRITEBYTECODE=1`, `PYTHONPATH=src`, and
  `PYTHONIOENCODING=utf-8`

Important probe detail: literal Chinese sent through PowerShell can render or arrive incorrectly depending on console
encoding, so the route probes used Python `\u` escapes for exact prompt input.

## Status

Blocking status: one Chinese paste parity issue remains.

Doc path:

- `docs/agent-handoffs/cycle-171-chinese-privacy-review.md`
