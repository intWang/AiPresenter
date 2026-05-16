# Cycle 111 Risk Scan: RingCentral Video Knowledge-Package Consolidation

Date: 2026-05-16
Scope: documentation-only risk/review scan. Do not edit production code, tests, or `packages/ringcentral-video.yaml` as part of this handoff.

## Verdict

Go, with guardrails, for a narrow documentation consolidation that makes the RingCentral Video safety and localization knowledge easier to review.

No-go for any update that changes package YAML, copies large package data into docs, claims new runtime behavior, or turns recent cycle handoffs into a broad evergreen product manual. The consolidation should be a source map and review checklist, not a second implementation of the package.

The safest shape is:

- Keep package facts anchored to `packages/ringcentral-video.yaml`, current CLI reports, and tests.
- Keep runtime safety behavior anchored to named gates such as `questionPolicy: answerOnly`, `_can_operate(...)`, Q&A-first matching, and `create_question_interrupt_step(...)`.
- Keep localization counts as dated verification output, not prose promises.
- Keep tone behavior documented as style-only; it must not imply policy, authorization, or compliance validation.

## Risks By Severity

| Severity | Risk | Failure mode | Impact | Guardrail |
| --- | --- | --- | --- | --- |
| P0 | Docs claim behavior code does not enforce | A consolidated doc says Meeting information, Notes/Transcript, recording, invite, share, participants, chat, or transcript prompts are always safe without citing the current routing gates and tests. | Reviewers may trust stale prose over runtime code, and future changes may weaken safety unnoticed. | Every runtime-safety claim must cite a source anchor: `packages/ringcentral-video.yaml`, `src/ai_presenter/runtime/questions.py`, `src/ai_presenter/runtime/session.py`, and focused `tests/unit/test_questions.py` coverage. |
| P0 | Package YAML duplication | The doc copies entrypoint, alias, Q&A, flow, or localized narration content from `packages/ringcentral-video.yaml`. | Docs become a stale shadow package; future YAML edits create conflicting truths. | Summarize only counts, policies, evidence status, and review rules. Link to package YAML for details. |
| P0 | Localization count drift | The doc states Chinese/Japanese counts from memory or prior cycles after aliases or Q&A changed. | Operators may approve incomplete or regressed localized demos. | Treat counts as dated command output. Regenerate `localization-report` for any doc update that mentions counts. |
| P0 | Tone described as safety policy | `careful`, `privacy`, `safety`, `guarded`, or `compliance` are documented as making operations safer or changing eligibility. | Users may believe tone selection changes authorization or compliance status. | State that tone is a rendering/style layer only. Route, `can_operate`, `questionPolicy`, and interrupt creation must be tone-invariant. |
| P1 | Safety routing overgeneralized | Notes/Transcript hardening is documented as a general ability to classify all private meeting content. | Product behavior is overclaimed; unseen prompts may be assumed covered. | Describe only known guarded prompt classes and say new sensitive prompt families require tests before being documented as protected. |
| P1 | Evidence hierarchy blurred | Official RingCentral docs, repo package data, UI observations, runbooks, and acceptance runs are presented as equally strong evidence. | A product feature can look executable without local observation or acceptance evidence. | Preserve the source hierarchy: official docs scope product features; local package/tests describe AiPresenter behavior; live observations and `acceptance-runs.md` provide current-build evidence. |
| P1 | Review checklist too broad to maintain | The consolidation tries to cover all RingCentral Video product surfaces, every prior cycle, and future backlog in one doc. | Reviewers stop using it, and stale sections accumulate. | Keep the document focused on safety-routing, localization counts, tone behavior, verification commands, and links to existing knowledge docs. |
| P1 | Verification commands copied without scope | The doc recommends full-suite or live RingCentral validation for small doc-only updates. | Verification becomes expensive and ignored; unrelated `.coverage` or live-environment churn leaks into docs review. | For doc-only updates, require scope/diff checks and CLI report regeneration only when counts are stated. Reserve tests or live acceptance for behavior/package changes. |
| P2 | Implementation detail leakage | The doc explains helper internals, matcher term lists, or test fixture strings in detail. | Maintainers must update docs for harmless refactors, and sensitive routing rules become noisy. | Name the behavior gates and tests; avoid duplicating private matcher dictionaries or prompt matrices unless the doc is specifically a risk scan for those terms. |
| P2 | Stale-cycle citation sprawl | The consolidation quotes many cycle handoffs without identifying which facts are still current. | Old risk notes become indistinguishable from current code. | Prefer current knowledge docs and command output. Use recent cycle handoffs as rationale, not as authoritative present-tense facts. |
| P2 | Encoding false confidence | CJK examples are reviewed only through mojibake-prone terminal output. | Reviewers may approve broken or unintended Chinese/Japanese strings. | Prefer CLI summaries for counts and source/test files for literal CJK text; avoid judging correctness from a garbled console transcript. |

