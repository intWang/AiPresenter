# Cycle 008 Demand Analysis: Package Runtime Index

Date: 2026-05-16
Role: demand-analysis sidecar
Write scope: this file only

## Read Scope

Reviewed local repo evidence only. No production code was modified.

- `README.md`
- `docs/agent-handoffs/cycle-004-demand-analysis.md`
- `docs/agent-handoffs/cycle-005-summary.md`
- `docs/agent-handoffs/cycle-006-summary.md`
- `docs/agent-handoffs/cycle-006-implementation.md`
- `docs/agent-handoffs/cycle-007-summary.md`
- `docs/agent-handoffs/cycle-007-implementation.md`
- `docs/agent-handoffs/cycle-007-review.md`
- `docs/runbooks/ringcentral-manual-acceptance.md`
- `docs/superpowers/plans/2026-05-16-timing-telemetry.md`
- `packages/ringcentral-video.yaml`
- `src/ai_presenter/packages/models.py`
- `src/ai_presenter/runtime/questions.py`
- `src/ai_presenter/runtime/package_demo.py`
- `src/ai_presenter/runtime/session.py`
- `src/ai_presenter/runtime/material_runtime.py`
- `src/ai_presenter/runtime/temporary_package.py`
- focused unit tests around material packages, questions, controller sessions, temporary packages, and package actions

The working tree was already dirty before this handoff. I treated all existing modified and untracked files as other agents' work and did not revert or overwrite them.

## Current Context

Cycle 005 made controller state more trustworthy through a pure operator view model. Cycle 006 moved the first multilingual question slice into package data with package-owned `questionAliases`, localized Q&A questions, and localized answers. Cycle 007 added privacy-safe timing logs around exactly the two runtime areas that now matter for this candidate: `answer_question()` and `PackageActionExecutor.execute_action()`.

The current RingCentral package is not huge: a read-only loader probe reported `entrypoints=27`, `demo_flows=4`, `qa=3`, and `explainers=21`. That means a runtime index is unlikely to produce dramatic human-visible latency for the curated RingCentral package alone. The stronger need is future-proofing the hot paths that now serve both prepared packages and generated running-app packages, where visible controls can make `operationEntryPoints` much larger and where users may ask repeated questions during a live demo.

## User-Facing Need

The user need is confidence under live interruption:

- A typed question should feel instant and should not get slower as RingCentral coverage or generated running-app packages grow.
- Safe question-driven actions should resolve the intended control reliably, then queue or execute without a second round of avoidable package scanning.
- Controller feedback should remain responsive while the operator asks multiple questions in sequence.
- Performance work should not loosen the safety boundary: risky controls such as leave, share, record, mute, invite, reactions, and toggles must remain answer-only unless a later confirmed-action policy explicitly changes that.

This is not a new UX feature. It is a runtime plumbing increment that protects the UX created in Cycles 005-007.

## Evidence From Repo

- `src/ai_presenter/packages/models.py` validates duplicate operation entrypoint IDs by building a local dictionary, but `MaterialPackage.entrypoint_by_id()` still performs a linear scan each call.
- `src/ai_presenter/runtime/package_demo.py` calls `entrypoint_by_id()` for each executable action, and `demo_flow_by_id()` scans `package.demo_flows`.
- `src/ai_presenter/runtime/session.py` calls `entrypoint_by_id()` again while turning a question response into an interrupt step.
- `src/ai_presenter/runtime/questions.py` scans Q&A and entrypoints on every question:
  - Q&A substring match scans all Q&A questions and localized questions.
  - Q&A token fallback recomputes question tokens on each call.
  - Package alias matching scans every entrypoint's `question_aliases` on each call.
  - Entry point scoring recomputes title, id, area, and purpose tokens on each call.
  - Legacy alias fallback scans a static Python alias table and then calls `entrypoint_by_id()`.
- `src/ai_presenter/runtime/temporary_package.py` can create one operation entrypoint per visible control in a selected desktop app. That is the likely growth path where linear matching becomes more noticeable.
- Cycle 007 timing telemetry now gives implementation agents a place to compare before/after behavior without logging private question text or UI target labels.

## Recommendation

Yes: this is the right next performance increment, if the scope stays narrow.

