# Cycle 176 Experience Handoff: Durable Presenter Meta Knowledge

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`
Scope: write only `docs/agent-handoffs/cycle-176-experience.md`

## Sources Read

- `docs/agent-handoffs/cycle-176-demand-analysis.md`
- `docs/agent-handoffs/cycle-176-risk-scan.md`
- `docs/agent-handoffs/cycle-176-technical-scan.md`
- `docs/agent-handoffs/cycle-175-experience.md`
- Current working diff for `docs/knowledge/ringcentral-video/runtime-safety-routing.md`
- Current working diff for `tests/unit/test_material_packages.py`
- `git status --short` and `git diff --stat`

Current workspace context: `.coverage`, `docs/knowledge/ringcentral-video/runtime-safety-routing.md`, and `tests/unit/test_material_packages.py` were already dirty, and the three Cycle176 scan docs were already untracked. Treat those as work from other agents. This pass only writes the experience handoff named above.

## When To Promote Handoff Lessons

Handoffs are good for fresh context; knowledge docs are for durable rules future agents must preserve without replaying every cycle. Promote a handoff lesson into `docs/knowledge/**` when it has become a repo-local invariant, ownership boundary, or review trigger that crosses more than one implementation slice.

Cycle176 is a good example. Cycles 174 and 175 proved the same pattern in English and Chinese: Presenter expression requests are AiPresenter runtime behavior, not RingCentralVideo product knowledge. That lesson affects routing, package ownership, safety reviews, localization, and future tests, so it belongs in `runtime-safety-routing.md`.

Do not promote every useful detail. Keep prompt matrices, exact fragment lists, temporary line numbers, uncommitted hashes, and exploratory scan wording in handoffs unless they are needed as stable maintenance rules. Durable docs should say what must remain true, who owns it, what must not be claimed, and which focused tests protect it.

## Doc Contract Test Pattern

The reusable pattern is a narrow docs-contract assertion in `tests/unit/test_material_packages.py`. The test reads a knowledge doc as text and asserts a few stable boundary phrases. This is intentionally smaller than a markdown parser or documentation linter.

Use this pattern when a knowledge doc carries a safety or ownership contract, especially one that can regress through innocent wording edits. Cycle176 extends `test_ringcentral_knowledge_docs_preserve_evidence_boundaries` with phrases that lock the Presenter meta rule:

- Presenter expression requests are runtime answer-only guards.
- They are not RingCentralVideo package aliases or Q&A.
- Pure meta requests should not produce a RingCentralVideo entrypoint.
- The docs must not claim persistent language or tone state changes.

Keep these assertions short and semantic. They should preserve the boundary, not freeze the whole paragraph. If the doc wording has to change later, update the assertion only after confirming the replacement still protects the same safety contract.

## Safety Wording Pitfalls

The main Cycle176 experience lesson is that the doc wording matters almost as much as the code boundary. A sentence that sounds slightly too strong can tell the next agent to implement the wrong layer.

Avoid saying Presenter meta requests "switch AiPresenter to Chinese", "set privacy tone", "remember beginner mode", or "update voice settings" unless a controller/session state mutation exists and is tested. The current guard answers safely; it does not persist natural-language preferences.

Avoid saying local routing tests prove live RingCentral behavior. The safe wording is repo-local: tests prove local routing boundaries only, and live RingCentral acceptance still needs dated acceptance evidence.

Avoid suggesting package YAML owns these prompts. Presenter language, tone, pacing, detail, and familiarity requests are not app facts, aliases, Q&A, localized titles, demo flows, or package metadata. Putting them in `packages/ringcentral-video.yaml` would blur product knowledge with Presenter behavior and create package count and localization diagnostic churn.

For Chinese and other CJK prompts, keep the documentation warning phrase-level. Bare words for language, tone, safety, privacy, status, or pacing can steal real RingCentralVideo routes such as meeting-info, encryption, host controls, recording, chat, participants, share, invite, leave, notes, transcript, or full screen. Mojibake should stay unsupported instead of becoming a new implicit alias.

## Next-Cycle Backlog

- Run the focused docs-contract tests after the current knowledge/test diff is complete:
  `tests/unit/test_material_packages.py::test_ringcentral_knowledge_docs_preserve_evidence_boundaries`
  and `tests/unit/test_material_packages.py::test_ringcentral_knowledge_docs_are_registered_in_navigation_indexes`.
- Run `git diff --check -- docs\knowledge\ringcentral-video\runtime-safety-routing.md tests\unit\test_material_packages.py docs\agent-handoffs\cycle-176-experience.md` before handoff.
- Review the new `runtime-safety-routing.md` section for accidental overclaims about live RingCentral acceptance, persistent voice state, or package YAML ownership.
- Add controller/session interrupt sentinel coverage only in a future source/test slice if agents need to prove Presenter meta prompts never enqueue `question-answer-demo`.
- Keep broader multilingual Presenter meta coverage as later, prompt-set-driven slices with route-risk tests.
- Do not change package YAML, package counts, localization diagnostics, source routing, staging, or commits unless a future assignment explicitly owns them.

## Status

Cycle176 experience handoff complete. The durable lesson is to promote repeated handoff learnings into knowledge docs only when they become stable maintenance contracts, then guard the contract with small literal docs tests and careful safety wording.

Changed file path:

- `docs/agent-handoffs/cycle-176-experience.md`
