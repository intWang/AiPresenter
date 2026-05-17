# Cycle 204 Lessons: Wiring Evidence Guards Into CLI

## Reusable Lesson

When a guard depends on an optional sidecar document, distinguish implicit discovery from explicit user intent. An implicit sibling `acceptance-runs.md` may be optional for compatibility, but an explicit `--acceptance-runs` path must be read directly and fail if it is missing or unreadable.

## Prompt Pattern

Review CLI guard wiring by asking: "Can the user pass an option that appears to enable the guard but actually disables it when the file is absent?" If yes, add a missing-file regression and make explicit paths strict while keeping automatic discovery optional.

## Test Lesson

Guard wiring needs both negative and positive CLI tests:

- synthetic `Accepted` evidence plus ineligible acceptance runs should fail;
- synthetic `Accepted` evidence plus a qualifying synthetic manual pass should succeed;
- explicit missing sidecar path should fail before rendering target lines.

## Follow-Up Candidates

- Render the acceptance-runs path in validation-target output when a guard file is loaded.
- Add a CLI help/README note for `--acceptance-runs`.
- Consider enforcing a similar sidecar-document distinction in future knowledge-package commands.
