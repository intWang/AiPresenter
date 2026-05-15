# Piper TTS Engine Design

## Goal

Add a free, friendlier TTS option for AiPresenter demos without removing existing speech providers. The first engine is Piper TTS because it can run locally, does not require an API key, and produces more natural English than Windows SAPI.

## Scope

- Add a `piper` speech provider that returns WAV audio compatible with the existing `MediaOutput` pipeline.
- Add one RingCentral test profile that uses `providers.speech: piper` and speaker output.
- Keep `fake`, `windows-sapi`, `windows-sapi-en`, `windows-sapi-zh`, and `openai` unchanged.
- Add automated unit coverage around command construction, audio validation, and provider registration.
- Add a smoke path for manually synthesizing one short English line.

## Architecture

`PiperSpeechProvider` will live in `src/ai_presenter/providers/piper_provider.py`. It will call Piper through the installed Python module with a subprocess:

```powershell
python -m piper -m en_US-lessac-medium -f output.wav -- "text"
```

The provider will accept `voice`, `data_dir`, `download_dir`, and `timeout_seconds` options with conservative defaults. Generated WAV bytes are read into `SpeechAudio` and then played through the existing `SoundDeviceSink` / `CombinedOutput` layer.

## Configuration

`create_provider_registry()` will register `piper` when a profile uses `providers.speech: piper`. The initial profile will be:

```yaml
profiles/ringcentral-video-piper-speaker.yaml
```

It will mirror `ringcentral-video-bind-speaker.yaml`, but set `speech: piper`.

## Error Handling

The provider will fail fast with clear messages when Piper is missing, exits non-zero, times out, or writes an empty WAV. It will not silently fall back to SAPI because that would hide TTS quality problems during demos.

## Testing

Unit tests will mock subprocess execution and verify:

- valid text produces `SpeechAudio` from a WAV file,
- blank text is rejected,
- non-zero Piper exits include stderr,
- provider registration works for a `piper` profile.

Manual acceptance will run the piper profile and synthesize one short line before using it in a full RingCentral demo.
