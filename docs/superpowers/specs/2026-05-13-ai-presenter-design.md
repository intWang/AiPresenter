# AI Presenter Design

Date: 2026-05-13

## Goal

Build a config-driven AI presenter MVP that can run a predefined application flow, observe the target app in real time, generate concise narration from verified UI state and meeting events, and output the generated voice through both local speakers and a virtual microphone.

The first supported app profile is RingCentral:

- Start from an already logged-in and already open `RingCentralDevelop` window.
- Open the Video tab and click Start.
- Detect the launched `RingCentralVideo` process.
- Bind to the meeting window with class `RingCentralVideoClass`.
- Observe RingCentral meeting UI state and events.
- Generate dynamic narration for meeting UI state and meeting events.
- Output TTS audio to local speakers, a configured virtual microphone, or both.

RingCentralVideo is the reference app profile, not a special case in the core runtime. The architecture must support later desktop and browser app profiles, plus future virtual avatar video output.

## Non-Goals For MVP

- Do not automate login. The user must already be logged in.
- Do not build a GUI. The MVP is a CLI.
- Do not support workflow recording or natural-language workflow authoring.
- Do not interpret shared screen or presentation content.
- Do not install or manage virtual audio drivers.
- Do not generate or output virtual avatar video in the MVP.
- Do not inject audio directly into RingCentral internals. Use configured OS audio devices.

## Product Shape

The MVP is a command-line runner:

```powershell
ai-presenter run --profile ringcentral-video
```

The runner loads a profile, executes the launch phase, binds to the target presentation window, then starts the presenter loop. The console shows operational status and errors. Runtime logs capture observations, state transitions, events, generated narration, and media output results.

## Architecture

The system is app-profile first. The core runtime owns orchestration and provider boundaries; app profiles own app-specific launch, binding, state, event, and narration rules.

### Core Runtime

The core runtime must not hardcode RingCentral behavior. It provides:

- `ProfileRunner`: loads and validates a profile, then runs launch and presenter phases.
- `AutomationDriver`: executes app automation primitives. It has desktop and browser implementations.
- `WindowMonitor`: locates and tracks target app windows, process metadata, focus, visibility, and lifecycle.
- `ObservationPipeline`: collects screenshots, accessibility/UI trees, process/window metadata, and app-specific observations.
- `StateReducer`: turns raw observations into structured state.
- `EventDetector`: compares current and previous state to produce meaningful events.
- `NarrationEngine`: turns verified state and events into concise narration while enforcing profile policy.
- `MediaOutput`: sends generated audio or future video to configured output targets.
- `ProviderRegistry`: resolves vision, narration, speech, and future media providers.

### App Profiles And Adapters

Each supported app is represented by a profile and, when needed, an adapter module.

Profiles define stable configuration:

- app type: `desktop` or `browser`
- launch steps
- window/process binding rules
- observation sources
- state fields
- event types
- narration policy
- media output configuration
- provider configuration references

Adapters handle logic that is too app-specific or fragile for pure YAML, such as locating RingCentral controls, interpreting app-specific UI regions, or applying recovery rules.

### RingCentral Reference Profile

The first profile is `ringcentral-video`.

It assumes:

- `RingCentralDevelop` is already running.
- The user is already logged in.
- The Video tab can be opened from the main app window.
- Clicking Start launches a separate `RingCentralVideo` process.
- The meeting window class is `RingCentralVideoClass`.

The RingCentral adapter is responsible for:

- focusing the `RingCentralDevelop` window
- navigating to the Video tab
- clicking Start
- waiting for `RingCentralVideo`
- binding the `RingCentralVideoClass` window
- extracting RingCentral-specific UI state from screenshots and UI Automation data

## Data Flow

The presenter phase uses an observe, reduce, detect, narrate, output loop.

