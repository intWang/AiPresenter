# Cycle 115 Demand Analysis: Repo-Local Maintainability Playbook

Date: 2026-05-16
Scope: demand analysis only. This file is the only file edited by this handoff.

## Product And Maintainer Demand

AiPresenter has reached the point where optimization is no longer only about adding the next RingCentral Video route, language wedge, docs guard, or runtime performance improvement. The repo now has enough repeated maintenance patterns that future agents need a compact, repo-local way to decide what kind of artifact a cycle should produce before they start changing code.

Recent cycles show stable patterns:

- RingCentral Video safety routing must keep Q&A-first, answer-only, blocked, observed, repo-tested, and accepted evidence distinct.
- Localization wedges must preserve partial-versus-complete language status, avoid live-readiness claims, and update counts deliberately.
- Docs navigation guards must protect canonical knowledge discoverability without turning the repo into a general docs-lint project.
- Runtime performance hygiene should prefer behavior-preserving internal indexes, deterministic structural tests, and narrow timing notes over flaky wall-clock gates.
- `.coverage` is a known local dirty artifact and must not be staged.

The demand is for a maintainability decision guide that future agents can find in the repo, review in a normal PR, and use before proposing more implementation cycles. This is adjacent to Codex skill optimization, but it should start as a repo artifact rather than a global Codex skill.

## Artifact Options Considered

| Option | Commitability | Verification | Future Discoverability | Risk | Fit For Cycle 115 |
| --- | --- | --- | --- | --- | --- |
| Real Codex skill in Codex home | Poor for this repo; it lives outside the project and is not naturally reviewed with AiPresenter changes. | Hard to verify from repo CI or focused tests. | Low for future repo readers unless their local Codex home matches. | High: global behavior drift, hidden coupling, and current cycle constraints forbid editing Codex home skills. | No-go. |
| Repo-local Codex skill scaffold | Commitable if a `.codex` or plugin convention is introduced, but this repo currently has no local skill distribution pattern. | Mostly structural until Codex loads it; verification would be tool-environment-specific. | Medium, but only for Codex users who know where to look. | Medium: adds tool-specific infrastructure before proving the content. | Not first. |
| Skill candidate/spec only | Easy to commit under `docs/superpowers/specs/` or a handoff. | Markdown-only review. | Medium; it can be lost among many specs unless indexed. | Low, but it delays immediate operational value. | Useful as a section, not the whole slice. |
| Repo-local maintainability playbook | Easy to commit as a docs/runbook file. | Markdown diff check plus grep-based content checks; no production behavior risk. | High if linked from README or future handoffs and named for agents. | Low: documentation-only and repo-owned. | Recommended. |
| Another narrow RingCentral or performance artifact | Commitable and verifiable, but repeats recent cycle themes instead of addressing the cross-cycle pattern. | Depends on artifact. | Narrow. | Low to medium. | Lower priority for Cycle 115. |

## Recommendation

Cycle 115 should create a repo-local maintainability playbook, not a real Codex skill.

Recommended future file:

- `docs/runbooks/agent-maintainability-playbook.md`

Optional future link target, only if that implementation cycle is allowed to edit README:

- `README.md`, under the existing project/runbook area, with one link to the playbook.

The playbook should be a practical decision guide for future agents. It should not duplicate every prior handoff. Its job is to distill the repeated maintenance rules into a small set of checks that help an agent choose the right next artifact: code change, package YAML change, docs knowledge update, runbook update, demand analysis, risk scan, or skill candidate.

## Why Not A Real Codex Skill Yet

A real Codex skill is useful only when the behavior should follow the agent across repositories or when the repo has a stable local skill packaging convention. AiPresenter is not there yet for maintainability guidance.

Reasons to defer:

- Current instructions explicitly forbid editing Codex home skills.
- A global skill would be hard to review, commit, or roll back with AiPresenter.
- The repeated patterns are still repo-specific: RingCentral Video evidence levels, package localization counts, profile/provider compatibility, and `.coverage` handling.
- The safest path is to make the guidance visible to any contributor first, then promote a narrow candidate to a real skill only after the repo playbook proves durable.

The playbook can include a "Codex Skill Candidates" section. That section should list candidate skills and graduation criteria without creating or installing any skill.

## Recommended One-Cycle Slice

