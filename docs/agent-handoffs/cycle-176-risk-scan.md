# Cycle 176 Risk Scan: Presenter Meta Routing Knowledge Update

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`
Role: Cycle176 risk-scan handoff

## Scope And Boundary

This pass reviewed the current RingCentral runtime safety knowledge doc, Cycle174/175 handoffs, and focused Presenter meta routing tests. Per assignment, it writes only this file:

- `docs/agent-handoffs/cycle-176-risk-scan.md`

No source, tests, package YAML, knowledge docs, coverage, staging, or commit changes were made. The workspace already had `.coverage` dirty before this scan and it was not touched.

Reviewed anchors:

- `docs/knowledge/ringcentral-video/runtime-safety-routing.md`
- Cycle174 handoffs for demand, technical scan, risk scan, implementation, experience, initial test review, and follow-up test review
- Cycle175 handoffs for demand, technical scan, risk scan, implementation, experience, and test review
- `src/ai_presenter/runtime/questions.py`
- `src/ai_presenter/runtime/session.py`
- `src/ai_presenter/runtime/voice.py`
- `tests/unit/test_questions.py`
- `tests/unit/test_material_packages.py`

Candidate slice: document Presenter meta routing lessons in `docs/knowledge/ringcentral-video/runtime-safety-routing.md`.

## Current Lessons To Preserve

Cycle174 established the English Presenter meta guard. Cycle175 extended it to high-confidence Chinese phrase-level prompts and added contained localized Q&A protection. The stable shape is:

- Q&A safety routing still runs before Presenter meta matching.
- Pure Presenter expression requests return answer-only guidance with `entrypoint_id=None`, `can_operate=False`, and no question interrupt.
- Mixed prompts can still preserve RingCentralVideo intent through Q&A, package aliases, meeting-info location lookup, or entrypoint titles.
- Presenter meta prompts skip broad entrypoint token fallback.
- The guard lives in runtime question routing, not `packages/ringcentral-video.yaml`.
- The guard answers safely; it does not persistently mutate `PresenterVoiceSettings`, controller state, or session voice state.

## Risks For The Knowledge Update

### 1. Overstating Live RingCentral Evidence

High risk. The Cycle174/175 evidence is local routing tests and manual probes, not a dated live RingCentral acceptance run. The runtime safety doc already says it does not replace dated acceptance evidence and warns not to promote live route evidence without an acceptance record.

Avoid wording like:

- "accepted in RingCentral"
- "validated live"
- "safe for unattended live operation"
- "proves the RingCentral UI route"

Safe framing:

- "repo-local routing tests cover this boundary"
- "this is a runtime routing invariant"
- "live RingCentral acceptance still requires a dated acceptance run"

### 2. Implying Persistent Voice State

High risk. The current Presenter meta answer says AiPresenter can adjust language, tone, pacing, and guidance depth through voice settings, but the meta guard itself returns an answer; it does not change persistent controller/session voice state.

Avoid wording like:

- "Switches the Presenter to Chinese"
- "updates the current tone"
- "remembers the user's requested guidance depth"
- "sets voice state from natural-language prompts"

Safe framing:

- "Pure Presenter meta prompts are answered as expression requests and do not operate RingCentral Video."
- "This guard does not persist language, tone, pacing, or guidance-depth state unless a separate controller/session state slice implements and tests that behavior."

### 3. Contradicting Package/YAML Ownership

High risk. Presenter meta prompts are AiPresenter expression requests, not RingCentralVideo product facts, aliases, Q&A, or localized titles. Adding them to YAML would change package counts and diagnostics for a runtime guard.

Avoid wording that suggests:

- Presenter meta prompts belong in `packages/ringcentral-video.yaml`.
- Package aliases should include language, tone, pacing, or beginner guidance.
- Runtime-only documentation should update operation entrypoint, Q&A, alias, demo-flow, or localization counts.

Safe framing:

- "The package owns RingCentralVideo surfaces and product Q&A; the runtime guard owns Presenter expression requests."
- "Package count drift is a review trigger unless a separate package slice explicitly changes YAML."

### 4. Duplicating Stale Details

Medium risk. The knowledge doc should capture the durable routing pattern, not paste the whole fragment list, all test matrices, or handoff-only implementation snapshots. Fragment lists and test prompts can drift quickly.

Avoid:

- full copies of `_PRESENTER_META_REQUEST_FRAGMENTS`
- long Cycle174/175 prompt matrices
- unverified commit hashes for recent-cycle anchors
- line numbers from the current working tree
- restating current package counts unless YAML changed

Safe framing:

- summarize phrase-level English and Chinese coverage
- reference the invariant, not every fragment
- add Recent Cycle Anchors rows only after final commits exist and hashes are verified
- keep package count text unchanged for a docs-only runtime lesson

### 5. Insufficient Tests For A Durable Doc Claim

Medium risk. A docs-only update can still regress knowledge boundaries if no test asserts the new wording. Existing routing tests cover runtime behavior, but they do not yet require the knowledge doc to mention Presenter meta routing without overclaiming acceptance or persistence.

Recommended test additions for an implementation cycle:

- Add a docs assertion near `tests/unit/test_material_packages.py::test_ringcentral_knowledge_docs_preserve_evidence_boundaries` that `runtime-safety-routing.md` contains the Presenter meta ownership and no-persistence boundary.
- Keep focused routing sentinels in `tests/unit/test_questions.py` green for English pure meta, Chinese pure meta, mixed RingCentral intents, bare Chinese safety words, and mojibake rejection.
- If the knowledge doc adds a "Recent Cycle Anchors" row, assert only committed cycle anchors are listed with real commit hashes.

## Must-Have Doc Wording

Recommended placement: add a short section in `docs/knowledge/ringcentral-video/runtime-safety-routing.md` after "Tone Is Style-Only" or near the current runtime anchors.

Suggested wording:

```markdown
## Presenter Meta Requests Are Runtime Answer-Only

