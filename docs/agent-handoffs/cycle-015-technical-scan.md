# Cycle 015 Technical Scan: Local Voice Asset Availability

Date: 2026-05-16

## Current Architecture Summary

- `PresenterVoiceSettings` in `src/ai_presenter/runtime/voice.py` normalizes language/tone and owns provider compatibility through `validate_profile_voice()` and `resolve_speech_provider_name()`.
- Chinese local speech currently routes to `windows-sapi-zh` for `piper`, `windows-sapi`, and English/Chinese SAPI profiles. English from `windows-sapi-zh` routes to `windows-sapi-en`.
- `create_provider_registry()` in `src/ai_presenter/runtime/factory.py` hard-codes SAPI voice selectors: `Zira` for English and `Huihui` for Chinese. Piper uses `PiperSpeechProvider()` defaults.
- `WindowsSapiSpeechProvider` only validates actual voice existence during synthesis, via private `_select_voice()`.
- `PiperSpeechProvider` shells out to `python -m piper -m <voice>` and defaults data dir to `%AI_PRESENTER_PIPER_DATA_DIR%` or `~/.cache/ai-presenter/piper-voices`; it has no preflight API.
- `diagnose_configuration()` already has an optional `voice` parameter used by CLI `doctor --language/--tone`. This is the safest insertion point because regular fake profiles and runtime dry runs do not need asset checks.

## Recommended Changes

- Add provider probe helpers, keeping synthesis behavior unchanged:
  - `src/ai_presenter/providers/windows_speech.py`
    - Add `InstalledSapiVoice` dataclass with `name: str` and maybe `id: str | None`.
    - Add `list_installed_sapi_voices(loader: Callable[[], Any] | None = None) -> tuple[InstalledSapiVoice, ...]`.
    - Add `sapi_voice_available(voice_name: str, voices: Iterable[InstalledSapiVoice]) -> bool` using the same case-insensitive substring match as `_select_voice()`.
    - Keep COM import/dispatch isolated so tests can inject fake voices and non-Windows hosts do not import `win32com`.
  - `src/ai_presenter/providers/piper_provider.py`
    - Add `PiperVoiceAssets` dataclass with `voice: str`, `model_path: Path`, `config_path: Path`.
    - Add `default_piper_voice_assets(voice: str = "en_US-lessac-medium", data_dir: Path | None = None) -> PiperVoiceAssets`.
    - Add `piper_voice_assets_available(assets: PiperVoiceAssets) -> bool`, checking both `.onnx` and `.onnx.json` locally.
    - Use the same `_default_data_dir()` and `_require_nonblank()` rules as `PiperSpeechProvider`.
- Add diagnostics glue:
  - `src/ai_presenter/runtime/diagnostics.py`
    - Add `_diagnose_voice_assets(profile, voice, *, sapi_voice_lister=list_installed_sapi_voices, piper_asset_resolver=default_piper_voice_assets) -> DiagnosticCheck | None`.
    - Call it after `_diagnose_voice()` only when `voice is not None` and compatibility passed.
    - Use `resolve_speech_provider_name(profile, voice)` to check the actual route, not the configured provider.
    - For `windows-sapi-en`, expect `Zira`; for `windows-sapi-zh`, expect `Huihui`; for plain `windows-sapi`, either skip with `WARN` or check that at least one SAPI voice is installed.
    - For `piper`, check the default Piper voice assets currently used by `PiperSpeechProvider()`.
    - Return `None` for `fake`, `openai`, and unsupported voice routes so fake/test profiles stay unaffected.
- CLI likely needs no new options if diagnostics run only when `doctor` receives `--language` or `--tone`. Avoid adding asset checks to `voices`, `demo`, `controller`, or runtime factory in this pass.

## Test Strategy

- Do not require real SAPI voices, COM, Piper binaries, or Piper models.
- Unit-test provider helpers with fake injected data:
  - Fake SAPI lister returns `("Microsoft Zira Desktop", "Microsoft Huihui Desktop")`.
  - Missing SAPI lister raises `ImportError`/`RuntimeError`; diagnostics should report a clear local asset failure or warning without importing COM in tests.
  - Piper tests create temporary `en_US-lessac-medium.onnx` and `en_US-lessac-medium.onnx.json` files under `tmp_path`.
- Add diagnostics tests by monkeypatching injected helpers in `tests/unit/test_diagnostics.py`:
  - `doctor` voice check for `ringcentral-video-bind-speaker` + `zh-CN` reports `voice assets` OK when fake Huihui exists.
  - Same route reports missing `Huihui` when fake voices omit it.
  - `ringcentral-video-piper-speaker` + English checks Piper model/config paths via `tmp_path`.
  - `ringcentral-video-piper-speaker` + Chinese checks SAPI Huihui, not Piper, because the resolved route is `windows-sapi-zh`.
  - `ringcentral-video` fake profile with no voice remains unchanged; fake profile with unsupported Chinese still fails only compatibility.
- CLI tests should only assert formatted doctor output and exit code. Keep provider-specific probe behavior tested below CLI level.

## Edge Cases and Platform Considerations

- On non-Windows hosts, SAPI diagnostics should not crash. Prefer a `FAIL` only when the user explicitly asked doctor to check a SAPI-routed voice; otherwise no check should run.
- SAPI display names vary by Windows edition/language pack. Match by substring, case-insensitive, consistent with `_select_voice()`.
- COM enumeration can fail even when `win32com` imports; catch broad runtime exceptions and turn them into diagnostic detail.
- Piper may auto-download when synthesizing, but this feature is about local availability. Do not run `python -m piper`, synthesize audio, or hit the network in doctor.
- The current profile schema has no explicit Piper voice/model path or SAPI voice override. Keep checks aligned with today's hard-coded defaults unless a later cycle adds profile-level voice asset config.
- Avoid making default `doctor --profile ringcentral-video-piper-speaker` fail on machines without Piper models. Gate local asset checks behind `--language/--tone` voice preflight.

## Proposed File List

- `src/ai_presenter/providers/windows_speech.py`
- `src/ai_presenter/providers/piper_provider.py`
- `src/ai_presenter/runtime/diagnostics.py`
- `tests/unit/test_windows_speech_provider.py`
- `tests/unit/test_piper_provider.py`
- `tests/unit/test_diagnostics.py`
- `tests/unit/test_cli.py`
