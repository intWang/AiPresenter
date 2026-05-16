# Cycle 114 Risk Scan: Package Matching Performance

Date: 2026-05-16
Scope: documentation-only risk scan. This handoff does not edit production code, package YAML, tests, profiles, coverage, git history, or knowledge indexes.

## Verdict

Conditional go for a low-risk performance/response-time optimization only if the next cycle keeps behavior identical and treats caching/indexing as an internal implementation detail.

No-go for any change that reorders user-visible routing, weakens privacy/safety matching, introduces timing benchmark flakes, claims broad performance wins without measurements, or stages `.coverage`.

The safest shape is:

- Optimize only the already hot matching path around package Q&A, entrypoint lookup, alias matching, and repeated question handling.
- Preserve the current precedence: exact/package Q&A first, safety Q&A before generic matching, entrypoint aliases before token scoring, and `questionPolicy: answerOnly` / risky-word checks before any interrupt can be created.
- Keep cache lifetime tied to an immutable package instance or a clearly versioned package snapshot.
- Use deterministic behavior tests for routing and safety; use coarse timing smoke checks only as diagnostics, not brittle pass/fail gates.
- Document measured scope precisely, including package size, command, machine context if relevant, and whether the data is unit-level or live-app evidence.

## Primary Risks

| Severity | Risk | Failure mode | Impact | Guardrail |
| --- | --- | --- | --- | --- |
| P0 | Stale package state | A cache survives a package reload, running-app scan, language change, or temporary package replacement. | AiPresenter answers from old Q&A/aliases, exposes removed routes, or misses newly scanned controls. | Attach indexes to the `MaterialPackage` instance, rebuild on `load_material_package()` / temporary package creation, and never use a process-global cache keyed only by package id. |
| P0 | Changed route ordering | Refactoring alias or token indexes changes longest-alias precedence, source-order tie breaks, Q&A-before-entrypoint matching, or exact-match behavior. | A safe answer can become an operable route, or a user question can land on a different RingCentral control. | Add routing parity tests for representative English, Chinese, and Japanese questions before optimization, then prove identical `entrypoint_id`, `can_operate`, and answer family after optimization. |
| P0 | Privacy/safety matcher regression | Performance work bypasses `_match_recording_safety_qa()`, `_match_notes_transcript_safety_qa()`, `questionPolicy: answerOnly`, or non-operable risky route checks. | Recording, notes/transcripts, meeting info, invite links, chat, participant names, and post-meeting artifacts may become executable or over-disclosed. | Treat sensitive prompt tests as release gates. Any safety route changed from answer-only/non-operable is a blocker unless explicitly approved by a separate privacy review. |
| P0 | Cache key includes private text | A memoization layer stores raw questions, answers, chat-like text, participant names, meeting IDs, or invite links in logs or long-lived structures. | The optimization creates a privacy retention surface that did not exist before. | If memoization is needed, prefer precomputed package indexes over query-result caches. If a query cache is unavoidable, key by normalized non-sensitive test inputs only in tests; do not log raw questions or answer text. |
| P1 | Timing benchmark flakiness | Unit tests assert strict millisecond thresholds or compare timings on shared/loaded Windows environments. | CI and local runs fail unpredictably; maintainers weaken meaningful tests to make benchmarks pass. | Keep performance tests as optional diagnostics or assert structural behavior such as fewer repeated tokenizations via injected spies. Do not gate on absolute latency except with very loose smoke thresholds. |
| P1 | Over-optimization | A broad indexing abstraction is added before the current package sizes need it, duplicating model internals or making matching harder to reason about. | The code becomes more complex, more fragile, and harder to review than the response-time gain justifies. | Prefer small, local reuse of existing package-private precomputations. Stop if the change needs new schema concepts, cross-package registries, background invalidation, or async machinery. |
| P1 | Locale/token behavior drift | Token precomputation changes casefolding, stopword filtering, CJK handling, or localized question inclusion. | Non-English questions can stop matching, or generic English words can overmatch more often. | Reuse `normalize_question_prompt()`, `match_field_tokens()`, and `match_meaningful_tokens()` instead of duplicating token logic. Add focused localized regression cases. |
| P1 | Temporary package indexes diverge | Running-app scan builds temporary packages that do not receive the same index fields as file-loaded packages. | Controller Q&A may work for YAML packages but fail or slow down for scanned apps. | Build indexes through `MaterialPackage.model_validate()` or one shared constructor path; avoid post-init mutation that temporary packages can skip. |
| P2 | Docs claims overreach | Handoffs or docs say the optimizer makes AiPresenter "fast", "real-time", or "live accepted" based on unit timing or offline matching. | Operators may treat a small internal speedup as live RingCentral reliability evidence. | State exact measurement method and scope. Do not claim live response-time improvement without dated live run evidence. |
| P2 | Coverage artifact churn | Focused tests update `.coverage`, and the artifact is staged with the handoff or later implementation. | The diff violates cycle constraints and hides the real review surface. | Before staging or handoff, run `git status --short` and leave `.coverage` unstaged. |

