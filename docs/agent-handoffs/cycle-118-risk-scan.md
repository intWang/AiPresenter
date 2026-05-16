# Cycle 118 Risk Scan: Spanish Next-Slice Boundaries

Date: 2026-05-16
Scope: documentation-only risk scan for candidate Cycle 118 slices after Spanish report-only Q&A coverage. This handoff creates only `docs/agent-handoffs/cycle-118-risk-scan.md`.

## Findings

Cycle 117 completed Spanish report-only RingCentral Video Q&A coverage, but Spanish remains intentionally incomplete and unsupported at runtime:

- Spanish demo narration is still `0/51`.
- Spanish Q&A report coverage is now `12/12` questions and `12/12` answers.
- Spanish runtime presenter language remains unsupported and must continue to be rejected.
- `voices` must continue to list only English, Chinese, and Japanese unless a separate runtime support slice explicitly changes the compatibility matrix.
- Current RingCentral diagnostic prompt-count expectations should reflect the Cycle 117 movement from `73` to `84` Q&A prompts.
- `.coverage` is already modified in the worktree and remains out of scope.

Privacy and safety risk is highest if a Spanish narration or alias slice implies AiPresenter can read or act on private meeting content. Localization risk is highest if visible RingCentral UI labels are translated in package text even though the app surface remains English. Runtime risk is highest if report-only Spanish assets get mistaken for Spanish voice support.

## Recommendation

Go for exactly one narrow Cycle 118 implementation slice:

- Preferred: add Spanish demo narration coverage while keeping Spanish runtime unsupported.
- Acceptable: add a focused diagnostics prompt-count drift guard without package text changes.
- Planning-only: document Spanish runtime promotion requirements without enabling runtime Spanish.

No-go for combining Spanish demo narration, diagnostics behavior changes, and runtime promotion in one cycle. No-go for enabling Spanish runtime until demo narration, provider support, user-facing language catalogs, fallback text, CLI/controller validation, and voice asset diagnostics are designed and tested together.

## Go Boundaries

A single-cycle implementation may proceed only if it stays inside one of these envelopes:

- Spanish demo narration coverage: add `localizedText.es` for the existing `51` RingCentral demo steps, preserve English UI labels, keep `--language es` runtime rejection, and make `localization-report --language es --require-complete` pass only if Q&A remains complete and all required demo narration is present.
- Diagnostics drift guard: add or tighten tests that fail on unintended RingCentral diagnostic prompt-count movement, with documented expected counts and no package/runtime behavior change.
- Runtime promotion planning: write docs/tests-as-plan only; do not add `es` to runtime language literals, voice provider routing, controller choices, or `voices` output.

## No-Go Triggers

Stop the cycle if any implementation:

- Enables `PresenterVoiceSettings(language="es")`, CLI `--language es`, controller Spanish choices, provider selection, or voice labels as a side effect of report coverage.
- Translates visible RingCentral UI labels such as `Chat`, `Participants`, `Share`, `Invite`, `Notes`, `Settings`, `Background`, `Recording`, `Network quality`, `Blur`, `Mute`, `Start video`, `Stop video`, `React`, `Raise hand`, `More`, or `Leave`.
- Adds hidden live acceptance claims, including "accepted", "live verified", "demo-ready", "supported", or "RingCentral validated" based only on package YAML, unit tests, diagnostics, or localization reports.
- Adds broad Spanish aliases for private content or state-changing actions.
- Changes `questionPolicy`, `openSteps`, route authorization, `can_operate`, Q&A-first matching, interrupt creation, or locator behavior.
- Lets diagnostics count drift without a deliberate expected-count update and handoff note.
- Stages, deletes, resets, or normalizes `.coverage`.

## Failure Modes To Test

