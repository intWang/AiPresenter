# Controller App Selection And Questions Design

## Context

AiPresenter currently opens a small controller for one preselected desktop profile, one
material package, and one demo flow. Start, Pause, and End operate on that fixed demo session.
The RingCentral Video package path is stable, but the controller cannot yet choose another
prepared package, bind an already-running desktop app, answer user questions during a demo, or
build a reusable knowledge surface for apps without material packages.

The next controller iteration should make AiPresenter useful as both a prepared app presenter
and a fast app explorer.

## Goals

- Let the controller select the active demo target before starting.
- Support two target sources:
  - Existing material packages and their demo flows.
  - Currently running desktop apps with visible windows.
- For running apps without a material package, scan the selected window and generate an in-memory
  temporary material package with entrypoints, explainers, Q&A context, and a safe first demo flow.
- Keep Start, Pause, and End bound to the selected app session.
- Add a text question input and Submit button.
- Answer questions using the active package context.
- When a question maps to a safe, operable entrypoint, temporarily branch to that entrypoint,
  demonstrate it, then continue the original flow from a sensible next step.
- Let the user switch spoken output language between English and Chinese.
- Let the user switch presenter tone so spoken output can become more natural for the current
  demo context.

## Non-Goals For First Implementation

- Real-time voice input.
- Saving temporary packages as formal repo packages.
- Fully autonomous risky operations.
- Deep semantic understanding of arbitrary app business logic.
- Cross-window multi-app orchestration.
- Full multilingual localization beyond English and Chinese.
- Custom free-form voice design beyond the first tone presets.

## UX Design

The controller remains a compact desktop UI, but grows into four sections:

1. Target selector
   - Source selector: `Material package` or `Running desktop app`.
   - For material packages: package dropdown, flow dropdown, Refresh button.
   - For running apps: visible window dropdown, Scan button, Refresh button.
   - Status text shows the selected app/session.

2. Demo controls
   - Existing Start, Pause/Resume, and End buttons.
   - Buttons always operate on the current selected session.
   - Changing target while a demo is running is blocked until End completes.

3. Voice settings
   - Spoken language selector: `English` or `Chinese`.
   - Tone selector with first-version presets:
     - `Professional`: clear, structured, product-specialist delivery.
     - `Conversational`: warmer, more natural, less formal.
     - `Concise`: shorter sentences and faster transitions.
   - These settings apply to scripted demo narration, generated answers, and question-driven
     interrupt explanations.
   - Changing voice settings during a running demo applies to the next generated utterance; already
     playing audio is not interrupted.

4. Question box
   - Single-line text input.
   - Submit button.
   - Empty submissions are ignored.
   - Submitted questions are handled against the active session.

5. Answer/status area
   - Shows the latest answer summary, session state, or error.
   - For operable answers, shows which entrypoint was demonstrated.

## Architecture

### Controller Session Model

Introduce a controller-level session object that owns the selected target, demo control, current
package, selected flow, active runner thread, and latest error.

Core concepts:

- `ControllerTarget`: material package target or running app target.
- `ControllerSession`: selected target plus runtime state.
- `ControllerAppCatalog`: lists known packages and visible windows.
- `PresenterVoiceSettings`: selected language and tone for the active session.
- `QuestionRequest`: user text plus active session snapshot.
- `QuestionResponse`: answer text, optional entrypoint id, and whether the demo flow should resume.

The UI should not directly call `run_material_demo`. It should ask the session to start, pause,
end, scan, or answer a question.

### Voice Settings

Voice settings are session-level state:

- `language`: `en` or `zh`.
- `tone`: first-version preset such as `professional`, `conversational`, or `concise`.

Language affects the text that is sent to speech synthesis. For deterministic first-version
answers, templates should produce English or Chinese text directly. For OpenAI-backed narration,
the language and tone are added to the presenter context/instructions.

Tone affects phrasing, sentence length, pacing hints, and transition style. It should not change
the safety policy or cause the presenter to click different controls. The first implementation
can map tone to prompt/style text and template variants rather than creating a separate provider.

Speech provider selection remains explicit:

- English can use the current English Windows SAPI or OpenAI speech path.
- Chinese can use the current Chinese Windows SAPI or OpenAI speech path.
- If the selected profile cannot support the chosen language, the controller should show a clear
  status and refuse to start until the user changes language or profile.

### Material Package Target

For existing packages, the session loads:

- profile
- material package
- selected demo flow

Start runs the existing synchronized material demo path.

Questions use package `qa`, `explainers`, operation entrypoint titles, purposes, and presenter
notes. If a question maps to a package entrypoint with safe executable steps, the session pauses
the current flow, runs that entrypoint as an interrupting demo step, then resumes.

Answers should be rendered in the selected voice language and tone. Package source text can remain
English; translation or Chinese template rendering happens at answer/narration time.

### Running App Target

For running desktop apps, the catalog lists visible windows using process name, pid, class name,
title, and bounds. The first implementation can use Windows UI Automation and pywinauto-backed
window metadata already present in `WindowsDesktopDriver`.

Scan performs:

