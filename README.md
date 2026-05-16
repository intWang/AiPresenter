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

Run this before scripted demos to confirm the exact `--flow` id you plan to use.

List available package entrypoints, optionally filtered by area:

```powershell
.venv\Scripts\ai-presenter entrypoints --package ringcentral-video --area "Meeting toolbar"
```

Check package localization coverage without running automation:

```powershell
.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language zh
.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language zh --require-complete
```

Discover presenter voice aliases and check a profile's voice routes:

```powershell
.venv\Scripts\ai-presenter voices
.venv\Scripts\ai-presenter voices --profile ringcentral-video-bind-speaker
.venv\Scripts\ai-presenter doctor --profile ringcentral-video-bind-speaker --language zh-CN --tone friendly
```

`voices --profile ...` also reports local speech asset status for supported local routes.
For a strict pre-demo check, run `doctor --profile ... --language ... --tone ...`; missing SAPI
voices or Piper model files fail before a demo launches.

Before a real demo, run the diagnostic command to catch profile, package, flow, presenter-context,
and RingCentral capture-prerequisite issues early. When RingCentralVideo is already running,
`doctor` will try to discover the executable directory automatically; pass `--ringcentral-config`
when you want to check a specific `config.ini`.

```powershell
.venv\Scripts\ai-presenter doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo --ringcentral-config "C:\Path\To\RingCentralVideo\config.ini"
```

```powershell
.venv\Scripts\ai-presenter demo --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo --language zh-CN --tone friendly
```

For a small local control surface with Start, Pause, and End:

```powershell
.venv\Scripts\ai-presenter controller --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo --language English --tone coach
```

Regional aliases such as `zh-CN` and `en-US` normalize to the Chinese and English output
families. Tone aliases such as `warm` and `mentor` normalize to canonical labels in the
`Loaded voice` output.
Voice compatibility is checked before demo launch. The fake speech profile is suitable for
default English smoke tests; Chinese output requires OpenAI or the Windows SAPI Chinese route.

The controller starts in Target > Material package mode and shows the selected package and flow.
In Target > Running desktop app mode, Refresh lists visible windows, Scan reads the selected
window's visible controls, and the controller creates a temporary package for text questions.
Safe matched controls can be answered as operable entrypoints; risky controls remain answer-only.
The controller also includes language and tone selectors plus a text question box.

## Piper TTS

For a free local neural TTS test:

```powershell
.venv\Scripts\python -m pip install piper-tts
.venv\Scripts\python -m piper.download_voices --download-dir "$env:USERPROFILE\.cache\ai-presenter\piper-voices" en_US-lessac-medium
.venv\Scripts\ai-presenter controller --profile ringcentral-video-piper-speaker --package ringcentral-video --flow meeting-control-map-demo
```

The first Piper voice download can take a little while. The profile outputs to the configured speaker device.

## Manual Acceptance

Use `docs/runbooks/ringcentral-manual-acceptance.md` for the RingCentral MVP checklist,
including the controller target, question, language, tone, and running-app scan acceptance path.

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
