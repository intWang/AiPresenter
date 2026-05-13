# RingCentral Manual Acceptance

## Preconditions

- `RingCentralDevelop` is installed, open, and already logged in.
- The profile `profiles/ringcentral-video.yaml` loads successfully.
- A virtual audio device such as VB-CABLE or VoiceMeeter is installed when testing virtual microphone output.
- `OPENAI_API_KEY` and `AI_PRESENTER_OPENAI_NARRATION_MODEL` are set when testing OpenAI providers.

## Checklist

- [ ] Run `.venv\Scripts\ai-presenter run --profile ringcentral-video --dry-run`.
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
- [ ] Enable speaker output and confirm local playback.
- [ ] Enable virtual microphone output and confirm RingCentral receives audio from the configured virtual device.
- [ ] Review logs for profile load, launch steps, binding, observations, events, narration generation, and media output status.
