# Cycle 170 Post-Failure Review

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`
Scope: review the dirty diff after the post-failure `_can_match_qa_fragment` adjustment. This handoff is the only file written by this review.

## Blocking Findings

None.

The latest runtime rule in `src/ai_presenter/runtime/questions.py` matches the stated policy:

- Specific normalized fragments are allowed.
- Non-specific fragments compute `entrypoint_match`.
- If there is no entrypoint match, the Q&A fragment is allowed.
- If there is an entrypoint match, the Q&A fragment is allowed only when `entrypoint_match.id` is listed in the Q&A item's `related_entrypoint_ids`.

That restores the failure cases from the full-pytest aftermath:

- Bare `settings` no longer routes to the encryption Q&A. It falls through to a settings entrypoint.
- Bare `recording` still reaches the recording safety Q&A because the entrypoint match is `ringcentral.video.more.recording`, which is related to that Q&A item.
- Short Chinese `会议链接` still reaches the meeting-info privacy Q&A because the entrypoint match is `ringcentral.video.top.meeting-info`, which is related to that privacy Q&A item.
- Authored encryption/security-status prompts still return the new answer-only Meeting information Q&A and do not create interrupt steps.

## Non-Blocking Findings

1. Broad security/status fragments are intentionally allowed when no entrypoint is found, but they are now worth treating as a watch item.

   The new encryption Q&A in `packages/ringcentral-video.yaml` contains prompts such as `Security status`, `What is the security status?`, `Is the meeting secure?`, and `Can you verify meeting security?`. Under the stated rule, one-word prompts with no entrypoint match, such as `status`, `security`, `secure`, and `verify`, can route to the encryption-status Q&A. This is consistent with the rule and stays non-operable, but it means broad security language now defaults to encryption-status guidance rather than no-match or participant host/security guidance.

   Suggested follow-up if this surface matters: explicitly decide and test expected behavior for bare `security`, `status`, `secure`, `verify`, and `meeting security`.

2. The rule still trusts the "specific fragment" fast path before checking entrypoint relationship.

   This is exactly the requested rule, and the current focused prompts depend on it. The residual risk is that future multi-token Q&A prompts can shadow unrelated entrypoint routes if the user's query is contained in the Q&A prompt. The current dirty tests cover the high-risk encryption phrases that previously routed to Share, Leave, Settings, RingCentralDevelop, and Network, so this is not blocking for Cycle 170.

   Suggested follow-up: keep adding negative route assertions whenever new Q&A prompts include terms that are also entrypoint titles, aliases, or high-impact action verbs.

## Verification

Reviewed dirty diff for:

- `src/ai_presenter/runtime/questions.py`
- `packages/ringcentral-video.yaml`
- `tests/unit/test_questions.py`
- `tests/unit/test_cli.py`
- `tests/unit/test_diagnostics.py`
- `tests/unit/test_material_packages.py`

Read-only runtime probes were run with `PYTHONDONTWRITEBYTECODE=1` and `.venv\Scripts\python.exe -B`.

Focused pytest was rerun with project coverage and pytest cache disabled:

```powershell
.\.venv\Scripts\python.exe -B -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py::test_settings_prefers_settings_entrypoint tests\unit\test_questions.py::test_recording_answer_is_not_operable tests\unit\test_questions.py::test_chinese_meeting_link_short_question_uses_privacy_qa tests\unit\test_questions.py::test_ringcentral_encryption_status_questions_stay_meeting_info_answer_only tests\unit\test_questions.py::test_ringcentral_localized_encryption_status_questions_are_answer_only tests\unit\test_questions.py::test_ringcentral_sensitive_prompt_routing_is_tone_invariant
```

Result: `41 passed in 8.83s`.

No full pytest rerun was performed in this review pass. The user-provided focused verification after the latest change was `38 passed in 7.53s`; the local no-coverage rerun above covered the same named failure surfaces and produced `41 passed` because of the current parametrization in this dirty tree.

## Dirty Tree Note

The tree was already dirty on entry, including `.coverage`, package YAML, runtime code, tests, and untracked Cycle 170 handoff docs. I did not edit code, tests, package YAML, `.coverage`, staging, or commits.
