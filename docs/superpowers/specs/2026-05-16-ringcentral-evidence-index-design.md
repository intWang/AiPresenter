# RingCentral Evidence Index Design

Date: 2026-05-16

## Context

The RingCentral Video knowledge package now has separate documents for source scope, live observations, locator confidence, state coverage, privacy policy, acceptance runs, and manual acceptance. These files are valuable, but the next validation target is hard to choose because evidence is spread across several tables.

## Design

Create `docs/knowledge/ringcentral-video/evidence-index.md` as a navigation and decision index. It should not replace the existing source documents. Instead, it should point to them and answer:

- Which RingCentral Video surfaces have live evidence?
- Which package entrypoints are executable, explain-only, or still risky?
- Which locator/cleanup routes most need manual validation next?
- Which privacy rule applies before a surface can become executable?
- What should the next live/manual acceptance run record?

The index will use stable package entrypoint IDs as anchors. It will group rows by validation priority rather than by YAML order, because future agents need a work queue more than a catalog.

## Evidence Levels

- `Accepted`: automated tests plus dated live/manual acceptance for the current build and route.
- `Observed`: dated read-only or manual observation exists, but no click/cleanup acceptance.
- `Repo-tested`: package schema/tests cover the route, but no current live evidence.
- `Backlog`: official/product scope or explain-only knowledge exists, but the route is intentionally not executable.
- `Blocked`: privacy, role, confirmation, or missing locator prevents execution.

## Acceptance Criteria

- The evidence index exists and links to the current knowledge docs.
- Every current RingCentral package entrypoint is represented directly or by an explicit grouped row.
- High-priority validation targets include Add coworkers, top-bar coordinate routes, More occurrence routes, Chat/Participants/Invite/Share cleanup, Notes variants, Background/Settings close behavior, and queued Chat question acceptance.
- Privacy-sensitive surfaces reference the privacy matrix policy.
- The index includes a small maintenance checklist for future observations.
- Lightweight doc checks verify the index exists, has no placeholder markers, and mentions every package entrypoint ID.

## Non-Goals

- No live RingCentral clicks or screenshots in this cycle.
- No package YAML route changes in this cycle.
- No new official-source research unless a doc gap blocks the index.
- No rewrite of existing knowledge docs.

## Risks

- A summary index can become stale if future agents update locator/state docs but not the index.
- Over-aggregating rows can hide specific entrypoint risks.
- The index must keep checklist items distinct from actual acceptance evidence.
