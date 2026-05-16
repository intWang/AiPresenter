# Cycle 114 Demand Analysis: Faster RingCentral Doctor Diagnostics

Date: 2026-05-16
Scope: demand analysis only. This file is the only file edited by this handoff.

## Product Demand

AiPresenter's recent RingCentral Video cycles increased package language, alias, and safety coverage. That improves usefulness, but it also increases the amount of package-owned data inspected by `doctor`: every package diagnostic run now evaluates `27` entrypoints, `90` package-owned aliases, and `73` Q&A prompt candidates for duplicate aliases, duplicate Q&A prompts, unsafe exact alias overlap, and substring-risk reporting.

The highest-value small performance improvement for Cycle 114 is to reduce repeated diagnostics indexing work inside `src/ai_presenter/runtime/diagnostics.py` without changing any diagnostic output, route behavior, package content, or localization counts.

Why this target now:

- `doctor` is a frequent safety and readiness command after localization/package changes.
- RingCentral Video package scale has grown through Chinese, Japanese, and Spanish alias/Q&A work, so diagnostic scans will keep getting more expensive if each check rebuilds the same lookup maps independently.
- Question matching hot paths already use precomputed package indexes; diagnostics is now the more obvious repeated-work surface.
- The change can be implemented and verified in one cycle with focused unit tests plus a small in-process timing guard.
- The user-visible behavior should remain byte-for-byte equivalent for existing successful, warning, info, and failure cases.

Current local probe from this demand cycle:

```text
entrypoints: 27
package-owned aliases: 90
Q&A prompt candidates: 73
200 in-process diagnose_configuration(...) calls: about 1932.69 ms
doctor status: 11 ok, 1 info, 0 warnings, 0 failed
```

Treat the timing as a baseline for relative comparison on the same machine, not as a portable absolute SLA.

## Recommended One-Cycle Slice

Create a private diagnostics package index inside `src/ai_presenter/runtime/diagnostics.py` and build it once per `_diagnose_material_package(...)` call.

Recommended shape:

- Add a small frozen helper dataclass, for example `_PackageDiagnosticsIndex`.
- Build these shared structures once:
  - aliases grouped by `normalized_alias`;
  - aliases grouped by `language`;
  - Q&A candidates grouped by `normalized_question`;
  - Q&A candidates grouped by `(normalized_question, id(item))`, if that remains useful for exact-overlap logic.
- Change `_diagnose_question_aliases(...)`, `_diagnose_qa_questions(...)`, `_diagnose_qa_alias_overlaps(...)`, and `_diagnose_qa_alias_substring_risks(...)` to consume the shared helper.
- Preserve existing formatter helpers and diagnostic detail wording unless the implementation can prove a wording change is necessary; it should not be necessary.
- Keep the package model, package YAML, CLI command contract, and runtime question matcher unchanged.

The most important micro-optimization is the substring-risk pass. It currently scans all package aliases for each Q&A candidate. The index should let that check scan only aliases with the same language as the Q&A prompt, while preserving exact output ordering and the current INFO detail.

## Target Audience

- Operators who run `ai-presenter doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo` during readiness checks.
- Maintainers reviewing RingCentral Video package localization, aliases, and safety routing.
- Future package authors who will add more aliases and Q&A prompts and need diagnostics to stay responsive.
- CI or agent workflows that repeatedly call diagnostics after small package changes.

## Pain Point

The user-facing pain is not a broken feature; it is response-time drag in a command that is used as a confidence gate. As RingCentral Video package data grows, `doctor` spends avoidable time rebuilding equivalent alias/Q&A maps and doing broad cross-product scans. That makes each safety iteration feel heavier, especially when multiple agents run focused checks repeatedly.

This is a good performance target because the improvement is internal and observable, while the behavior surface is already well tested.

## Acceptance Criteria

A future Cycle 114 implementation satisfies this demand when:

- `diagnose_configuration(...)` builds shared diagnostics lookup data once per package diagnostic pass and reuses it across the alias/Q&A diagnostic checks.
- Existing RingCentral Video doctor output remains unchanged for the current package, including:
  - `[OK] question aliases: 90 package-owned aliases have no cross-entrypoint duplicates`
  - `[OK] qa questions: 73 Q&A question prompts have no cross-item duplicates`
  - `[OK] qa alias overlap: 73 Q&A question prompts have no unsafe package-owned alias overlaps`
  - `[INFO] qa alias substring risk: 11 Q&A question prompts contain package-owned alias substrings outside related entrypoints: ...`
  - `Doctor completed: 11 ok, 1 info, 0 warnings, 0 failed.`
