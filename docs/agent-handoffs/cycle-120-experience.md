# Cycle 120 Experience Handoff

## Cycle Summary

Cycle 120 separated package localization diagnostics from runtime presenter language support. The CLI now uses `doctor --localization-language` for package localization coverage checks, keeping those diagnostics distinct from runtime narration and presenter-language behavior.

The key outcome is clearer language ownership: Spanish can remain package-local and reportable in localization diagnostics without being treated as a runtime-supported presenter language.

## Reusable Lesson: CLI Wording And Language Lifecycle

Use `--language` only for runtime voice and presenter language selection. Use `--localization-language` for package localization coverage, reports, and diagnostic checks.

This distinction matters because language availability moves through a lifecycle. A locale may be useful for package coverage before it is safe to promote into runtime narration. CLI wording should preserve that boundary so users, tests, and future agents do not infer runtime support from diagnostic visibility.

## Future Runtime-Promotion Checklist

- Confirm the language has complete runtime narration coverage, not just package-local strings.
- Verify voice/presenter behavior end to end for the target locale.
- Keep package localization diagnostics separate from runtime language flags.
- Add tests that prove diagnostic reportability does not imply runtime support.
- Update user-facing help text only when the support boundary actually changes.
- Avoid staging `.coverage` or other generated coverage artifacts.

## Suggested Next-Cycle Opportunities

- Add another carefully scoped Spanish narration wedge while preserving the package-local versus runtime-supported boundary.
- Add a performance/index guard with a measured target so regressions are visible and actionable.
- Extend diagnostics around localization coverage only if the CLI wording continues to make lifecycle stage explicit.
