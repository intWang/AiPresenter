# Cycle 019 Demand Analysis: Controller Visibility And Responsiveness

Date: 2026-05-16
Role: demand-analysis worker
Write scope: this file only

## Read Scope

Reviewed local repository context only:

- `src/ai_presenter/runtime/controller.py`
- `src/ai_presenter/runtime/controller_view_model.py`
- `tests/unit/test_controller.py`
- `tests/unit/test_controller_view_model.py`
- `docs/agent-handoffs/cycle-016-summary.md`
- `docs/agent-handoffs/cycle-017-summary.md`
- `docs/agent-handoffs/cycle-018-summary.md`
- `docs/runbooks/ringcentral-manual-acceptance.md`

No live RingCentral actions were run. No production code, tests, package YAML,
runbook, or knowledge docs were edited.

## 1. Operator Problem

Cycles 016-018 improved the controller and RingCentral validation workflow in
important but separate ways:

- Cycle 016 made voice asset readiness visible and made Start/Submit respect
  missing local assets.
- Cycle 017 made manual RingCentral validation targets easier to discover.
- Cycle 018 made offline acceptance-record drafting safer and less repetitive.

The remaining controller problem is not missing automation coverage. It is that
the live operator surface still compresses too much state into one long summary
line and refreshes it every 500 ms, even though most fields change only after an
operator action. During a demo, the operator needs to quickly answer:

- What target is selected?
- Is the running-app target scanned and still valid?
- Is the selected voice usable?
- Is the controller running, paused, ending, or answering a question?
- Why is Start, Scan, or Submit disabled?
- Did my question queue a safe demonstration, start one, or stay text-only?

Today those answers are present, but they are packed into one string:

`Source | Target | Flow | Voice | Voice assets | Scan | Question`

That is useful for tests and compact display, but it is hard to scan under live
operator pressure. It also makes future status additions risky because every new
operator signal lengthens the same row. The controller now has enough
visibility features that the product demand is for clearer presentation and a
slightly calmer refresh model, not a larger RingCentral automation change.

## 2. Proposed Small Scope And Out-of-Scope

Recommended scope: improve controller operator visibility and perceived
responsiveness by refining the view-model output and Tk presentation without
changing automation behavior.

In scope:

- Keep the existing pure `ControllerOperatorViewModel` boundary, but add small
  display fields that make disabled-action reasons explicit, such as
  `target_status_label`, `voice_status_label`, `action_status_label`, or a
  single concise `next_action_label`.
- Replace or supplement the single dense `operator_summary` line in the Tk
  controller with stable labeled rows for target, voice, scan, and question
  status. This should be a layout/readability change, not a new workflow.
- Preserve all current button gating rules: Start requires target readiness and
  voice readiness; Scan/Refresh stay disabled while running; Submit stays
  blocked while stopping and when running-app scan is required.
- Reduce avoidable polling churn by ensuring the 500 ms status refresh does not
  perform fresh expensive checks. Cycle 016 already caches voice readiness; this
  slice should keep that behavior and make the intent explicit in tests or
  helper boundaries if implementation touches it.
- Make question outcomes more operator-readable while keeping the existing
  safety distinction: queued safe demo, started safe demo, answered-only risky
  route, answered-only no safe route, and current demo ending.
- Add focused unit tests in the view model and controller status helpers. If Tk
  layout is changed, keep it covered through pure view-model expectations rather
  than requiring live GUI automation.
- Update the controller acceptance checklist only if the visible controller text
  changes materially; otherwise keep the cycle implementation code/test-only.

Out-of-scope:

- Running, clicking, scanning, or validating live RingCentral.
- Changing RingCentral package routes, locators, evidence state, route safety,
  or acceptance-record behavior.
- Adding new automation actions or making risky routes executable.
- Replacing Tk, adding async frameworks, or rebuilding the controller UI.
- Adding screenshots, visual diffing, or GUI automation unless already supported
  by the local test harness.
- Changing speech provider routing, voice aliases, SAPI/Piper asset detection,
  or OpenAI behavior.
- Adding route metadata to package YAML; Cycle 017 already deferred that to a
  separate schema cycle.

## 3. Acceptance Criteria

A future Cycle 019 implementation should be accepted when:

- The controller presents target, flow, voice readiness, scan state, run state,
  and last question outcome in a form that is readable at a glance without
  relying on one long pipe-delimited summary string.
- The operator can see why Start is unavailable when:
  - the running desktop app has not been scanned;
  - selected local voice assets are missing;
  - the controller is already running or ending.
- The operator can see why Submit is unavailable when:
  - the question field is empty;
  - a running desktop app needs scanning;
  - selected local voice assets are missing;
  - the controller is ending.
- Running, paused, ending, and switching-to-answer states remain visible and
  continue to drive Pause/End labels and button enablement correctly.
- Existing safe-question behavior is unchanged:
  - safe questions queue while a demo is running;
  - safe questions start a focused demo while idle;
  - risky questions answer text-only and do not click;
  - ending demos answer text-only rather than starting new work.
- Existing running-app scan safety is unchanged: selecting or refreshing away
  from a scanned window clears the scanned state and blocks Start/Submit until
  the current selection is scanned again.
- The 500 ms refresh path does not call fresh voice asset checks on every tick
  for the same selected language/tone. Fresh checks remain appropriate on
  deliberate Start/Submit attempts and when language or tone changes.
- Focused tests cover the new labels or disabled-action reasons for material
  package mode, unscanned running-app mode, scanned running-app mode, missing
  voice assets, running state, ending state, and last question outcome.
- Existing controller and view-model tests still pass without requiring
  RingCentral, SAPI/Piper installation, or live desktop automation.

## 4. UX And Performance Risks

- Visibility risk: adding more labels can make the controller noisier if the UI
  simply expands the existing summary. Prefer a compact status area with stable
  rows over paragraphs or verbose help text.
- Operator trust risk: disabled buttons must have nearby reasons. A cleaner UI
  that hides the reason for a disabled Start or Submit would be a regression.
- Safety risk: making question outcomes more prominent must not make risky
  routes feel executable. Keep wording like `Answered only` for unsafe controls.
- Polling risk: Tk's `root.after(500, refresh_status)` is simple and adequate,
  but any fresh desktop scan, package scan, or voice asset probe inside that loop
  can make the controller feel sluggish. The refresh loop should read cached
  state and lightweight controller properties only.
- Threading risk: the controller reads `is_running`, `is_stopping`,
  `is_switching_targets`, and `last_error` from a background demo thread. This
  cycle should avoid deeper concurrency changes unless tests expose a concrete
  race.
- Layout risk: the window is currently `720x500`. Splitting status into rows
  should not crowd the question entry or chat history. Keep labels short and
  avoid adding large instructional text.
- Scope risk: Cycle 017 and 018 created tempting evidence/acceptance features.
  Pulling those into the controller now would blur the safety boundary and make
  RingCentral behavior harder to reason about.

## 5. Priority And Recommendation

Priority: medium-high for operator quality, low for automation breadth.

Recommendation: make Cycle 019 a focused controller polish/performance slice.
The best small product increment is not a new RingCentral route or a live
acceptance run; it is clearer operator state and cheaper refresh behavior in
the existing controller surface. This builds directly on Cycle 016's voice
readiness work, respects Cycle 017/018 safety boundaries, and can be verified
with unit tests around the pure view model and controller status helpers.

Suggested implementation target: add concise view-model labels for "why Start
or Submit is blocked" and present target/voice/scan/question status as stable
rows in Tk. Keep all RingCentral automation, scan behavior, and question safety
semantics unchanged.