Recommended Cycle 008 shape: create a package runtime index or index-backed helper for entrypoint, flow, Q&A, and alias lookup, then wire the existing hot question/action paths through it while preserving behavior exactly. Do not broaden safety policy, redesign the controller, or replace the timing logger in this cycle.

Why this is a good increment now:

- It directly follows Cycle 007's telemetry work.
- It is mostly pure Python data-shaping, so it can be tested without desktop automation.
- It benefits both curated RingCentral packages and generated running-app packages.
- It reduces repeated tokenization and repeated ID scans in the paths users hit while asking live questions.

Why it should remain modest:

- The current RingCentral package is small enough that the absolute speedup may be minor.
- UIA scanning, desktop binding, TTS, and audio playback may still dominate perceived latency.
- A broad cache layer could create staleness and behavior drift. Build an immutable per-package runtime index instead of global mutable caches.

## Likely Workflows Affected

- Controller text questions in Material package mode.
- Controller text questions in Running desktop app mode after Scan creates a temporary package.
- Question interrupt creation for safe, operable answers while a demo is running.
- Package action execution from scripted demo steps and question interrupts.
- CLI material demo startup paths that resolve package flows.
- Diagnostics and tests that call `entrypoint_by_id()` or `demo_flow_by_id()`.

## Suggested Acceptance Criteria

1. Behavior parity:
   - All existing question matching tests keep passing.
   - Package-owned aliases still take precedence over legacy aliases.
   - Longest package-owned alias still wins.
   - Localized Q&A questions and localized answers still work.
   - Mojibake Chinese input remains unsupported.
   - Risky matched controls remain `can_operate=False`.

2. Indexed lookup:
   - Entry point lookup by ID is backed by a precomputed mapping, not a fresh scan.
   - Flow lookup by ID is backed by a precomputed mapping or equivalent package helper.
   - Question matching reuses precomputed Q&A phrase candidates, package alias candidates, and entrypoint token fields for a package.
   - Temporary packages get the same indexed path as curated packages.

3. Runtime compatibility:
   - Existing public call sites can keep their current surface, or any new helper is introduced with minimal churn.
   - Pydantic model validation still rejects duplicate entrypoint IDs and unknown related IDs.
   - Index construction does not mutate package-authored lists or dictionaries in ways that surprise tests or callers.

4. Telemetry and privacy:
   - Existing `question_answered` and `package_action_executed` telemetry fields remain unchanged.
   - No user question text, generated answer text, exception text, or UI target labels are added to logs.
   - If before/after timing evidence is recorded, it uses synthetic or metadata-only data.

5. Performance evidence:
   - Add a focused synthetic-package regression or benchmark-style test that demonstrates repeated question and action lookups reuse indexed data.
   - Prefer deterministic evidence over brittle wall-clock thresholds. For example, prove token fields or ID maps are built once per index, then use a local timing probe as handoff evidence rather than a hard CI assertion.

6. Verification:
   - Focused tests for models/package index, questions, package demo, session, and temporary package pass.
   - Full unit test suite passes with only known environmental warnings.
   - `ruff`, `mypy`, and `git diff --check` pass for touched files.

## Risks

- Match drift: precomputing tokens can accidentally change tie-breaking, especially for generic tokens such as `people`, settings/background ambiguity, or package alias length precedence.
- Safety drift: faster lookup must not bypass `_can_operate()` or the open-step requirement used by `create_question_interrupt_step()`.
- Stale index: if an index is cached globally and a package object is mutated in tests or future runtime code, lookups could be wrong. An immutable helper passed with the package is safer than process-global caching.
- Schema coupling: adding private attrs or computed fields directly to Pydantic models may interact poorly with validation, serialization, or test fixtures. A small runtime helper module may be lower risk.
- Premature optimization: if live slowness is dominated by UIA scan/TTS/audio, this work may not be the biggest visible win. The value is still defensible because it is low-risk and protects scaling.
- Legacy alias debt: the static `_ENTRYPOINT_ALIASES` table remains a fallback. Indexing should not cement that table as the long-term localization model.

## Suggested Implementation Direction

Favor a small runtime index module over a broad refactor. A likely shape:

- `PackageRuntimeIndex` built from `MaterialPackage`.
- `entrypoint_by_id: dict[str, OperationEntrypoint]`.
- `flow_by_id: dict[str, DemoFlow]`.
- `qa_candidates` containing each Q&A item, all English/localized question strings, normalized strings, and meaningful token sets.
- `entrypoint_candidates` containing each entrypoint and precomputed title/id/area/purpose token sets.
- `package_alias_candidates` sorted or compared by normalized alias length, preserving longest-match behavior.

