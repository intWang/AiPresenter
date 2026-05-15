# AI Presenter

Config-driven AI presenter MVP for desktop app profiles.

## Setup

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -U pip
.venv\Scripts\python -m pip install -e ".[dev]"
```

## Run

```powershell
.venv\Scripts\ai-presenter run --profile ringcentral-video
```

The RingCentral MVP assumes `RingCentralDevelop` is already open and logged in.
The bundled `ringcentral-video` profile uses fake narration and speech providers for smoke testing.
Use `profiles\ringcentral-video-openai.example.yaml` when manually accepting real OpenAI narration and audio output.

## Run A Material Demo

List available demo flows:

```powershell
.venv\Scripts\ai-presenter flows --package ringcentral-video
```

List available package entrypoints, optionally filtered by area:

```powershell
.venv\Scripts\ai-presenter entrypoints --package ringcentral-video --area "Meeting toolbar"
```

Before a real demo, run the diagnostic command to catch profile, package, flow, presenter-context,
and RingCentral capture-prerequisite issues early. When RingCentralVideo is already running,
`doctor` will try to discover the executable directory automatically; pass `--ringcentral-config`
when you want to check a specific `config.ini`.

```powershell
.venv\Scripts\ai-presenter doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo --ringcentral-config "C:\Path\To\RingCentralVideo\config.ini"
```

```powershell
.venv\Scripts\ai-presenter demo --profile ringcentral-video --package ringcentral-video --flow meeting-control-map-demo
```

For a small local control surface with Start, Pause, and End:

```powershell
.venv\Scripts\ai-presenter controller --profile ringcentral-video --package ringcentral-video --flow meeting-control-map-demo
```

The controller includes language and tone selectors plus a text question box. Text questions are
answered from the active material package. Safe matched controls can later be demonstrated as
interrupt steps; risky controls are answer-only.

## Manual Acceptance

Use `docs/runbooks/ringcentral-manual-acceptance.md` for the RingCentral MVP checklist.

## Material Packages

App-level presenter knowledge lives under `packages/`. The first package is
`packages/ringcentral-video.yaml`; it covers RingCentral Video surfaces, operation entry points,
demo flows, concise explainers, anticipated Q&A, and manual control phrases.

VBG is modeled as one demo flow inside the RingCentral Video package, not as a separate app package.

## Presenter Soul And Memory

Presenter identity and durable coaching live under `presenter/`:

- `presenter/soul.md` defines the professional presenter role, voice, and safety boundaries.
- `presenter/memory.md` records durable user feedback, such as English RingCentral Video narration,
  tighter transitions, synchronized action timing, and complete Meeting coverage.
- `presenter/skills/` extends professional capabilities. The initial skills cover app-demo
  direction and live explanation behavior.

Profiles load these files through `narration.soulPath`, `narration.memoryPath`, and
`narration.skillPaths`.

## Synchronized Demo Flow

`src/ai_presenter/runtime/sync.py` runs package demo steps with narration placement set to
`before`, `during`, or `after`. `src/ai_presenter/runtime/manual.py` provides the first text
directive queue for live adjustment, including `say:` narration overrides and `skip`.
