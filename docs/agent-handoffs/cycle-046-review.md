# Cycle 046 Review

## Review Agent

Agent: `019e2e9c-a2de-7e60-9534-249272110900`

## Initial Findings

- Critical: none.
- Important: the first matcher guard blocked all one-word English Q&A fragment matches. It made `recording` fall through to the generic `Start recording: Start recording the meeting.` entrypoint answer, bypassing the recording safety Q&A.
- Minor: none.

## Resolution

The matcher now allows fragment matches for Q&A items that declare `relatedEntrypointIds`, so safety Q&A such as `recording`, `background`, and `choppy` can still answer with their package guidance.

Answer-only Q&A items still avoid broad shortcut words: if a fragment is not specific and already maps to an entrypoint, the answer-only Q&A lets entrypoint matching handle it. This keeps `participants` on `ringcentral.video.toolbar.participants` while exact/specific host-control questions use the new answer-only guidance.

## Follow-Up Review

The review agent rechecked the latest diff after the fix and reported no Critical, Important, or Minor findings. Its read-only probes confirmed:

- `participants` returns `ringcentral.video.toolbar.participants` with the generic Participants panel answer.
- `recording` returns the recording safety Q&A and includes participant-consent guidance.
- `background` returns the background privacy Q&A.
- `choppy` returns the network-quality troubleshooting Q&A.
- `host controls` remains answer-only with `entrypoint_id=None` and `can_operate=False`.

## Regression Coverage Added

- `test_recording_answer_is_not_operable` now asserts the recording safety text is returned and the generic `Start recording:` answer is not.
- `test_participants_matches_participants_entrypoint` now asserts `participants` stays on the Participants entrypoint and does not surface host/moderator answer text.

## Verification Evidence

- Red run before the fix: `test_recording_answer_is_not_operable` failed because `recording` returned `Start recording: Start recording the meeting.`
- Focused green run after the fix: `4 passed`.
- Wider focused run: `150 passed`.
- Focused lint: `ruff check --no-cache src\ai_presenter\runtime\questions.py tests\unit\test_questions.py` passed.
- Focused typing: `mypy --no-incremental src\ai_presenter\runtime\questions.py tests\unit\test_questions.py` passed.
- Probe:
  - `participants` -> `ringcentral.video.toolbar.participants`
  - `recording` -> recording safety Q&A
  - `background` -> background privacy Q&A
  - `choppy` -> network quality Q&A
  - `where are host controls for participants` -> answer-only host guidance
