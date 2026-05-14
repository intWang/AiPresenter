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

## Manual Acceptance

Use `docs/runbooks/ringcentral-manual-acceptance.md` for the RingCentral MVP checklist.

## Material Packages

App-level presenter knowledge lives under `packages/`. The first package is
`packages/ringcentral-video.yaml`; it covers RingCentral Video surfaces, operation entry points,
demo flows, concise explainers, anticipated Q&A, and manual control phrases.

VBG is modeled as one demo flow inside the RingCentral Video package, not as a separate app package.

## Synchronized Demo Flow

`src/ai_presenter/runtime/sync.py` runs package demo steps with narration placement set to
`before`, `during`, or `after`. `src/ai_presenter/runtime/manual.py` provides the first text
directive queue for live adjustment, including `say:` narration overrides and `skip`.
