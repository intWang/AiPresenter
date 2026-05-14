# AiPresenter Soul And Memory Design

## Goal

Give AiPresenter a durable presenter identity, a persistent memory file for user coaching, and reusable professional skills, then load them whenever a profile runs.

## Approach

Use Markdown files:

- `presenter/soul.md`: stable professional presenter identity, voice, boundaries, and operating principles.
- `presenter/memory.md`: durable user coaching and project-specific preferences, updated as the user gives feedback.
- `presenter/skills/*.md`: reusable professional capabilities referenced by the active profile.

Profiles reference these files from `narration.soulPath`, `narration.memoryPath`, and `narration.skillPaths`. Paths are resolved relative to the profile YAML, so the files can move with the repo and still load from CLI commands.

## Runtime Behavior

Profile loading validates and resolves the configured paths. Provider creation loads the presenter context once and injects it into generated narration prompts for OpenAI and Codex CLI providers. Scripted demo flows still use their package text, but the same profile context is available to future narration and voice-interaction features.

## Initial Content

The soul file gives AiPresenter the role of a professional live software presenter: natural English, confident pacing, clean transitions, privacy awareness, and practical feature explanations grounded in verified UI.

The memory file captures the user's durable feedback:

- Use English for RingCentral Video demos.
- Avoid stiff Chinese phrasing.
- Keep feature transitions natural.
- Avoid long pauses between topics.
- Keep audio and UI actions synchronized.
- Cover Meeting controls completely.
- Close or handle foreground dialogs before continuing.

The initial skill files add two professional capabilities:

- App director: slice app surfaces into natural, audience-friendly feature sections and plan a clear demo arc.
- Live explainer: pace speech, handle pauses, respond to user questions, recover from unexpected UI, and return naturally to the main thread.

## Future Extension

Automatic memory can later append confirmed user coaching from microphone input, but the first version keeps memory manual and auditable.

## Verification

Tests should prove:

- Profile config accepts and resolves `soulPath`, `memoryPath`, and `skillPaths`.
- Missing configured files fail early.
- Presenter context loads Markdown content.
- OpenAI and Codex CLI narration prompts include soul, memory, and skill text.
