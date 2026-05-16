# Cycle 047 Demand Analysis

## Recommended Slice

Harden RingCentral Video meeting-information questions so they remain answerable but are not auto-operable from question matching.

## User Value

Meeting information can expose meeting IDs, links, dial-in details, host identity, and encryption status. AiPresenter should explain where those details live, but should not queue an automatic UI action that might reveal private meeting details during a live demo.

## Acceptance Criteria

- English questions such as `meeting information`, `where is the meeting ID`, and `where is the meeting link` still match `ringcentral.video.top.meeting-info`.
- Chinese package aliases such as `会议号在哪里` and `会议链接` still match `ringcentral.video.top.meeting-info`.
- Those question responses return `can_operate is False`.
- The answer stays explanatory and does not read, invent, or copy meeting IDs, links, dial-in details, host identity, or encryption values.
- Existing safety behavior for Invite, Share, Recording, Leave, Notes, Chat, Participants, Network quality, and Background remains unchanged.

## Out Of Scope

- No confirmation workflow.
- No live RingCentral automation.
- No locator changes for top-bar coordinates.
- No package schema change.
- No broad matcher rewrite.
- No policy change allowing private meeting details to be read aloud.

## Likely Tests

- Add focused `tests/unit/test_questions.py` assertions for English and Chinese meeting-info questions.
- Keep existing alias matching coverage for `会议号在哪里`.
- Run focused question tests, then full pytest, ruff, mypy, and diff checks.

