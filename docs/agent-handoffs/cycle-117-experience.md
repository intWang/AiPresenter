# Cycle 117 Experience Handoff: Spanish Report-Only Boundary

Date: 2026-05-16
Scope: experience capture only. This file is the only file edited by this handoff.

## Cycle Summary

Cycle 117 completed Spanish report-only Q&A coverage for the RingCentral Video
package. Spanish Q&A report coverage should now read as 12/12 questions and
12/12 answers, while Spanish demo narration remains 0/51 and Spanish runtime
presenter language support remains unsupported.

The useful process learning is the boundary between package localization and
runtime presenter support. A localized report package can make diagnostics and
coverage reports more complete without changing what languages the live
presenter accepts, speaks, routes, or advertises.

## Reusable Lessons

- Treat report-only package localization as content coverage, not runtime
  enablement. Spanish Q&A coverage can be complete while runtime Spanish remains
  intentionally unavailable.
- Keep localization claims precise: "Spanish Q&A report coverage is complete"
  is different from "Spanish is a supported presenter language."
- Verify unsupported runtime Spanish by checking for a nonzero failure and the
  diagnostic text `Unsupported presenter language: es`. Do not assume a fixed
  exit code of 1; `demo --language es --dry-run` currently fails during CLI
  parameter validation with exit code 2.
- When adding localized Q&A prompts, update diagnostics prompt counts in the
  same slice so report expectations and operator-facing checks stay aligned.
- Preserve product UI labels that should remain literal in RingCentral Video
  guidance: `Invite`, `Chat`, `Participants`, `Settings`, `Background`, and
  `Blur`.
- Avoid broad language aliases unless routing tests prove they cannot change
  package selection, presenter support checks, or safety behavior by accident.
- Keep this learning in repo-local handoffs or knowledge docs. Do not promote it
  into a global Codex skill without an explicit design and approval path.
- Never stage `.coverage`. It is a local/generated artifact and is especially
  easy to include accidentally when a localization cycle touches tests.

## Next Language/Runtime Promotion Checklist

- Decide the layer first: report-only package coverage, demo narration
  coverage, or full runtime presenter promotion.
- For report-only expansion, verify localized Q&A question and answer counts
  independently and keep demo narration incompleteness visible.
- For demo narration expansion, add the narration prompts and rerun the
  localization report before changing runtime language lists.
- For runtime promotion, require end-to-end support across
  `PresenterVoiceSettings`, voice catalogs, CLI output, doctor diagnostics,
  package fallback behavior, provider compatibility, and no-match wording.
- Before runtime promotion, verify `demo --language es --dry-run` still rejects
  Spanish with a nonzero exit and `Unsupported presenter language: es`.
- Add routing and alias tests before accepting broad names such as language
  families, regional variants, or shorthand codes.
- Recheck preserved UI labels so localized prose does not translate fixed
  RingCentral interface strings.
- Confirm `.coverage` is not staged before any handoff, commit, or PR step.

## Suggested Next-Cycle Opportunities

- Finish Spanish demo narration coverage as the next package-localization slice,
  keeping runtime Spanish disabled until all runtime gates are deliberately met.
- Add a focused localization diagnostics test that fails when Q&A prompt counts
  change without matching report expectations.
- Draft a Spanish runtime promotion plan that enumerates every required code,
  docs, package, provider, and CLI surface before implementation begins.
- Review whether another report-only language can reuse the Cycle 117 pattern:
  complete Q&A coverage first, preserve literal UI labels, and defer runtime
  support until the presenter contract is ready.
