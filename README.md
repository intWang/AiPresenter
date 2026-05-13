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

## Manual Acceptance

Use `docs/runbooks/ringcentral-manual-acceptance.md` for the RingCentral MVP checklist.