## Required Factual Anchors

Use these anchors before approving any knowledge-package documentation update.

| Topic | Required anchor | What the doc may safely say |
| --- | --- | --- |
| Package scope | `packages/ringcentral-video.yaml` plus `docs/knowledge/ringcentral-video/source-index.md` | The package is the source of truth for entrypoints, flows, Q&A, localized text, aliases, and `questionPolicy`. Docs may summarize counts and policy roles, not duplicate full YAML. |
| Meeting information safety | `packages/ringcentral-video.yaml` has `ringcentral.video.top.meeting-info` with `questionPolicy: answerOnly`; `_can_operate(...)` checks `question_policy`; `create_question_interrupt_step(...)` returns no step when `can_operate` is false. | Meeting information questions may identify the entrypoint while staying answer-only; docs must not claim AiPresenter can read or expose live meeting IDs, links, host names, dial-in numbers, or E2EE state from private context. |
| Notes/Transcript safety | `packages/ringcentral-video.yaml` has `ringcentral.video.more.notes` with `questionPolicy: answerOnly`; `questions.py` has Notes/Transcript safety matching; tests assert no interrupt for action/content prompts and preserve location lookups. | Notes/Transcript can be documented as explain/location-safe under known tested prompts, not as a capability to start notes, read transcript content, summarize, copy, save, or export artifacts. |
| Q&A-first and safety routing | `answer_question(...)` routes exact Q&A and safety matches before entrypoint matching; focused tests cover recording, notes/transcript, meeting info, invite, share, participant/chat privacy, and leave routes. | Runtime safety is a set of ordered gates and tests, not a single product-wide guarantee. |
| Tone behavior | `src/ai_presenter/runtime/voice.py` defines canonical tones: `professional`, `conversational`, `concise`, `friendly`, `coach`, `formal`, `support`, `careful`; aliases such as `privacy`, `safety`, `safe`, `guarded`, and `compliance` normalize to `careful`. | Tone may change wording, prefixes, labels, or pacing only after routing/eligibility is decided. It must not change `entrypoint_id`, `can_operate`, `questionPolicy`, or interrupt creation. |
| Localization counts | Current CLI output from this scan: `zh` has `51/51` demo steps, `12/12` Q&A questions, `12/12` Q&A answers, and `questionAliases.zh` on `15/27` entrypoints with `49` aliases. `ja` has `51/51` demo steps, `12/12` Q&A questions, `12/12` Q&A answers, and `questionAliases.ja` on `13/27` entrypoints with `34` aliases. | Counts may be stated only with the command and date. If any package, package-loading, Q&A, alias, or localization code changes, rerun the reports before updating docs. |
| Evidence status | `docs/knowledge/ringcentral-video/evidence-index.md`, `observation-log.md`, `acceptance-runs.md`, and `validation-checklist-index.md` | Live UI behavior must be labeled by evidence type: procedure, read-only observation, accepted run, or unvalidated backlog. A runbook checklist is not acceptance evidence until recorded as a run. |
| Verification | `tests/unit/test_questions.py`, `tests/unit/test_material_packages.py`, `tests/unit/test_cli.py`, CLI `localization-report`, and focused risk-scan commands | Docs can recommend verification clusters, but should distinguish doc-only review from behavior/package verification. |

## Doc Anti-Patterns To Avoid

- Do not paste package YAML entrypoints, `openSteps`, aliases, Q&A bodies, or localized narration into docs.
- Do not state "RingCentral Video supports" when the claim really means "official docs mention" or "AiPresenter package describes".
- Do not state "AiPresenter safely handles all transcript/notes/chat/participant/meeting-info prompts." State the tested prompt class and the gate that protects it.
- Do not make `careful` or `privacy` sound like a compliance mode, consent detector, or private-data validator.
- Do not update localization numbers without pasting or citing the exact `localization-report` command output date.
- Do not use old cycle handoffs as present-tense truth when current code, package YAML, or knowledge docs have a stronger anchor.
- Do not convert risk scans into a broad RingCentral Video manual. Product-scope references belong in `source-index.md`; executable evidence belongs in observation and acceptance docs.
- Do not claim live UI acceptance from unit tests, dry runs, or runbook checklist items.
- Do not bury no-go conditions below narrative history; reviewers need them near the top.
- Do not add private matcher term lists or exact sensitive prompt inventories unless the doc is explicitly a term-risk review.

