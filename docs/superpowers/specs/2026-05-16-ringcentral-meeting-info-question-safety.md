# RingCentral Meeting Info Question Safety

## Problem

RingCentral Video meeting information exposes sensitive values such as meeting IDs, links, dial-in details, host identity, and encryption information. Package notes and privacy docs already say these values should be summarized or withheld unless explicitly requested, but question-triggered operation permission can still treat the meeting-info entrypoint as operable.

## Design

Keep matching behavior intact: users asking where meeting information, meeting ID, or meeting link lives should still receive the `ringcentral.video.top.meeting-info` entrypoint answer.

Change only the question safety gate: `ringcentral.video.top.meeting-info` should be explain-only for question responses, returning `can_operate=False`.

## Testing

Add tests that English and Chinese meeting-info questions still match the entrypoint while returning non-operable responses. Keep adjacent safety tests for recording, leave, invite, share, and participants passing.

