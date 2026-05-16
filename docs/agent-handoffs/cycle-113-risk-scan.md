# Cycle 113 Risk Scan: RingCentral Video New-Language Wedge

Date: 2026-05-16
Scope: documentation-only risk/review scan. This handoff does not edit production code, package YAML, tests, profiles, knowledge indexes, coverage, or git history.

## Verdict

Conditional go for a very small new-language wedge only if the cycle stays package-content scoped and treats the new language as incomplete until every required surface is deliberately reviewed.

No-go for a broad localization push, Q&A machine translation, alias expansion without matcher tests, docs that imply live RingCentral acceptance evidence, or any change that stages `.coverage`.

The safest shape is:

- Add one tightly scoped language entry for one low-risk RingCentral Video narration or Q&A surface.
- Keep privacy-sensitive Q&A out of scope unless the translated wording receives human review.
- Do not add broad aliases, substring aliases, doctor expectations, navigation-doc claims, or source-index wording changes in the same slice.
- Preserve `--require-complete` failure for the new language until all required demo narration and Q&A localization are intentionally complete.
- Review navigation and language docs for wording that distinguishes package localization from live RingCentral acceptance.

## Primary Risks

| Severity | Risk | Failure mode | Impact | Guardrail |
| --- | --- | --- | --- | --- |
| P0 | Partial localization is mistaken for language readiness | One translated line makes docs, CLI summaries, or reviewers describe the new language as supported. | A presenter may switch to a language with missing narration, missing Q&A, or unsafe fallback wording. | State that the new language is an incomplete wedge. `localization-report --require-complete` must remain nonzero until the language has full required coverage. |
| P0 | Unsafe mistranslation of privacy-sensitive Q&A | Recording, invite links, participants, chat, meeting info, notes, transcript, captions, post-meeting artifacts, or host-control answers lose consent, permission, or verification limits. | AiPresenter could appear to permit reading private data, starting state-changing features, or claiming artifacts exist. | Exclude privacy-sensitive Q&A from the first wedge, or require bilingual human review against the English safety boundaries before merge. |
| P0 | Alias overmatching routes questions to unsafe controls | Short or generic aliases match broad user questions before exact Q&A or safety wording can answer them. | The presenter may prepare an interrupt for meeting info, recording, share, notes, invite, participants, chat, or host controls when it should answer only. | Add no aliases in this wedge unless the alias is specific, non-substring-prone, and covered by focused matcher tests. Prefer no alias work for the first slice. |
| P0 | Doctor alias substring warnings are ignored | New-language aliases introduce substrings of existing aliases, or existing aliases become misleading when compared across languages. | `doctor` output becomes noisy or misses a real collision; reviewers approve a route ambiguity. | Run doctor for the touched language if aliases are touched. Treat new substring warnings as blockers unless the alias is removed or the matcher behavior is explicitly tested. |
| P0 | Navigation or language docs imply live RingCentral acceptance | A source index, language note, or handoff says the new language is accepted, validated, or live-ready based on package data or tests. | Operators may treat localization presence as evidence that RingCentral Video accepted the route in the current build. | Keep docs wording precise: localization/package/test evidence is not live acceptance. Live evidence belongs only in acceptance-run records with dated execution details. |
| P1 | `--require-complete` expectations drift | Tests or docs are updated to expect the new language to pass after one wedge. | The completeness gate loses its value for partial localization. | The first wedge should make the normal report show incremental progress while `--require-complete` still fails with clear missing coverage. |
| P1 | Source-index wording drift | `source-index.md` or related navigation docs are edited to describe the new language as a stable package fact, current support promise, or live evidence. | Knowledge docs become stronger than the evidence they cite. | Do not edit knowledge indexes in this cycle. If a later cycle must edit them, use dated command output and evidence labels, not blanket support wording. |
| P1 | Test brittleness from exact prose snapshots | Tests assert full translated text, exact report prose, or fragile ordering unrelated to the wedge. | Harmless wording fixes cause noisy failures, and reviewers avoid needed localization polish. | Test presence, counts, safety phrases, and missing-step identifiers. Avoid whole-paragraph snapshots. |
| P1 | Fallback language hides missing coverage | Runtime or docs make fallback English look like localized completion. | Missing translations are not visible until a live demo. | Keep report counts authoritative. Do not describe fallback as localization coverage. |
| P2 | Language code normalization surprises | Regional aliases such as `xx-YY` are introduced before canonical language behavior is clear. | CLI, doctor, and voice routing may report different language names or counts. | Start with one canonical language code. Add regional aliases only in a separate voice/language readiness cycle. |
| P2 | Coverage artifact churn | Running tests or reports updates `.coverage`, and the generated file is staged with the handoff. | The diff violates the cycle constraint and hides the real review surface. | Leave `.coverage` unstaged and out of scope. Verify git status before final handoff. |