1. Bind selected window.
2. Capture screenshot, window metadata, and UI Automation text/control tree.
3. Build a temporary `MaterialPackage` in memory:
   - `appId`: derived from process and pid.
   - `appName`: title or process.
   - `profileIds`: synthetic profile id for the scanned app.
   - `operationEntrypoints`: generated from visible controls.
   - `demoFlows`: one generated safe overview flow.
   - `explainers`: generated from title, area, control names, and visible text.
   - `qa`: minimal app-level answers about visible controls.

Temporary packages should follow the same model validation as normal packages.

### Generic Entry Point Generation

Each visible control candidate becomes an entrypoint when it has:

- non-empty name
- visible bounds
- usable control type or clear UI Automation metadata

Generated entrypoints include:

- id: stable synthetic id, based on app id and normalized control label.
- title: control label.
- area: inferred from window title or nearby grouping when available.
- purpose: short generated sentence.
- openSteps: a conservative `clickWindowControl` step when safe; otherwise empty.
- presenterNotes: risk note, control type, and source metadata.

### Safety Policy

Generic scanning must classify controls before automatic operation.

Safe default controls:

- navigation tabs
- menus
- accordions
- view toggles
- settings/preferences buttons
- informational buttons

Risky controls are explain-only unless a later version adds confirmation:

- delete
- remove
- leave
- end
- send
- submit
- pay
- purchase
- transfer
- record
- share
- invite when user identity or external communication may be affected

If safety is unknown, default to explain-only.

### Question Handling

Question handling runs against the active session:

1. Normalize user question.
2. Search exact and fuzzy matches over:
   - entrypoint ids
   - titles
   - areas
   - purposes
   - explainer keys and text
   - QA questions
   - visible UI text for temporary packages
3. Build an answer:
   - Use package QA when direct match exists.
   - Otherwise synthesize from entrypoint purpose, explainer details, and presenter notes.
   - Render the answer in the active language and tone.
4. Decide action:
   - If best match has safe open steps, create an interrupt step and run it.
   - If unsafe or not executable, answer without clicking.
5. Resume:
   - The original demo flow continues after the current or next safe step.
   - If the question focused on a future step, the runner may skip ahead to avoid repeating.

First implementation can use deterministic matching and template-based answers. OpenAI-backed
semantic answers can be layered on after the flow mechanics are stable.

## Data Flow

### Material Package Demo

Controller UI -> ControllerSession -> Material package target -> `run_material_demo` ->
`SynchronizedTimelineRunner` -> `PackageActionExecutor`.

Question interrupt:

Question input -> Question handler -> entrypoint match -> interrupt `DemoStep` ->
timeline runner -> resume active flow.

### Running App Demo

Controller UI -> running app target -> scan window -> temporary `MaterialPackage` ->
generated flow -> same material demo runner path.

The goal is to reuse the package machinery after scan. Temporary packages should not create a
parallel runtime path unless a window lacks all usable controls.

## Error Handling

- If no visible windows are found, show an actionable controller status.
- If scan fails, keep the selected app but do not start a demo.
- If temporary package validation fails, show the validation message and keep scan artifacts in
  memory for debugging.
- If a question arrives before a session is selected or scanned, show "Select or scan an app first."
- If a question maps to a risky action, answer and explain why it was not clicked.
- If the selected spoken language is unsupported by the current profile/provider, show a voice
  configuration error before starting or answering.
- If an interrupt action fails, show the entrypoint id and failure context, then resume only if
  the runner is still healthy.
- If the active app window disappears, End the session and show a window-lost status.

## Testing Strategy

Unit tests:

- Catalog lists package targets and running app targets.
- Temporary package generation creates valid `MaterialPackage` instances from fake UI controls.
- Risk classifier marks destructive/external controls as explain-only.
- Question matcher selects QA, explainer, entrypoint title, and visible UI text matches.
- Question handler returns answer-only for risky actions and action+answer for safe actions.
- Voice settings choose English or Chinese answer text.
- Tone settings alter deterministic phrasing without changing matched entrypoints or safety.
- Unsupported language/provider combinations produce a clear validation error.
- Controller session binds Start/Pause/End to the selected target.
- Controller blocks target change during active demo.

Integration-style tests with fakes:

- Material package target still runs the existing RCV flow.
- Running app target scans a fake window, starts generated flow, pauses, resumes, and ends.
- Question interrupt executes a safe generated entrypoint and then resumes the demo.
- Question interrupt for a risky generated entrypoint does not click.

Manual acceptance:

- Start controller.
- Select RingCentral package and run `meeting-control-map-demo`.
- Ask "What does Invite do?" and verify answer plus app action.
- Switch language to Chinese and ask the same question; verify Chinese spoken/visible answer.
- Switch tone to Conversational and verify the answer is less formal while staying accurate.
- Select a running desktop app without a package.
- Scan it, start generated demo, ask about a visible safe control, and verify answer/action.
- Ask about a risky control and verify no click happens.

## Rollout Plan

1. Extract controller session state from Tk UI.
2. Add app/package catalog.
3. Add visible-window discovery.
4. Add temporary package generation for scanned windows.
5. Add question model, matcher, and deterministic answer builder.
6. Add session voice settings for English/Chinese and tone presets.
7. Add question interrupt execution.
8. Wire Tk UI.
9. Add docs and manual acceptance checklist.

This order keeps the UI as a thin shell over testable runtime units.
