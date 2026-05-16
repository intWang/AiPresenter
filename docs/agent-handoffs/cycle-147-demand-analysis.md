# Cycle 147 Demand Analysis: acceptance-draft Draft-Only Boundary

Date: 2026-05-17
Cycle: 147
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`

## User Value

The user value is preventing a generated RingCentral Video acceptance draft
from being mistaken for acceptance evidence.

`acceptance-draft` is useful because it pre-fills package, flow, entrypoint,
checklist, intended steps, privacy, and required manual acceptance fields before
a human runs the live RingCentral workflow. That convenience is also the risk:
the more complete the draft looks, the easier it is for a future operator or
agent to treat it as proof.

The boundary must stay explicit in every successful draft surface:

- `Draft only`
- `not acceptance evidence`
- `No live RingCentral action has been performed by this helper.`

Those phrases should remain visible in stdout and in any written draft file.
Only a completed, dated manual record appended after a real run belongs in
`docs/knowledge/ringcentral-video/acceptance-runs.md`. The helper does not run
RingCentral, click controls, observe results, collect evidence files, or make a
pass/fail claim.

## Recommended Minimum Scope

Keep this as a narrow output-contract guard around the existing
`acceptance-draft` implementation.

Recommended implementation:

- In `tests/unit/test_acceptance_manual_record.py`, keep or strengthen the
  existing successful draft coverage so the rendered draft must include all
  three boundary phrases:
  - `Draft only`
  - `not acceptance evidence`
  - `No live RingCentral action has been performed by this helper.`
- In `tests/unit/test_cli.py`, strengthen
  `test_acceptance_draft_outputs_entrypoint_template` so CLI stdout for a
  successful entrypoint draft also asserts the three boundary phrases.
- In `tests/unit/test_cli.py`, strengthen
  `test_acceptance_draft_outputs_flow_template` so CLI stdout for a successful
  flow draft also asserts the same draft-only boundary.
- In `tests/unit/test_cli.py`, strengthen
  `test_acceptance_draft_can_write_to_output_file` so the written file asserts
  the same three phrases, not just `Draft only`.
- Preserve the existing refusal guard that rejects an output path named
  `acceptance-runs.md`.
- Prefer test-only changes unless a focused test proves one of the boundary
  phrases is genuinely missing from a required output path.

The minimum useful behavior is: a future change cannot remove the draft-only
language from stdout or file output without breaking a focused unit test.

## Out Of Scope

Do not broaden this cycle into live acceptance, package behavior, or runtime
work.

Do not touch:

- `docs/knowledge/ringcentral-video/acceptance-runs.md`
- package YAML or package metadata
- profiles
- runtime, controller, provider, route, question matching, localization, voice,
  UIA, or RingCentral app interaction behavior
- dependency files, lockfiles, or project packaging
- `.coverage`

Do not add or imply:

- a new live RingCentral acceptance claim
- a new dated acceptance run
- a pass/fail result
- that a generated draft is acceptance evidence
- that CLI generation performed a live RingCentral action
- promotion from `Repo-tested` or `Observed` to `Accepted`
- broad refactors outside the draft rendering/output contract

If implementation appears to require changing live acceptance docs, package
definitions, profiles, runtime behavior, or dependency metadata, pause and
rescope. This demand is about preserving visible draft-only language, not about
executing or recording acceptance.

## Acceptance Criteria

Implementation should be accepted when:

- Successful `acceptance-draft` stdout for an entrypoint includes `Draft only`,
  `not acceptance evidence`, and
  `No live RingCentral action has been performed by this helper.`
- Successful `acceptance-draft` stdout for a flow includes the same three
  boundary phrases.
- A draft written with `--output` includes the same three boundary phrases in
  the file contents.
- The manual renderer test still directly guards the draft-only boundary.
- Existing required manual acceptance fields, package/flow/entrypoint context,
  privacy reminder, and intended-step prefill behavior remain intact.
- Output to a path named `acceptance-runs.md` is still refused.
- No live acceptance run is added or modified.
- No package YAML, profile, runtime, dependency metadata, or `.coverage` change
  is included.
- Focused tests pass for the touched acceptance-draft checks.
- Whitespace verification passes for touched files.

Suggested focused verification for the implementation subtask:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_acceptance_manual_record.py::test_manual_acceptance_draft_prefills_entrypoint_context_without_claiming_acceptance tests\unit\test_cli.py::test_acceptance_draft_outputs_entrypoint_template tests\unit\test_cli.py::test_acceptance_draft_outputs_flow_template tests\unit\test_cli.py::test_acceptance_draft_can_write_to_output_file tests\unit\test_cli.py::test_acceptance_draft_rejects_acceptance_runs_output_file
git diff --check -- tests\unit\test_acceptance_manual_record.py tests\unit\test_cli.py
git status --short
```

Manual smoke is optional for a test-only change, but the expected visible
boundary shape is:

```text
> Draft only: this is not acceptance evidence until filled after the manual run and appended to `acceptance-runs.md`.
> No live RingCentral action has been performed by this helper.
```

## Handoff Prompt For Implementation Subtask

Cycle147 implementation subtask. You are not the only agent in this repo. Keep
the change narrow, do not revert other work, and do not stage or revert
`.coverage`.

Repository:
`C:\Users\rcadmin\Documents\Repos\AiPresenter`

Goal:
Guard the `acceptance-draft` draft-only boundary so successful stdout and file
output continue to say the generated text is only a draft, is not acceptance
evidence, and did not perform any live RingCentral action.

Read first:

- `docs/agent-handoffs/cycle-147-demand-analysis.md`
- `docs/agent-handoffs/cycle-146-experience.md`
- `tests/unit/test_acceptance_manual_record.py`
- `tests/unit/test_cli.py` around `acceptance-draft`
- `src/ai_presenter/acceptance/manual_record.py`
- `docs/knowledge/ringcentral-video/acceptance-runs.md`

Recommended implementation:

- Strengthen `test_acceptance_draft_outputs_entrypoint_template` so stdout
  includes:
  - `Draft only`
  - `not acceptance evidence`
  - `No live RingCentral action has been performed by this helper.`
- Strengthen `test_acceptance_draft_outputs_flow_template` with the same three
  stdout assertions.
- Strengthen `test_acceptance_draft_can_write_to_output_file` so the written
  file includes the same three phrases.
- Keep the existing renderer test guarding the same boundary in
  `test_manual_acceptance_draft_prefills_entrypoint_context_without_claiming_acceptance`;
  only edit it if the focused guard needs clearer wording.
- Preserve the refusal test for writing directly to `acceptance-runs.md`.
- Do not change source unless a focused failing test proves a required output
  path is genuinely missing the boundary phrase.
- Do not create or update acceptance runs.
- Do not add live acceptance wording.
- Do not touch package YAML, profiles, runtime/provider behavior, dependency
  metadata, or `.coverage`.

Verification:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_acceptance_manual_record.py::test_manual_acceptance_draft_prefills_entrypoint_context_without_claiming_acceptance tests\unit\test_cli.py::test_acceptance_draft_outputs_entrypoint_template tests\unit\test_cli.py::test_acceptance_draft_outputs_flow_template tests\unit\test_cli.py::test_acceptance_draft_can_write_to_output_file tests\unit\test_cli.py::test_acceptance_draft_rejects_acceptance_runs_output_file
git diff --check -- tests\unit\test_acceptance_manual_record.py tests\unit\test_cli.py
git status --short
```

Success means `acceptance-draft` remains useful as a manual-record starter
while stdout and file output cannot be mistaken for a completed RingCentral
acceptance run.