1. `WindowMonitor` tracks the target `RingCentralVideoClass` window and reports process exit, window loss, minimize state, focus changes, and class mismatch.
2. `ObservationPipeline` captures window screenshots, Windows UI Automation information, window title, process name, process id, window class, bounds, and focus state.
3. The RingCentral adapter extracts app-specific signals where possible, such as microphone state, camera state, active dialogs, participant count, and meeting joined state.
4. `StateReducer` merges raw observations into a structured state object.
5. `EventDetector` compares state snapshots and emits events only for meaningful changes.
6. `NarrationEngine` builds a short narration from verified events and current state.
7. `SpeechProvider` converts narration text to audio.
8. `MediaOutput` sends audio to configured outputs: speaker, virtual microphone, or both.
9. Logs record each state snapshot, event, narration, provider result, and output result.

## Profile Configuration

The initial profile format is YAML. Example:

```yaml
id: ringcentral-video
type: desktop

launch:
  appProcess: RingCentralDevelop
  requireAlreadyLoggedIn: true
  steps:
    - action: focusWindow
      match:
        process: RingCentralDevelop
    - action: clickTab
      target: Video
    - action: clickButton
      target: Start

bind:
  process: RingCentralVideo
  windowClass: RingCentralVideoClass
  timeoutMs: 30000

observe:
  intervalMs: 1000
  sources:
    - screenshot
    - windowsUiAutomation
    - windowMetadata

events:
  - meeting_joined
  - mic_state_changed
  - camera_state_changed
  - participant_count_changed
  - dialog_appeared
  - connection_warning

narration:
  style: concise_presenter
  maxSentences: 2
  minSecondsBetweenUtterances: 4
  repeatCooldownSeconds: 30
  confidenceThreshold: 0.75
  forbidSharedScreenInterpretation: true

audio:
  output: both
  speakerDevice: default
  virtualMicDevice: "VB-CABLE Input"

providers:
  vision: default-cloud-vision
  narration: default-cloud-llm
  speech: default-cloud-tts
```

Provider credentials are not stored in profiles. They are loaded from environment variables or a later secrets provider.

## AI Recognition And Narration

The AI layer is constrained. It is not a free-form agent.

Rules:

- Prefer deterministic signals from Windows UI Automation, window metadata, process state, and app adapters.
- Use vision models only for UI signals that deterministic sources cannot reliably provide.
- Vision models return schema-validated structured state, not final narration.
- Low-confidence state is logged and ignored for narration.
- Events drive narration. The system does not speak on every polling interval.
- Narration must be limited to verified meeting UI state and meeting events.
- Narration must not infer shared-screen content.
- Narration must not invent participants, meeting intent, or private content.
- Repeated events are suppressed by cooldown.
- Recent narration and state are kept in memory to avoid redundant speech.

Example structured recognition output:

```json
{
  "meetingJoined": true,
  "micMuted": true,
  "cameraOff": false,
  "activeDialog": null,
  "participantCount": 3,
  "confidence": 0.86
}
```

## Media Output

MVP audio output supports:

- `speaker`: play TTS through local speaker output.
- `virtual_mic`: send TTS audio to a configured virtual microphone device.
- `both`: send the same TTS output to both.

The virtual microphone implementation assumes the user has installed and configured a virtual audio device such as VB-CABLE, VoiceMeeter, or an equivalent driver. The app chooses and writes to that device; it does not install the driver.

The output layer is named `MediaOutput` rather than `TtsOutput` so the same boundary can later support:

- `AvatarVideoOutput`: generate a virtual human presenter video.
- virtual camera output
- video stream output
- synchronized avatar video and TTS audio

Virtual avatar generation and video output are explicit future work and are not part of MVP acceptance.

## Error Handling

The CLI should fail fast for unrecoverable setup errors and continue safely for transient observation errors.

Unrecoverable errors:

- profile validation fails
- `RingCentralDevelop` is not found
- user is not logged in or the Video tab cannot be reached
- Start cannot be clicked after configured retries
- `RingCentralVideo` does not appear before timeout
- no window with class `RingCentralVideoClass` can be bound
- configured virtual microphone device is required but unavailable
- required provider credentials are missing

