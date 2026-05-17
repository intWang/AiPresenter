# Cycle 159 Risk Scan: RingCentral Video Screen Sharing Exact Prompts

Date: 2026-05-17
Cycle: 159
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`
Latest related commit inspected: `0307173`

## Scope

Documentation-only risk scan for RingCentral Video screen share and
shared-content question behavior around these exact English prompts:

- `Share my screen`
- `Start sharing`
- `Stop sharing`
- `Read the shared screen`
- `Can you describe what's on screen?`
- `Show my screen`

Only this handoff file was authored for the cycle. Do not treat this scan as a
source, package, runtime, test, profile, coverage, or live RingCentral
acceptance change.

The working tree already contained non-doc changes before this scan:

- `.coverage` is dirty.
- `packages/ringcentral-video.yaml` is dirty and already contains the
  screen-sharing safety Q&A item and English localized Q&A prompts for the six
  strings above.
- `tests/unit/test_questions.py` is dirty and already contains a focused
  screen-sharing safety test for the six prompts above.
- `tests/unit/test_cli.py`, `tests/unit/test_diagnostics.py`, and
  `tests/unit/test_material_packages.py` are dirty.
- `docs/agent-handoffs/cycle-159-demand-analysis.md` and
  `docs/agent-handoffs/cycle-159-technical-scan.md` are untracked.

Those files were inspected but not edited by this risk-scan pass.

## Current Runtime Baseline

Read-only probes against the current working tree show the six exact prompts
route to the authored screen-sharing safety Q&A answer:

| Prompt | Current route | `can_operate` | Interrupt step | Current answer shape |
| --- | --- | --- | --- | --- |
| `Share my screen` | `ringcentral.video.toolbar.share` | `False` | none | screen-sharing safety Q&A |
| `Start sharing` | `ringcentral.video.toolbar.share` | `False` | none | screen-sharing safety Q&A |
| `Stop sharing` | `ringcentral.video.toolbar.share` | `False` | none | screen-sharing safety Q&A |
| `Read the shared screen` | `ringcentral.video.toolbar.share` | `False` | none | screen-sharing safety Q&A |
| `Can you describe what's on screen?` | `ringcentral.video.toolbar.share` | `False` | none | screen-sharing safety Q&A |
| `Show my screen` | `ringcentral.video.toolbar.share` | `False` | none | screen-sharing safety Q&A |

The safety answer begins with:

`Screen sharing can expose private content and changes what other people see.`

Location-style prompts still route to the Share entrypoint and return thin
location/control text while staying non-operable:

| Prompt | Current route | `can_operate` | Interrupt step | Current answer shape |
| --- | --- | --- | --- | --- |
| `Where is Share?` | `ringcentral.video.toolbar.share` | `False` | none | `Screen sharing: Start sharing...` |
| `Where is screen sharing?` | `ringcentral.video.toolbar.share` | `False` | none | `Screen sharing: Start sharing...` |

This split is acceptable: command-shaped or private-content prompts get the
safety answer, while location-shaped prompts can explain where the Share control
lives without queuing a live UI action.

## Safety Boundary

The current structural safety boundary is strong:

- Q&A matching runs before entrypoint matching in
  `src/ai_presenter/runtime/questions.py`.
- The six exact prompts are authored under Q&A, not under
  `operationEntrypoints[*].questionAliases`.
- `create_question_interrupt_step(...)` returns `None` whenever
  `can_operate=False`.
- `ringcentral.video.toolbar.share` is rejected by `_can_operate(...)` because
  its id/title/purpose include risky words such as `share` and `start`.
- The Share entrypoint open step uses `cleanup: escape`, so exploratory control
  tours should close the picker and never click the final Share button.
- The package notes say narration must not infer shared-screen content unless
  verified by an allowed source.
- The share explainer says the presenter does not press the final Share button
  unless the user confirms.

Recommended risk level: high. Screen sharing can expose the user's desktop,
application windows, documents, private notifications, customer data, or other
meeting-sensitive content. A false positive can also start or stop content
presentation for everyone in the meeting.

## Risk Summary

No current blocker was found in the settled inspected behavior. The exact
prompts are answer-only in practice, non-operable, and create no interrupt step.

The main risks are future drift:

- moving these exact prompts from Q&A to package-owned entrypoint aliases
- weakening `_RISKY_ENTRYPOINT_WORDS` so Share becomes operable from question
  handling
- treating `Start sharing`, `Stop sharing`, or `Show my screen` as executable
  confirmation instead of safety guidance
- treating `Read the shared screen` or `Can you describe what's on screen?` as
  permission to read private content without an approved observation source
- adding screenshot or OCR behavior that bypasses the verified-source and user
  permission boundary
- letting a running demo interrupt queue `Share` from one of these prompts
- translating action-shaped localized prompts as entrypoint aliases instead of
  Q&A safety prompts
- changing diagnostics counts mechanically without reviewing real alias and Q&A
  inventory changes

## No-Accidental-Share Boundary

Safe behavior:

- Answer all six exact prompts with screen-sharing safety guidance.
- Keep `entrypoint_id == "ringcentral.video.toolbar.share"` for the Q&A item.
- Keep `can_operate=False`.
- Keep `create_question_interrupt_step(...) is None`.
- State that screen sharing can expose private content and changes what others
  see.
- Require explicit confirmation of what should be shared or stopped before any
  future executable workflow.
- Only describe visible shared content after an approved observation source has
  captured it and the user allows it.

No-go behavior:

- Do not click `Share`, the final share-confirmation button, a window tile, a
  desktop tile, system-audio sharing, or any picker item from these question
  prompts.
- Do not stop an active share from these question prompts without a separate
  confirmed-action workflow and verified current sharing state.