Presenter meta requests ask AiPresenter to change how it answers, such as language, tone, pacing, guidance depth, or user familiarity. They are not RingCentral Video control requests.

The runtime handles high-confidence Presenter meta phrases in `src/ai_presenter/runtime/questions.py`. Q&A safety matching still runs first. Pure meta prompts return an answer-only `QuestionResponse` with no `entrypoint_id`, `can_operate=False`, and no `create_question_interrupt_step(...)`. Mixed prompts can still preserve explicit RingCentralVideo intent through Q&A, package aliases, meeting-info location lookup, or entrypoint titles; broad token fallback is skipped while meta matching is active.

This guard does not persist language, tone, pacing, or guidance-depth state. Do not describe it as changing controller/session voice state unless a separate state-mutation slice implements and tests that behavior.

Do not add Presenter meta phrases to `packages/ringcentral-video.yaml` as aliases, Q&A, localized titles, or package facts. The package owns app surfaces and product knowledge; the runtime guard owns Presenter expression requests. YAML, localization, and package-count drift are regressions unless a separate package slice explicitly owns them.

Contained localized Q&A matching preserves authored safety answers when a style prefix is added to a sensitive RingCentral prompt. Keep fragments phrase-level and reject bare safety/status words or mojibake text as supported meta prompts.

Repo tests prove only local routing boundaries. They are not live RingCentral acceptance evidence.
```

Optional small addition to the maintenance checklist:

```markdown
- Before documenting Presenter meta routing, verify the wording says answer-only/no-interrupt, does not claim persistent voice-state mutation, keeps package YAML ownership separate, and does not promote repo tests to live RingCentral evidence.
```

## Test Recommendations

For a docs-only knowledge update:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -B -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_knowledge_docs_preserve_evidence_boundaries
git diff --check
```

For a broader confidence pass after editing the knowledge doc:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -B -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests\unit\test_questions.py::test_presenter_meta_requests_do_not_route_to_ringcentral_controls tests\unit\test_questions.py::test_chinese_presenter_meta_requests_do_not_route_to_ringcentral_controls tests\unit\test_questions.py::test_presenter_meta_modifiers_do_not_steal_ringcentral_intents tests\unit\test_questions.py::test_chinese_presenter_meta_modifiers_do_not_steal_ringcentral_intents tests\unit\test_questions.py::test_chinese_bare_safety_words_do_not_match_presenter_meta_or_security tests\unit\test_questions.py::test_chinese_presenter_meta_mojibake_does_not_match
```

If future work changes wording around package ownership or counts, add package diagnostics/localization checks before merging:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -B -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests\unit\test_material_packages.py tests\unit\test_cli.py::test_doctor_loads_profile_package_and_flow tests\unit\test_cli.py::test_localization_report_outputs_ringcentral_chinese_coverage
```

## No-Go Conditions

Do not accept the Cycle176 knowledge update if it:

- Claims live RingCentral acceptance or accepted route confidence from local tests.
- Says natural-language Presenter meta prompts persistently change language, tone, pacing, or guidance depth.
- Tells future agents to add Presenter meta prompts to package YAML aliases or Q&A.
- Changes package count claims without a package/YAML diff.
- Duplicates the full fragment list in the knowledge doc.
- Omits the Q&A-first and mixed-intent routing boundary.
- Omits tests or at least a focused docs assertion plan.

## Recommendation

Proceed with a small knowledge-doc update only. Add a durable Presenter meta routing section to `runtime-safety-routing.md`, keep it invariant-focused, and avoid turning Cycle174/175 handoff details into stale package facts. Pair the update with a docs boundary assertion in `test_material_packages.py` if source/test edits are allowed in the implementation cycle; otherwise run the existing docs and routing sentinels before handoff.

## Status

Status: risk scan complete; source, tests, package YAML, knowledge docs, `.coverage`, staging, and commits were not modified by this pass.

Changed file path:

- `docs/agent-handoffs/cycle-176-risk-scan.md`
