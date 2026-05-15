# Controller Chat Questions Design

## Goal

Make controller text interaction feel like a live assistant conversation: users can see question history, read AiPresenter answers, and get safe actionable answers demonstrated without waiting for the main demo to naturally reach the next step.

## Behavior

- The question area becomes a chat transcript with append-only history.
- Every submitted question appends `You: ...`.
- AiPresenter appends the answer text.
- Safe operable answers behave differently by controller state:
  - If a demo is running, request the current flow to stop and switch to a single-step answer demo.
  - If no demo is running, start a single-step answer demo immediately.
- Risky or explain-only answers remain text-only and must not click controls.

## Architecture

`PresenterController.submit_question()` returns a structured result instead of a bare string. The result includes answer text and a demonstration status. `PresenterController` can now schedule a one-step question demo as the next controller target, using `DemoControl.request_stop()` to make the current flow yield.

The Tk UI keeps rendering simple and native: a read-only `Text` widget for history, one entry field, and Submit. This avoids a large UI rewrite while making the controller much more usable.

## Testing

Unit tests cover:

- safe questions interrupt the current flow when a demo is running,
- safe questions start a single-step demo when idle,
- risky questions remain text-only,
- chat transcript formatting appends user and presenter turns.