## Go Guardrails

Proceed only if all of these remain true:

- Exactly one narrow new-language wedge is implemented later; this risk scan itself implements nothing.
- The first slice avoids privacy-sensitive Q&A unless a bilingual reviewer confirms the safety boundary.
- No production code, package loader behavior, runtime routing, profiles, tests, source indexes, knowledge indexes, coverage, or git history are changed in this handoff.
- New-language `--require-complete` remains failing until full required coverage exists.
- Aliases are omitted in the first wedge, or each alias is specific enough to avoid broad substring matching and is covered by focused checks.
- Doctor output has no new unexplained alias substring warning if aliases are touched.
- Documentation says "localized package content" or "offline report coverage" instead of "live RingCentral accepted" unless there is dated acceptance-run evidence.
- `.coverage` remains unstaged.

## No-Go Triggers

Stop the cycle if any of these appear in the proposed implementation:

- A translated privacy-sensitive Q&A answer drops explicit user confirmation, visible-context verification, role/permission limits, participant consent, or private-content reading limits.
- A language doc, navigation doc, source index, or handoff claims live RingCentral readiness from package YAML, unit tests, or CLI localization reports.
- `--require-complete` is changed to pass for a partially localized language.
- Broad aliases such as generic words for "meeting", "video", "chat", "people", "record", "notes", or "info" are added without matcher proof.
- Doctor reports a new alias substring warning and the implementation treats it as harmless without evidence.
- Tests snapshot long translated paragraphs or exact localized prose instead of the behavior being protected.
- The diff touches production code, tests, profiles, package YAML outside the future scoped wedge, `docs/knowledge` indexes, `.coverage`, or git history.

## Review Checklist

Use this checklist before approving any Cycle 113 implementation that follows this scan.

- [ ] Diff scope matches the assigned wedge and does not include production code, profiles, unrelated package YAML, tests outside the approved slice, knowledge indexes, generated coverage, or git metadata.
- [ ] The new language is described as incomplete unless `--require-complete` truly passes after full coverage.
- [ ] The normal localization report shows the expected incremental count change for only the touched surface.
- [ ] `--require-complete` still fails for the new language after a partial wedge, and the missing coverage is understandable.
- [ ] Privacy-sensitive Q&A is unchanged, or every translated answer preserves consent, permission, explicit-request, visible-context, and private-content boundaries.
- [ ] No new aliases are added, or each new alias is reviewed for overmatching, substring collisions, and route ambiguity.
- [ ] Doctor output is reviewed if aliases are touched; any new substring warning is resolved or backed by focused matcher evidence.
- [ ] Source-index, navigation, and language docs do not imply live RingCentral acceptance evidence from offline localization work.
- [ ] Tests, if added in a later implementation cycle, avoid exact prose snapshots and focus on counts, targeted keys, safety constraints, and matcher behavior.
- [ ] `.coverage` is present only as a local dirty artifact if tests touched it; it is not staged or discussed as part of the deliverable.
- [ ] The final handoff separates package localization status from live RingCentral acceptance status.

## Suggested Future Verification

For this advisory handoff, a markdown diff check and git status review are enough.

For a later implementation of the language wedge, use focused offline checks only:

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language <new-language>
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language <new-language> --require-complete
git status --short
git diff --check -- packages\ringcentral-video.yaml docs\agent-handoffs\cycle-113-risk-scan.md
```

If aliases are touched, add the focused doctor command for the relevant profile and language, then review any alias substring warnings before merge. Do not run or record live RingCentral acceptance for this wedge unless a separate acceptance cycle explicitly authorizes it.