- Do not claim sharing started, stopped, or is active unless verified from the
  UI or another approved observation source.
- Do not read, summarize, OCR, describe, or infer private shared-screen content
  by default.
- Do not queue, start, or interrupt a running demo with Share from these
  prompts.
- Do not present unit tests, doctor output, localization output, or package
  routing as live RingCentral acceptance.

## Duplicate Alias And Matching Risks

The current shape is safer than broad aliases because the six prompts live under
the screen-sharing safety Q&A item. This preserves Q&A-first behavior and avoids
generic entrypoint answers such as:

`Screen sharing: Start sharing a screen, window, or selected content.`

Preserve that shape. If future work adds package-owned aliases, keep them
location-oriented, for example `where is Share` or `screen sharing button
location`. Do not add command aliases such as `share my screen`, `start
sharing`, `stop sharing`, `show my screen`, `read screen`, or `describe screen`
under the Share entrypoint.

Localized aliases need the same care. Spanish, Japanese, and Chinese may use
short phrases that can mean both "where is the control" and "perform the
action." When the phrase is action-shaped or content-reading-shaped, prefer
Q&A safety prompts over entrypoint aliases.

## Diagnostics And Localization Counts

Current diagnostics from
`ai-presenter doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo`:

- `question aliases`: `157` package-owned aliases, no cross-entrypoint
  duplicates.
- `qa questions`: `109` Q&A question prompts, no cross-item duplicates.
- `qa alias overlap`: `109` Q&A question prompts, no unsafe package-owned alias
  overlaps.
- `qa alias substring risk`: existing `INFO` with `11` prompts; Q&A-first
  matching still applies.
- Overall doctor shape: `11 ok, 1 info, 0 warnings, 0 failed`.

Current localization reports:

- Chinese: `51/51 demo steps`, `13/13 Q&A questions`, `13/13 Q&A answers`;
  aliases `15/27` entrypoints and `49` aliases.
- Japanese: `51/51 demo steps`, `14/14 Q&A questions`, `14/14 Q&A answers`;
  aliases `13/27` entrypoints and `34` aliases.

Future cycles should rerun doctor before changing exact count strings. The
Japanese Q&A count is currently one higher than Chinese because the package has
an additional Japanese-localized Q&A prompt in the current working tree.

## Recommended Test Guidance

Keep tests that prove:

- all six exact English prompts return the screen-sharing safety answer
- all six exact prompts keep `entrypoint_id == "ringcentral.video.toolbar.share"`
- all six exact prompts keep `can_operate is False`
- all six exact prompts create no interrupt step
- `Share my screen`, `Start sharing`, and `Show my screen` do not return thin
  `Screen sharing:` entrypoint text
- `Read the shared screen` and `Can you describe what's on screen?` do not use
  the older narrower shared-content answer if the intended contract is the
  broader screen-sharing safety Q&A
- location prompts still route to Share but remain non-operable
- diagnostics counts match the actual package inventory
- localization completion remains unchanged for supported package languages

Recommended verification for an implementation or review cycle:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py::test_ringcentral_english_screen_sharing_questions_stay_qa_first tests\unit\test_questions.py::test_ringcentral_localized_shared_screen_qa_returns_chinese_answer
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_questions_ok_for_ringcentral_package tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_alias_overlap_ok_for_ringcentral_package tests\unit\test_cli.py::test_doctor_loads_profile_package_and_flow
.\.venv\Scripts\ai-presenter.exe doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language zh
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ja
git diff --check -- packages\ringcentral-video.yaml tests\unit\test_questions.py tests\unit\test_diagnostics.py tests\unit\test_cli.py docs\agent-handoffs\cycle-159-risk-scan.md
```

Avoid coverage-producing commands unless requested. If `.coverage` is already
dirty, leave it untouched.

## Verification Performed

Commands run during this scan:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py::test_ringcentral_english_screen_sharing_questions_stay_qa_first tests\unit\test_questions.py::test_ringcentral_localized_shared_screen_qa_returns_chinese_answer
.\.venv\Scripts\ai-presenter.exe doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language zh
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ja
```

Results:

- Focused question tests: `7 passed`.
- Doctor: `11 ok, 1 info, 0 warnings, 0 failed`.
- Chinese localization report: `51/51 demo steps`, `13/13 Q&A questions`,
  `13/13 Q&A answers`.
- Japanese localization report: `51/51 demo steps`, `14/14 Q&A questions`,
  `14/14 Q&A answers`.

An earlier focused pytest run in this scan reported one failure for
`Share my screen`, returning thin `Screen sharing:` entrypoint text. A rerun and
direct probe after reloading the current working tree showed all six exact
prompts returning the intended screen-sharing safety Q&A. Treat any recurrence
of that failure as a blocker because it means command-shaped sharing prompts are
no longer consistently Q&A-first.

## Go/No-Go

Go if future implementation or review work:

- preserves the six exact prompts as Q&A-first safety prompts
- keeps all six non-operable with no interrupt step
- preserves location-style Share lookup behavior without turning it executable
- requires verified source plus user permission before describing shared
  content
- reruns focused question tests and doctor diagnostics after inventory changes
- describes the change as deterministic package-routing coverage, not live
  RingCentral acceptance

No-go if the change:

- lets any of the six prompts start or stop sharing
- lets any of the six prompts create a question interrupt step
- moves action-shaped or content-reading prompts to entrypoint aliases
- weakens the risky-word block for `share`, `start`, or `stop`
- reads or infers shared-screen content without an approved observation source
  and explicit user permission
- claims live RingCentral share picker, source selection, stop-sharing, or
  private-content reading acceptance