- Existing duplicate-alias, duplicate-Q&A, exact-overlap, substring-risk, related-entrypoint allowance, non-ASCII escaping, and trimmed-question diagnostics tests continue to pass.
- A focused performance/regression test or benchmark-style unit test demonstrates that substring-risk diagnostics does not inspect aliases from unrelated languages for each Q&A prompt. Prefer a deterministic counter/spying test over a brittle wall-clock threshold.
- An optional local timing note shows improvement or no regression on the same in-process loop used during implementation. Do not make wall-clock timing a hard CI gate.
- No changes are made to `packages/ringcentral-video.yaml`, production question routing semantics, package loading behavior, localization report counts, profiles, docs knowledge indexes, coverage files, or git history.

## Non-Goals

- Do not change `answer_question(...)`, `_match_qa(...)`, `_match_entrypoint(...)`, `_can_operate(...)`, `questionPolicy`, or interrupt-step creation.
- Do not add new package YAML aliases, localized questions, localized answers, demo narration, entrypoints, or flows.
- Do not add persistent package-loader caching, filesystem mtime caches, or process-global mutable diagnostics caches in this cycle.
- Do not change CLI output text to make tests easier.
- Do not convert diagnostics into a general lint framework.
- Do not modify localization-report behavior or completeness rules.
- Do not edit production code outside the narrow diagnostics helper/refactor unless a focused test proves it is unavoidable.
- Do not stage `.coverage`; it is already dirty in the worktree.

## Likely Files Involved

Future implementation will likely touch only:

- `src/ai_presenter/runtime/diagnostics.py`
  - Add the shared package diagnostics index helper.
  - Thread the helper through the package diagnostic functions.
  - Preserve existing formatter helpers and output order.
- `tests/unit/test_diagnostics.py`
  - Add or update focused tests around shared-index behavior and language-scoped substring checks.
  - Keep existing behavior assertions intact.
- `tests/unit/test_cli.py`
  - Only if the existing doctor CLI expectation needs a targeted preservation assertion. Prefer avoiding this file if `test_diagnostics.py` already protects the behavior.

Avoid touching these areas for this slice:

- `src/ai_presenter/runtime/questions.py`
- `src/ai_presenter/packages/models.py`
- `src/ai_presenter/packages/loader.py`
- `packages/ringcentral-video.yaml`
- `profiles/*`
- `docs/knowledge/*`
- package YAML, tests unrelated to diagnostics, coverage artifacts, and git history.

## Verification Guidance

Recommended focused verification:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_diagnostics.py
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_cli.py::test_doctor_loads_profile_package_and_flow
.\.venv\Scripts\ai-presenter.exe doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo
git diff --check -- src\ai_presenter\runtime\diagnostics.py tests\unit\test_diagnostics.py tests\unit\test_cli.py
git status --short
```

Optional same-machine timing probe after implementation:

```powershell
@'
from pathlib import Path
from time import perf_counter
from ai_presenter.config.loader import load_profile
from ai_presenter.packages.loader import load_material_package
from ai_presenter.runtime.diagnostics import diagnose_configuration

package = load_material_package(Path("packages/ringcentral-video.yaml"))
profile = load_profile(Path("profiles/ringcentral-video-bind-speaker.yaml"))
start = perf_counter()
for _ in range(200):
    diagnose_configuration(
        profile=profile,
        material_package=package,
        flow_id="meeting-control-map-demo",
    )
print(round((perf_counter() - start) * 1000, 3))
'@ | .\.venv\Scripts\python.exe -
```

Use this timing only as implementation evidence. The deterministic acceptance check should be that the substring-risk diagnostic uses the language-scoped alias index and preserves output.

## Handoff Notes

- This is a performance/response-time cycle, not another language or safety-content cycle.
- The safest implementation is a private refactor inside diagnostics with behavior-preserving tests.
- The likely win grows with RingCentral Video package scale, especially if Spanish or future language wedges add more aliases and Q&A prompts.
- Keep `.coverage` out of staging. It was dirty before this handoff.
