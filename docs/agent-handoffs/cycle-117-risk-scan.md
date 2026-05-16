# Cycle 117 Risk Scan: Spanish Report-Only Q&A Completion

Date: 2026-05-16
Scope: documentation-only risk scan for completing Spanish report-only RingCentral Video Q&A coverage. This handoff creates only `docs/agent-handoffs/cycle-117-risk-scan.md`.

## Verdict

Conditional go for a narrow package-localization implementation that adds Spanish `localizedQuestions.es` and `localizedAnswers.es` for the existing RingCentral Video Q&A set while keeping Spanish runtime support disabled.

No-go for any change that enables `PresenterVoiceSettings(language="es")`, adds Spanish to public runtime language choices, translates demo narration, changes `questionPolicy`, changes `openSteps`, changes route authorization, makes live RingCentral acceptance claims, edits profiles, or stages `.coverage`.

Current read-only baseline from this scan:

- Spanish localization report: `0/51` demo steps, `1/12` Q&A questions, `1/12` Q&A answers, and `questionAliases.es` on `1/27` entrypoints with `3` aliases.
- Spanish `--require-complete` exits `1` with `Localization coverage incomplete for es.`
- Chinese and Japanese `--require-complete` reports still pass with `51/51` demo steps and `12/12` Q&A question/answer coverage.
- `voices` lists English, Chinese, and Japanese only.
- `doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo` completes with `11 ok`, `1 info`, `0 warnings`, and `0 failed`.
- Current doctor package signals are `90` package-owned aliases and `73` Q&A question prompts.
- `.coverage` is already modified in the worktree and is out of scope.

## Go Guidance

Proceed only if the future implementation stays package/report-only:

- Add Spanish question and answer localization for the 11 currently missing Q&A items in `packages/ringcentral-video.yaml`.
- Preserve the existing Spanish background/privacy seed.
- Keep RingCentral UI labels such as `Chat`, `Participants`, `Share`, `Notes`, `Settings`, `Background`, `Recording`, and `Network quality` in English when they refer to visible UI labels.
- Prefer full, specific Spanish Q&A prompts over broad Spanish aliases.
- Keep Spanish demo narration at `0/51` unless a separate runtime-language or narration-localization cycle is approved.
- Keep Spanish runtime unsupported and prove that with tests or CLI checks.

## No-Go Triggers

Stop the implementation if any proposed change:

- Adds `es` to runtime language literals, CLI/controller language choices, voice labels, provider compatibility, or voice asset checks.
- Makes `localization-report --package ringcentral-video --language es --require-complete` pass while Spanish demo narration remains missing.
- Calls Spanish "supported", "accepted", "live verified", or "demo-ready" based only on package YAML, localization report output, unit tests, or doctor output.
- Adds broad `questionAliases.es` for private content or state-changing actions such as reading chat, reading names, copying links, starting notes, starting captions, translating, recording, sending reactions, raising hand, sharing, inviting, muting others, locking, leaving, or ending.
- Changes `questionPolicy`, `openSteps`, locator metadata, route authorization, `can_operate`, Q&A-first matching, or question interrupt creation.
- Converts report-only Spanish Q&A coverage into runtime Spanish voice behavior.
- Stages, resets, deletes, or normalizes `.coverage`.

## Primary Risks

| Severity | Risk | Failure mode | Guardrail |
| --- | --- | --- | --- |
| P0 | Privacy phrasing drift | Spanish answers use wording that sounds like AiPresenter will read meeting links, meeting IDs, chat, participant names, roles, notes, transcripts, captions, shared-screen content, recordings, summaries, or insights by default. | Use explicit boundary language: explain where a surface is, do not read or summarize private content unless the user explicitly asks and visible context is verified. |
| P0 | Answer-only behavior regression | A localized safety prompt points at an operable entrypoint or encourages an action, causing a future Spanish prompt to queue a question interrupt or imply permission. | Keep sensitive Q&A as explanatory. Do not edit `questionPolicy` or `openSteps`. Verify sensitive prompts remain `can_operate=False` where route tests cover them. |
| P0 | Matching overreach | New Spanish prompts are too short, alias-like, or action-oriented, so `qa_question_candidates` shadow safe entrypoint lookup or collide with existing aliases. | Add complete question forms, not fragments. Avoid new Spanish aliases unless a focused test proves one is needed. Run doctor duplicate, overlap, and substring diagnostics. |
| P1 | Localization completeness semantics | Q&A reaches `12/12`, and docs or tests treat Spanish as complete even though demo narration is still `0/51`. | Use "Spanish Q&A complete" or "report-only Q&A coverage", never "Spanish localization complete". `--require-complete` must continue to fail. |
| P1 | Diagnostics count drift | Adding Spanish localized questions increases Q&A prompt counts and may change the INFO-level alias-substring summary. | Update focused diagnostics expectations deliberately and document the count movement. Current baseline is `90` aliases and `73` Q&A prompts. |
| P1 | Runtime Spanish leakage | Tests or implementation add `es` to runtime voice settings to exercise localized Q&A. | Keep runtime voice checks rejecting `es`; test report-only coverage through package/localization APIs and CLI reports, not by enabling runtime Spanish. |
| P2 | Mixed evidence labels | Handoffs or README imply live RingCentral acceptance, provider compatibility, or current-build UI verification from offline package checks. | Name evidence exactly: package report, unit test, doctor, or live/manual acceptance. Do not make live acceptance claims in this slice. |
| P2 | Coverage artifact staging | Focused pytest runs modify `.coverage`, then the artifact is staged with the package/test changes. | Run `git status --short` and `git diff --cached --name-status`; leave `.coverage` unstaged. |