Future Cycle 115 implementation should create one concise playbook with these sections:

- Purpose: define the playbook as a pre-change decision aid for AiPresenter agents.
- Artifact chooser: when to create a demand analysis, implementation handoff, risk scan, test review, runbook, knowledge doc, package YAML change, production-code change, or skill candidate.
- RingCentral Video safety maintenance rules: preserve safety routing, evidence language, privacy boundaries, cleanup expectations, and live-acceptance separation.
- Localization wedge rules: count changes, partial-versus-complete language wording, voice/provider compatibility, and report verification.
- Docs navigation rules: canonical RingCentral knowledge belongs under `docs/knowledge/ringcentral-video/` and must remain indexed.
- Runtime performance hygiene rules: behavior parity first, structural tests over wall-clock assertions, local timing notes only as supporting evidence.
- Verification and staging checklist: focused tests, `git diff --check`, `git status --short`, and explicit `.coverage` exclusion.
- Skill candidate register: candidate names, trigger conditions, repo evidence required before promotion, and why none should edit Codex home during normal cycles.

Keep the playbook short enough to be read before an implementation cycle. A good target is roughly 120 to 180 lines.

## Acceptance Criteria

A future Cycle 115 implementation satisfies this demand when:

- `docs/runbooks/agent-maintainability-playbook.md` exists and is the main new artifact.
- The playbook gives future agents a clear chooser for at least these artifact types: demand analysis, implementation handoff, risk scan, test review, runbook, canonical knowledge doc, package YAML change, production-code change, and skill candidate.
- It names the recurring AiPresenter guardrails:
  - RingCentral Video safety routing and evidence-level precision;
  - localization wedge count discipline and live-acceptance separation;
  - docs navigation/discoverability guards;
  - performance changes that preserve behavior and avoid flaky timing gates;
  - `.coverage` must not be staged.
- It recommends repo-local skill candidates only as candidates, with explicit graduation criteria before any real Codex skill is created.
- If README is edited in the implementation cycle, the edit is one small discoverability link only; no setup, CLI, or product behavior docs are rewritten.
- Verification includes `git diff --check` over the playbook and any README link, plus `git status --short` to prove `.coverage` remains unstaged.
- The implementation does not edit production code, package YAML, tests, profiles, coverage files, git history, or Codex home skills.

## Non-Goals

- Do not create or install a real Codex skill in Cycle 115.
- Do not create a repo-local `.codex` skill directory unless a later cycle first designs and verifies a repo-local skill-loading convention.
- Do not change presenter runtime skills under `presenter/skills/` or `src/ai_presenter/presenter/skills/`.
- Do not edit `packages/ringcentral-video.yaml`, source code, tests, profiles, generated coverage, or git history.
- Do not promote live RingCentral acceptance evidence or imply that docs-only playbook work validates live app behavior.
- Do not convert the playbook into a full contribution guide, style guide, or general agent handbook.
- Do not stage `.coverage`.

## Likely File Locations For Future Implementation

Preferred:

- Create `docs/runbooks/agent-maintainability-playbook.md`.

Optional, only if discoverability is explicitly included in the implementation scope:

- Edit `README.md` with one link to `docs/runbooks/agent-maintainability-playbook.md`.

Avoid:

- `.codex/`, `C:\Users\rcadmin\.codex\skills\`, `presenter/skills/`, `src/ai_presenter/presenter/skills/`, `packages/`, `profiles/`, `src/`, and `tests/`.

## Review Focus

Reviewers should check that the future playbook:

- Gives operational choices instead of restating history.
- Does not conflict with existing RingCentral Video knowledge docs, especially `runtime-safety-routing.md`, `privacy-matrix.md`, `evidence-index.md`, and `source-index.md`.
- Keeps skill guidance as candidate/spec guidance, not a hidden global Codex behavior change.
- Uses precise evidence language and never converts repo-tested or observed work into live accepted work.
- Keeps verification lightweight and documentation-appropriate.
- Leaves `.coverage` unstaged.

## Handoff Notes

The next maintainability improvement should be boring in the best way: one readable repo-local playbook, easy to review, easy to link, and easy for future agents to use before they reach for a broader artifact. If the playbook proves useful across several cycles, a later demand analysis can promote one narrow section into a real Codex skill with a separate design, install path, and verification story.
