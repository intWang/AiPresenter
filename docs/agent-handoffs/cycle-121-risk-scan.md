# Cycle 121 Risk Scan

Scope: documentation-only risk scan for candidate Cycle 121 work after the Cycle 120 diagnostics/runtime language boundary guard. This handoff creates only `docs/agent-handoffs/cycle-121-risk-scan.md`; do not stage or commit from this scan.

## Current Boundary

- Spanish package localization remains partial and reportable, not runtime supported.
- Cycle 120 added `doctor --localization-language` so package localization diagnostics can inspect keys such as `es` without promoting Spanish into `--language`.
- Spanish runtime must still be rejected by presenter voice/runtime paths.
- The next cycle should pick one narrow slice. Combining Spanish content, diagnostics wording, performance/index behavior, and playbook docs would make regressions hard to isolate.

## Candidate Slice Risks

### Spanish Narration Wedge

Go only if the slice is package-local narration for a named flow or step group.

Main risks:

- Runtime Spanish leakage through `voices`, profiles, provider routing, controller language choices, or `PresenterVoiceSettings`.
- Translated UI labels that make users search for Spanish labels in an English RingCentral UI. Visible labels such as `Chat`, `Participants`, `Invite`, `Share`, `Notes`, `Recording`, `More`, `Leave`, and `Stop video` should stay literal unless the actual product UI changes.
- Misleading support wording, especially "Spanish supported", "Spanish accepted", "runtime-ready", or "live verified".
- Stale diagnostic counts if tests or handoffs keep old Spanish coverage totals after adding narration.

Go boundary:

- Add only Spanish `localizedText.es` narration for the selected package-owned demo steps.
- Keep Spanish Q&A, aliases, runtime language support, provider catalogs, and controller choices unchanged unless explicitly scoped.
- Update localization-report and diagnostic count assertions from package-derived current totals.
- Prove `demo --language es --dry-run` and `doctor --language es` still reject runtime Spanish.

No-go boundary:

- The slice requires Spanish voices, profile support, controller support, translated UI labels, new aliases, or wording that says Spanish is supported rather than partially localized.

### Performance or Index Guard

Go only with a measured target and behavior-lock tests first.

Main risks:

- Matching/index behavior drift in Q&A precedence, alias ordering, localized question lookup, substring diagnostics, or duplicate detection.
- Diagnostics counts changing because an index excludes, duplicates, or reorders package material.
- "Performance" refactors accidentally changing public package validation or runtime routing.

Go boundary:

- Define the exact surface under guard, such as package index immutability, lookup parity, or duplicate-count stability.
- Add before/after tests that assert current matching results and diagnostic counts.
- Keep YAML, localization strings, runtime languages, and CLI wording unchanged.

No-go boundary:

- The slice changes matching semantics while also changing Spanish content, diagnostics text, or playbook docs.

### Diagnostics Polish

Go if the polish clarifies lifecycle wording without expanding behavior.

Main risks:

- Misleading acceptance wording that treats package localization coverage as runtime language support.
- Stale diagnostic counts in examples or assertions.
- Runtime Spanish leakage if `--localization-language es` is conflated with `--language es`.

Go boundary:

- Keep `--language` as the runtime voice selector and `--localization-language` as the package coverage selector.
- Use wording such as "package localization", "coverage", "incomplete", and "runtime language unsupported".
- Assert Spanish diagnostics can be reported while Spanish runtime commands remain rejected.

No-go boundary:

- Any diagnostic output says Spanish is accepted, supported, runnable, live-ready, or voice-ready.

### Playbook or Skill Docs

Go if docs preserve the boundary and do not imply implementation completion.

Main risks:

- Support/acceptance wording becomes broader than the code supports.
- Examples embed stale counts or commands that future agents treat as source of truth.
- Docs encourage staging `.coverage` or unrelated generated artifacts during handoff cycles.

Go boundary:

- Document the lifecycle distinction: package-local coverage can exist before runtime support.
- Prefer commands that verify current behavior over hard-coded claims where possible.
- Include an explicit reminder that `.coverage` is generated and should remain unstaged.

No-go boundary:

- Docs describe Spanish as generally supported or recommend runtime demos in Spanish before runtime promotion exists.

## One-Cycle Recommendation

Preferred Cycle 121 slice: a small diagnostics polish or playbook/docs update that reinforces the Cycle 120 boundary. This has the lowest blast radius and reduces future confusion before more Spanish content is added.

Acceptable alternate: one small Spanish narration wedge, but only if it is package-local, keeps UI labels literal, updates counts, and re-verifies Spanish runtime rejection.

Defer by default: performance/index work. It is valuable, but it needs a dedicated behavior-lock plan because matching and diagnostic-count drift are high-impact regressions.

Do not combine these slices in one cycle.

## Required Failure-Mode Checks

| Failure mode | What can go wrong | One-cycle guard |
| --- | --- | --- |
| Runtime Spanish leakage | Spanish appears in runtime language choices, voice catalogs, profiles, controller choices, provider routing, or dry-run execution. | Keep `--language es` rejection tests and `voices` exclusion tests in scope for any Spanish-adjacent slice. |
| Translated UI labels | Spanish narration translates English product labels and sends users looking for labels that are not visible. | Review touched Spanish strings for literal UI labels; add focused assertions for the selected flow when practical. |
| Stale diagnostic counts | Localization or diagnostic output reports old demo/Q&A/alias totals after content or index changes. | Derive expected totals from current package status and update exact assertions in the same slice. |
| Matching/index behavior drift | Lookup order, alias precedence, duplicate warnings, or localized question matching changes during performance work. | Add parity tests before refactoring and keep diagnostics count tests unchanged unless the behavior change is intentional. |
| Misleading support/acceptance wording | CLI, docs, or handoffs imply Spanish is supported, accepted, runtime-ready, or live verified. | Grep touched text for support claims and replace with package-local lifecycle wording. |
| `.coverage` staging | Generated coverage data is staged with a docs or handoff change. | Check `git status --short` before handoff; leave `.coverage` unstaged and do not include it in commits. |

## Minimal Exit Checklist

- [ ] Diff contains only files explicitly assigned to the implementation cycle.
- [ ] `.coverage` is not staged.
- [ ] Spanish runtime support remains unchanged unless the cycle explicitly promotes runtime Spanish.
- [ ] Spanish package localization counts are current after any narration changes.
- [ ] Visible RingCentral UI labels remain literal in Spanish narration.
- [ ] Diagnostics and docs separate package localization coverage from runtime language support.
- [ ] Matching/index behavior has parity tests before any performance/index refactor.

Bottom line: for Cycle 121, go small. The safest one-cycle move is boundary-preserving diagnostics/docs polish; the only content slice worth accepting is a tightly named Spanish narration wedge with runtime rejection and count checks kept front and center.
