# RingCentral Manual Acceptance

## Preconditions

- `RingCentralDevelop` is installed, open, and already logged in.
- The profile `profiles/ringcentral-video.yaml` loads successfully.
- A virtual audio device such as VB-CABLE or VoiceMeeter is installed when testing virtual microphone output.
- In the RingCentralVideo executable directory, `config.ini` has `DisableAffinityMask=true` so meeting child
  windows can be captured reliably.

## Smoke Checklist

This uses the default fake providers. It verifies desktop automation, window binding, state detection, event filtering, and logging. It does not prove audible speech or OpenAI behavior.

- [ ] Run `.venv\Scripts\ai-presenter run --profile ringcentral-video --dry-run` from the repo root.
- [ ] Run `.venv\Scripts\ai-presenter demo --profile ringcentral-video --package ringcentral-video --flow meeting-control-map-demo --dry-run`.
- [ ] Run `.venv\Scripts\ai-presenter controller --profile ringcentral-video --package ringcentral-video --flow meeting-control-map-demo --dry-run`.
- [ ] From another directory, run `<repo>\.venv\Scripts\ai-presenter run --profile ringcentral-video --dry-run`.
- [ ] Confirm the profile loads without validation errors.
- [ ] Open `RingCentralDevelop` and confirm the user is logged in.
- [ ] Run `.venv\Scripts\ai-presenter run --profile ringcentral-video --iterations 1`.
- [ ] Confirm the Video tab is selected.
- [ ] Confirm Start is clicked.
- [ ] Confirm `RingCentralVideo` starts.
- [ ] Confirm the runner binds a window with class `RingCentralVideoClass`.
- [ ] Confirm meeting joined state is detected only after in-meeting controls are visible.
- [ ] Toggle microphone and confirm one narration event.
- [ ] Toggle camera and confirm one narration event.
- [ ] Change participant count and confirm one narration event.
- [ ] Review logs for profile load, launch steps, binding, observations, events, narration generation, and media output status.

## Real Audio And OpenAI Checklist

This uses `profiles/ringcentral-video-openai.example.yaml`, which switches narration and speech to OpenAI while keeping RingCentral state recognition deterministic through the adapter.

- [ ] Set `OPENAI_API_KEY`.
- [ ] Set `AI_PRESENTER_OPENAI_NARRATION_MODEL`.
- [ ] Optionally set `AI_PRESENTER_OPENAI_TTS_MODEL`; when omitted, speech uses the built-in TTS model default.
- [ ] Confirm `profiles/ringcentral-video-openai.example.yaml` points `virtualMicDevice` to the installed virtual audio device.
- [ ] From the repo root, run `.venv\Scripts\ai-presenter run --profile profiles\ringcentral-video-openai.example.yaml --dry-run`.
- [ ] From the repo root, run `.venv\Scripts\ai-presenter run --profile profiles\ringcentral-video-openai.example.yaml --iterations 1`.
- [ ] Confirm local speaker playback contains audible presenter speech.
- [ ] Confirm RingCentral receives audio from the configured virtual microphone device.