## Go / No-Go

Go if the Cycle 111 documentation update:

- Touches only documentation files approved for the consolidation.
- Keeps `packages/ringcentral-video.yaml`, production code, and tests unchanged.
- Uses current source anchors for each runtime-safety, localization, tone, and verification claim.
- Labels counts as dated evidence and keeps the exact command available to rerun.
- Describes safety behavior as route/eligibility/interrupt invariants, not as broad product capability.
- Points readers to existing knowledge docs instead of replacing them.

No-go if the update:

- Edits package YAML, production code, tests, profiles, or generated artifacts.
- Duplicates package data or localized copy in docs.
- Claims new runtime behavior without matching code/test evidence.
- Changes or rationalizes localization counts without running the report.
- Implies tone changes authorization, safety policy, compliance, or consent handling.
- Presents official RingCentral documentation as proof that AiPresenter can operate a route.
- Treats a runbook procedure as dated acceptance evidence.

## Review Checklist

Use this checklist before approving the consolidation PR or handoff.

- [ ] Diff scope is documentation-only and does not touch `packages/ringcentral-video.yaml`, production code, tests, profiles, generated coverage, or live artifacts.
- [ ] Every runtime-safety statement names at least one current anchor: `questionPolicy: answerOnly`, `_can_operate(...)`, Q&A-first matching, risky route tests, or `create_question_interrupt_step(...)`.
- [ ] Meeting information and Notes/Transcript are described as answer-only for question mode; the doc does not imply opening, reading, copying, exporting, summarizing, or verifying private meeting artifacts.
- [ ] Tone language says `professional`, `conversational`, `concise`, `friendly`, `coach`, `formal`, `support`, and `careful` are style choices; aliases such as `privacy` normalize to `careful` and do not change routing.
- [ ] Localization counts are either omitted or tied to fresh `localization-report` output for both `zh` and `ja`.
- [ ] Any stated Chinese/Japanese counts match current report output: `zh` aliases `15/27` entrypoints and `49` aliases; `ja` aliases `13/27` entrypoints and `34` aliases; both languages have `51/51` demo steps and `12/12` localized Q&A questions/answers.
- [ ] The document distinguishes product-scope sources, package knowledge, unit-test behavior, manual procedure, read-only observation, and accepted live evidence.
- [ ] The doc links to `source-index.md`, `evidence-index.md`, `validation-checklist-index.md`, `observation-log.md`, and `acceptance-runs.md` where appropriate instead of copying their contents.
- [ ] Verification guidance is scoped: doc-only changes require diff/source review; package/localization changes require material-package and localization checks; runtime routing/tone changes require focused question/voice tests.
- [ ] No broad, evergreen maintenance burden is introduced. Any future-work list is short and points to the owning knowledge doc.
- [ ] No stale handoff fact is used as current truth unless it is still backed by code, package YAML, a current knowledge doc, or a dated command output.
- [ ] The final recommendation remains explicit: go only under the documentation-only guardrails; no-go for behavior, YAML, localization, or tone-policy drift.

## Recommended Verification For This Doc-Only Slice

For this risk scan, I ran:

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language zh
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ja
```

Before merging any later documentation consolidation that repeats counts, rerun those commands and update the dated evidence. If a later change touches package YAML, package loading, question routing, tone rendering, or tests, add focused verification such as:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\unit\test_material_packages.py tests\unit\test_cli.py::test_localization_report_outputs_chinese_demo_and_qa_coverage tests\unit\test_cli.py::test_localization_report_outputs_japanese_demo_and_qa_coverage -q -o addopts=""
.\.venv\Scripts\python.exe -m pytest tests\unit\test_questions.py tests\unit\test_voice.py -q -o addopts=""
```

Do not use these commands to imply live RingCentral Video acceptance. Live evidence still belongs in `docs/knowledge/ringcentral-video/acceptance-runs.md`.