## Guardrails

Proceed only if all of these remain true:

- Cycle 114 risk scan itself creates only `docs/agent-handoffs/cycle-114-risk-scan.md`.
- Future implementation keeps public package schema, package YAML, profiles, and knowledge indexes unchanged unless a separate cycle explicitly authorizes them.
- The optimized path preserves current answer routing for sensitive prompts, localized Q&A, package-owned aliases, legacy aliases, and no-match fallbacks.
- Any index is derived entirely from package data already accepted by `MaterialPackage` validation.
- Cache invalidation is simple: a new package object means a new index; no cross-run persistence and no hidden dependency on file modification time.
- Logs keep the current privacy discipline: duration, package id, language, tone, entrypoint id, and operability are okay; raw user question and answer text are not.
- Tests focus on deterministic behavior and index construction. Timing checks are optional, coarse, and not the only proof of improvement.
- Performance documentation includes before/after commands and avoids live-readiness or broad UX claims.
- `.coverage` remains unstaged.

## No-Go Triggers

Stop the cycle if any proposed implementation does one of these:

- Changes `entrypoint_id`, `can_operate`, or answer-only behavior for recording, notes/transcripts, meeting info, invite/share/leave, chat privacy, participant names, or post-meeting artifact prompts.
- Moves entrypoint matching ahead of Q&A/safety matching for speed.
- Replaces longest-alias/source-order behavior with an unordered map, set iteration, trie, or scorer without parity tests.
- Adds process-global mutable caches keyed by package id, language, or raw question text.
- Stores raw questions, answer text, meeting IDs, invite links, chat content, participant names, or transcripts in cache keys, logs, test snapshots, or docs.
- Adds strict wall-clock timing assertions to normal unit tests.
- Requires live RingCentral, network access, audio devices, or desktop UI automation to prove the optimization.
- Edits production code, package YAML, tests, profiles, knowledge indexes, coverage, or git history as part of this documentation-only handoff.
- Stages `.coverage`.

## Review Checklist

Use this checklist before approving any later Cycle 114 implementation.

- [ ] Diff scope matches the approved implementation slice; this risk-scan handoff remains the only Cycle 114 file from this advisory step.
- [ ] Package index/cache lifetime is tied to a `MaterialPackage` instance or an explicitly rebuilt immutable snapshot.
- [ ] No raw user questions or generated answers are cached or logged.
- [ ] Existing route precedence is preserved: Q&A and safety checks before generic entrypoint matching, package aliases before legacy aliases, longest package alias before shorter aliases, and source-order tie breaks for equal length aliases.
- [ ] Sensitive prompts remain non-operable where they are non-operable today.
- [ ] Localized English/Chinese/Japanese Q&A and aliases still match expected routes.
- [ ] Temporary packages from running-app scan use the same validated model/index path as YAML-loaded packages.
- [ ] New tests avoid exact long-prose snapshots and strict timing thresholds.
- [ ] Any performance evidence lists the command, data set, and before/after numbers without claiming live acceptance.
- [ ] `git status --short` is reviewed before staging; `.coverage` is not staged.

## Suggested Future Verification

For this advisory handoff, a markdown diff check and git status review are enough.

For a later implementation cycle, recommended focused checks are:

```powershell
.\.venv\Scripts\python.exe -m pytest `
  tests\unit\test_questions.py `
  tests\unit\test_material_packages.py `
  -q -o addopts=""

git diff --check -- src\ai_presenter\runtime\questions.py src\ai_presenter\packages\models.py tests\unit\test_questions.py tests\unit\test_material_packages.py docs\agent-handoffs\cycle-114-risk-scan.md
git status --short
```

If the implementation only changes package-index construction, add the narrowest relevant test file instead of the full suite. If it adds any timing instrumentation, verify that timing logs still omit raw question text and answer text. Do not run live RingCentral acceptance for this performance slice unless a separate acceptance cycle explicitly authorizes it.