## Privacy Phrasing Checklist

Spanish answers should preserve these meanings:

- Shared screen: do not infer, read, or describe private shared content by default.
- Invite and meeting info: do not read links, IDs, dial-in details, names, emails, or suggestions aloud by default.
- Chat and participants: do not read chat messages, participant names, roles, or private tabs by default.
- Host controls: do not mute, remove, lock, change security, or manage participants without explicit confirmation and verified context.
- Reactions and raise hand: visible meeting signals should not be sent or left active unless explicitly requested.
- Audio/video readiness: do not toggle real meeting media unless the user intends to change state.
- Network quality: avoid guessing exact causes without observed diagnostic values.
- Notes, transcript, captions, translation: explain discovery surfaces, but do not start, read, translate, or summarize content by default.
- Post-meeting artifacts: do not promise that recordings, transcripts, summaries, or insights exist.
- Recording: keep explain-only until user confirmation, allowed role, and participant consent are clear.

## Verification Checklist

For this documentation-only scan:

- [ ] Diff contains only `docs/agent-handoffs/cycle-117-risk-scan.md`.
- [ ] `git diff --check -- docs\agent-handoffs\cycle-117-risk-scan.md` passes.
- [ ] `git status --short --untracked-files=all` is reviewed; `.coverage` remains unstaged.

For the future Spanish Q&A implementation:

- [ ] `localization-report --package ringcentral-video --language es` reports `0/51` demo steps, `12/12` Q&A questions, and `12/12` Q&A answers.
- [ ] `localization-report --package ringcentral-video --language es --require-complete` still exits nonzero because demo narration remains incomplete.
- [ ] `localization-report --package ringcentral-video --language zh --require-complete` and `--language ja --require-complete` still pass.
- [ ] `voices` still lists English, Chinese, and Japanese only.
- [ ] `demo --profile ringcentral-video --package ringcentral-video --flow meeting-control-map-demo --language es --dry-run` still rejects Spanish with `Unsupported presenter language: es`.
- [ ] Sensitive Spanish Q&A prompts are tested or otherwise reviewed for answer-only, non-operable behavior where runtime routing is intentionally exercised.
- [ ] Safe location-style prompts remain helpful and do not become destructive, content-reading, or state-changing actions.
- [ ] Doctor diagnostics complete with no warnings or failures; any intentional Q&A prompt-count or substring-info change is documented.
- [ ] No README, handoff, test name, or assertion claims live RingCentral acceptance or Spanish runtime support.
- [ ] `git diff --check` passes.
- [ ] `git status --short` confirms `.coverage` is not staged.

Suggested focused commands for the implementation cycle:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py tests\unit\test_cli.py tests\unit\test_questions.py tests\unit\test_diagnostics.py
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language es
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language es --require-complete
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language zh --require-complete
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ja --require-complete
.\.venv\Scripts\ai-presenter.exe voices
.\.venv\Scripts\ai-presenter.exe demo --profile ringcentral-video --package ringcentral-video --flow meeting-control-map-demo --language es --dry-run
.\.venv\Scripts\ai-presenter.exe doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo
git diff --check
git diff --cached --name-status
git status --short --untracked-files=all
```

The expected Spanish `--require-complete` and Spanish `demo --language es` commands should fail until a separate Spanish runtime and demo-narration slice is explicitly approved.

## Coverage Staging Warning

`.coverage` was already modified before this scan. Do not stage, delete, reset, or regenerate it from this subagent. If future focused tests update it again, leave it unstaged unless the user explicitly assigns coverage artifact maintenance.
