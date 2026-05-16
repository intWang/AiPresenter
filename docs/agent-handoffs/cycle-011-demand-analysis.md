# Cycle 011 Demand Analysis: CLI Voice Flags

Date: 2026-05-16

## User-Facing Need

Operators can choose presenter language and tone in the Tk controller, but scripted demos and controller launch commands still default to English / Professional. Exposing the same voice selection through CLI commands makes Chinese and tone-specific acceptance runs repeatable.

## Expected Workflows

```powershell
.\.venv\Scripts\ai-presenter demo --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo --language zh-CN --tone friendly
```

```powershell
.\.venv\Scripts\ai-presenter controller --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo --language English --tone coach
```

## Acceptance Criteria

- `demo` and `controller` expose optional `--language` and `--tone` flags.
- Values normalize through `PresenterVoiceSettings`, preserving aliases such as `zh-CN`, `English`, `warm`, `mentor`, and `structured`.
- Invalid values fail before automation or UI launch.
- Dry-run output includes the normalized label.
- Non-dry runtime calls receive canonical `PresenterVoiceSettings`.
- Controller menus initialize from the CLI-selected voice and remain editable by the operator.

## Risks

- CLI voice selection does not guarantee local TTS availability. Runtime provider validation remains authoritative.
- Adding flags to `run` would overpromise because that path does not yet consume material-demo voice settings.
- Tk selector initialization must map canonical values back to shared labels or the first Start click will reset voice to defaults.

## Documentation Suggestions

- Update README command examples for `demo` and `controller`.
- Update RingCentral manual acceptance runbook with a CLI-launched Chinese/friendly or coach-tone check.
- Note that regional aliases normalize to English/Chinese output families; they do not add new languages.