| Risk | Failure mode | Required test or check |
| --- | --- | --- |
| Accidental runtime Spanish enablement | Spanish package coverage causes `demo --language es --dry-run`, runtime voice validation, or `voices` to accept Spanish. | Assert Spanish runtime remains rejected unless this is an explicit runtime-promotion cycle. |
| Translated RingCentral UI labels | Spanish narration says localized labels where the product UI still shows English labels, causing users to search for controls that do not exist. | Review package text and add assertions for key English UI labels in localized narration where practical. |
| Hidden live acceptance claims | Docs, test names, or output imply live RingCentral validation from offline evidence. | Grep touched docs/tests for acceptance wording and require dated live/manual evidence for any live claim. |
| Broad Spanish aliases | Short Spanish aliases overmatch sensitive prompts for chat, participants, recording, notes, links, share, invite, mute, leave, or end. | Prefer full localized Q&A questions; if aliases are added, add negative routing tests for private and destructive actions. |
| Diagnostic count drift | New localized prompts change Q&A counts or substring summaries while tests still bless stale expectations. | Run doctor/diagnostic tests and update expected counts only with an explicit explanation. |
| `.coverage` staging | Focused pytest updates `.coverage`, and it is staged with source changes. | Run `git status --short` and `git diff --cached --name-status`; leave `.coverage` unstaged. |

## Acceptance Criteria

For a Spanish demo narration slice:

- `localizedText.es` exists for all required RingCentral demo steps and preserves privacy boundaries.
- English RingCentral UI labels remain English inside Spanish narration where they name visible controls.
- Spanish Q&A remains `12/12` questions and `12/12` answers.
- Spanish runtime remains unsupported in `voices` and `demo --language es --dry-run`, unless the cycle was explicitly re-scoped to runtime promotion.
- No broad Spanish aliases are added.
- No live RingCentral acceptance or runtime support claims are added.
- Diagnostic prompt-count expectations are intentionally updated if counts move.
- `.coverage` is not staged.

For a diagnostics-only slice:

- No package YAML, runtime language, provider, route, or controller behavior changes.
- Tests fail on unintended RingCentral Q&A prompt-count drift.
- Expected counts are documented with the current baseline.
- `.coverage` is not staged.

For a runtime-promotion planning slice:

- Output is planning or test-design documentation only.
- Runtime Spanish remains disabled.
- The plan names required provider, fallback, CLI, controller, localization completeness, privacy, and acceptance evidence gates.

## Verification Checklist

For this documentation-only scan:

- [ ] Diff contains only `docs/agent-handoffs/cycle-118-risk-scan.md`.
- [ ] `git diff --check -- docs\agent-handoffs\cycle-118-risk-scan.md` passes.
- [ ] `git status --short --untracked-files=all` is reviewed; `.coverage` remains unstaged.

For the selected Cycle 118 implementation:

- [ ] `localization-report --package ringcentral-video --language es` reports the intended Spanish demo/Q&A counts for the chosen slice.
- [ ] `localization-report --package ringcentral-video --language zh --require-complete` and `--language ja --require-complete` still pass.
- [ ] `voices` still excludes Spanish unless runtime promotion is explicitly approved.
- [ ] `demo --profile ringcentral-video --package ringcentral-video --flow meeting-control-map-demo --language es --dry-run` still rejects Spanish unless runtime promotion is explicitly approved.
- [ ] Touched Spanish narration preserves English RingCentral UI labels and avoids private-content reading claims.
- [ ] No touched docs/tests claim live RingCentral acceptance without dated live/manual evidence.
- [ ] No broad Spanish aliases are introduced; any alias addition has negative routing coverage.
- [ ] Doctor/diagnostics prompt counts are checked and deliberately updated if changed.
- [ ] `git diff --check` passes.
- [ ] `git diff --cached --name-status` and `git status --short --untracked-files=all` confirm `.coverage` is not staged.

Suggested focused commands for a future implementation cycle:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py tests\unit\test_cli.py tests\unit\test_questions.py tests\unit\test_diagnostics.py
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language es
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language zh --require-complete
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ja --require-complete
.\.venv\Scripts\ai-presenter.exe voices
.\.venv\Scripts\ai-presenter.exe demo --profile ringcentral-video --package ringcentral-video --flow meeting-control-map-demo --language es --dry-run
.\.venv\Scripts\ai-presenter.exe doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo
git diff --check
git diff --cached --name-status
git status --short --untracked-files=all
```

If Spanish runtime remains out of scope, the Spanish demo command should continue to fail with an unsupported-language error even after report coverage improves.