Recoverable errors:

- a single screenshot capture fails
- UI Automation returns partial data
- a vision provider call times out
- recognition confidence is below threshold
- TTS generation fails for one event
- speaker output fails while virtual microphone output succeeds, or the reverse, when output mode is `both`

Recoverable errors are logged and skipped for the current loop. The runtime must not narrate uncertain or stale state as fact.

## Logging And Observability

Logs must make the run debuggable without exposing unnecessary sensitive content.

Required log categories:

- profile load and validation
- launch step start, success, retry, and failure
- window/process binding details
- observation source status
- structured state snapshots
- emitted events
- narration text
- provider latency and errors
- media output status
- shutdown reason

Screenshots can be saved only when an explicit debug flag is enabled. Debug captures should be stored under an ignored runtime directory.

## Security And Privacy

The system observes app windows and may send screenshots or extracted UI text to cloud providers in the MVP. This must be explicit in configuration and logs.

Requirements:

- No API keys or credentials in source files or profiles.
- Provider keys are read from environment variables or a later secrets provider.
- Profiles must declare whether cloud vision or cloud narration is enabled.
- Screenshot capture is limited to the bound target window, not the full desktop.
- Shared-screen content interpretation is disabled for the MVP.
- Saved screenshots require explicit debug mode.
- Error messages must not print provider secrets.

The provider architecture must allow future local-model replacements for vision, narration, and speech.

## Testing Strategy

Unit tests:

- profile schema validation
- launch plan parsing
- state reducer behavior
- event detection
- narration cooldown and de-duplication
- provider interface error handling
- media output routing mode selection

Integration tests:

- RingCentral profile loads and resolves adapter dependencies
- recorded screenshot fixtures produce expected structured state
- UI Automation fixtures produce expected structured state
- state snapshots produce expected event sequences
- speech audio is routed to mocked speaker and virtual microphone outputs

Manual acceptance:

- User opens `RingCentralDevelop` and confirms they are logged in.
- CLI runs `ai-presenter run --profile ringcentral-video`.
- Runner opens the Video tab and clicks Start.
- Runner detects `RingCentralVideo` and binds `RingCentralVideoClass`.
- Presenter loop identifies meeting UI state and event changes.
- Presenter generates short narration only for verified UI state/events.
- Speaker output plays locally when enabled.
- Virtual microphone output is received by RingCentral when configured.
- Logs show the launch, binding, observations, events, narration, and output status.

Out of automated test scope:

- real RingCentral authentication
- real meeting network quality
- virtual audio driver installation
- cloud provider uptime

## Acceptance Criteria

The MVP is accepted when:

1. The CLI can run the `ringcentral-video` profile from an already logged-in `RingCentralDevelop` session.
2. The launch phase reliably starts the meeting and binds the `RingCentralVideoClass` window.
3. The presenter phase detects at least meeting joined state, microphone state, camera state, active dialog, and participant count changes.
4. Narration is event-driven, concise, non-repetitive, and limited to verified RingCentral meeting UI state/events.
5. Audio can be routed to speaker, virtual microphone, or both through configuration.
6. Runtime logs are sufficient to diagnose launch, recognition, narration, and output failures.
7. The core runtime remains app-agnostic, with RingCentral implemented as the first app profile and adapter.
8. The design leaves explicit extension points for browser profiles, local AI providers, virtual audio driver management, and virtual avatar video output.

## Future Work

- Browser automation profiles for Web apps.
- Workflow recorder for creating profiles from user actions.
- Natural-language profile authoring.
- Local vision, narration, and speech providers.
- App-managed virtual audio driver setup.
- Virtual avatar video generation.
- Virtual camera output.
- Shared screen and presentation content understanding.
- Desktop GUI for profile selection, status, logs, and Start/Stop controls.