Then update hot paths conservatively:

- `questions.answer_question()` can build/use an index and delegate matching to index-backed helpers.
- `package_demo.demo_flow_by_id()` and `PackageActionExecutor` can use package/index helpers for ID lookup.
- `session.create_question_interrupt_step()` should use the same indexed entrypoint lookup only if it does not force larger API churn.

If implementation agents prefer to keep `MaterialPackage.entrypoint_by_id()` as the compatibility surface, they can add an internal map while preserving current exceptions. The key is to avoid repeated linear scans and repeated tokenization without forcing unrelated production-code changes.

## Not Recommended For This Cycle

- Do not redesign the Tk controller.
- Do not change risky-action or confirmation policy.
- Do not migrate all legacy Chinese aliases into the package.
- Do not introduce a metrics backend or structured logging replacement.
- Do not optimize UIA scanning in the same cycle unless this candidate stalls.

## Read-Only Commands Used

```powershell
git status --short
rg --files
Get-ChildItem -Force docs\agent-handoffs
rg -n "runtime|entrypoint|alias|question|action|scan|linear|hot path|telemetry|timing|operator|controller" .
Get-Content -Raw docs\agent-handoffs\cycle-007-summary.md
Get-Content -Raw docs\agent-handoffs\cycle-007-implementation.md
Get-Content -Raw docs\agent-handoffs\cycle-007-review.md
Get-Content -Raw docs\agent-handoffs\cycle-004-demand-analysis.md
rg -n "def answer_question|def _answer_question|def _match|def _tokens|questionAliases|question_aliases|operation_entrypoints|entrypoint_by_id|related_entrypoint_ids|for .*entrypoints|for .*qa|QAItem|OperationEntrypoint" src\ai_presenter\runtime\questions.py src\ai_presenter\packages\models.py tests\unit\test_questions.py tests\unit\test_material_packages.py
rg -n "def demo_flow_by_id|entrypoint_by_id|operation_entrypoints|execute_action|PackageActionExecutor|for .*demo_flows|for .*operation_entrypoints" src\ai_presenter\runtime\package_demo.py src\ai_presenter\runtime\controller.py src\ai_presenter\runtime\session.py tests\unit\test_package_demo.py tests\unit\test_controller.py
Get-Content -Raw src\ai_presenter\runtime\questions.py
Get-Content -Raw src\ai_presenter\runtime\package_demo.py
Get-Content -Raw src\ai_presenter\packages\models.py
Get-Content -Raw src\ai_presenter\runtime\session.py
Get-Content -Raw src\ai_presenter\runtime\material_runtime.py
Get-Content -Raw docs\superpowers\plans\2026-05-16-timing-telemetry.md
Get-Content -Raw src\ai_presenter\runtime\temporary_package.py
rg -n "operationEntrypoints:|  - id:|questionAliases:|localizedQuestions:|localizedAnswers:|qa:|demoFlows:" packages\ringcentral-video.yaml
Get-Content -Raw tests\unit\test_questions.py
Get-Content -Raw tests\unit\test_material_packages.py
Get-Content -Raw README.md
.\.venv\Scripts\python -c "from pathlib import Path; from ai_presenter.packages.loader import load_material_package; p=load_material_package(Path('packages/ringcentral-video.yaml')); print(f'entrypoints={len(p.operation_entrypoints)} demo_flows={len(p.demo_flows)} qa={len(p.qa)} explainers={len(p.explainers)} package={p.app_id}')"
Test-Path docs\agent-handoffs\cycle-008-demand-analysis.md
rg -n "entrypoint_by_id\(|demo_flow_by_id\(|answer_question\(|execute_action\(|question_aliases|operation_entrypoints" src tests docs\agent-handoffs\cycle-007-summary.md docs\runbooks\ringcentral-manual-acceptance.md
Get-Content -Raw docs\runbooks\ringcentral-manual-acceptance.md
Get-Content -Raw docs\agent-handoffs\cycle-006-summary.md
Get-Content -Raw docs\agent-handoffs\cycle-006-implementation.md
Get-Content -Raw docs\agent-handoffs\cycle-005-summary.md
```
