import json
import subprocess
import sys
from pathlib import Path

import pytest
from typer.testing import CliRunner

from ai_presenter.cli import app
from ai_presenter.cli import REPO_PACKAGE_DIR
from ai_presenter.cli import PACKAGE_PROFILE_DIR
from ai_presenter.cli import REPO_PROFILE_DIR
from ai_presenter.cli import resolve_material_package
from ai_presenter.cli import resolve_profile
from ai_presenter.runtime import diagnostics
from ai_presenter.runtime.voice import PresenterVoiceSettings
from ai_presenter.runtime.voice_assets import VoiceAssetAvailability


def test_cli_help_renders() -> None:
    result = CliRunner().invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "AI presenter" in result.stdout


def test_cli_import_does_not_load_desktop_runtime_modules() -> None:
    code = (
        "import json, sys; "
        "import ai_presenter.cli; "
        "names = ["
        "'ai_presenter.desktop.windows', "
        "'ai_presenter.runtime.factory', "
        "'ai_presenter.runtime.controller', "
        "'ai_presenter.runtime.diagnostics', "
        "'ai_presenter.runtime.voice_assets', "
        "'ai_presenter.providers.base', "
        "'ai_presenter.providers.piper_provider', "
        "'ai_presenter.providers.windows_speech'"
        "]; "
        "print(json.dumps({name: name in sys.modules for name in names}, sort_keys=True))"
    )

    result = subprocess.run(
        [sys.executable, "-c", code],
        check=True,
        capture_output=True,
        text=True,
    )

    assert json.loads(result.stdout) == {
        "ai_presenter.desktop.windows": False,
        "ai_presenter.runtime.controller": False,
        "ai_presenter.runtime.diagnostics": False,
        "ai_presenter.runtime.factory": False,
        "ai_presenter.runtime.voice_assets": False,
        "ai_presenter.providers.base": False,
        "ai_presenter.providers.piper_provider": False,
        "ai_presenter.providers.windows_speech": False,
    }


def test_localization_report_does_not_load_voice_asset_providers() -> None:
    code = (
        "import json, sys; "
        "from typer.testing import CliRunner; "
        "from ai_presenter.cli import app; "
        "result = CliRunner().invoke("
        "app, ["
        "'localization-report', '--package', 'ringcentral-video', "
        "'--language', 'zh', '--require-complete'"
        "]"
        "); "
        "names = ["
        "'ai_presenter.runtime.diagnostics', "
        "'ai_presenter.runtime.voice_assets', "
        "'ai_presenter.providers.base', "
        "'ai_presenter.providers.piper_provider', "
        "'ai_presenter.providers.windows_speech'"
        "]; "
        "print(json.dumps({"
        "'exit_code': result.exit_code, "
        "'output': result.output, "
        "'loaded': {name: name in sys.modules for name in names}"
        "}, sort_keys=True))"
    )

    result = subprocess.run(
        [sys.executable, "-c", code],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)

    assert payload["exit_code"] == 0, payload["output"]
    assert "Package: ringcentral-video" in payload["output"]
    assert payload["loaded"] == {
        "ai_presenter.runtime.diagnostics": False,
        "ai_presenter.runtime.voice_assets": False,
        "ai_presenter.providers.base": False,
        "ai_presenter.providers.piper_provider": False,
        "ai_presenter.providers.windows_speech": False,
    }


def test_run_dry_run_loads_profile() -> None:
    result = CliRunner().invoke(app, ["run", "--profile", "ringcentral-video", "--dry-run"])

    assert result.exit_code == 0
    assert "Loaded profile: ringcentral-video" in result.stdout
    assert "Dry run complete." in result.stdout


def test_run_dry_run_loads_profile_path() -> None:
    profile_path = Path("profiles/ringcentral-video.yaml")

    result = CliRunner().invoke(app, ["run", "--profile", str(profile_path), "--dry-run"])

    assert result.exit_code == 0
    assert "Loaded profile: ringcentral-video" in result.stdout


def test_demo_dry_run_loads_profile_package_and_flow() -> None:
    result = CliRunner().invoke(
        app,
        [
            "demo",
            "--profile",
            "ringcentral-video",
            "--package",
            "ringcentral-video",
            "--flow",
            "meeting-controls-tour",
            "--dry-run",
        ],
    )

    assert result.exit_code == 0
    assert "Loaded profile: ringcentral-video" in result.stdout
    assert "Loaded package: ringcentral-video" in result.stdout
    assert "Loaded flow: meeting-controls-tour" in result.stdout


def test_demo_passes_language_and_tone_to_runtime(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[PresenterVoiceSettings] = []

    def fake_run_material_demo(*_args: object, voice: PresenterVoiceSettings | None = None) -> None:
        assert voice is not None
        calls.append(voice)

    monkeypatch.setattr("ai_presenter.cli.run_material_demo", fake_run_material_demo)

    result = CliRunner().invoke(
        app,
        [
            "demo",
            "--profile",
            "ringcentral-video-bind-speaker",
            "--package",
            "ringcentral-video",
            "--flow",
            "meeting-control-map-demo",
            "--language",
            "zh-CN",
            "--tone",
            "friendly",
        ],
    )

    assert result.exit_code == 0
    assert "Loaded voice: Chinese / Friendly" in result.stdout
    assert calls == [PresenterVoiceSettings(language="zh", tone="friendly")]


def test_demo_dry_run_reports_normalized_voice_aliases() -> None:
    result = CliRunner().invoke(
        app,
        [
            "demo",
            "--profile",
            "ringcentral-video",
            "--package",
            "ringcentral-video",
            "--flow",
            "meeting-controls-tour",
            "--language",
            "English",
            "--tone",
            "warm",
            "--dry-run",
        ],
    )

    assert result.exit_code == 0
    assert "Loaded voice: English / Friendly" in result.stdout


def test_demo_rejects_unsupported_profile_voice_before_runtime(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    called = False

    def fake_run_material_demo(*_args: object, **_kwargs: object) -> None:
        nonlocal called
        called = True

    monkeypatch.setattr("ai_presenter.cli.run_material_demo", fake_run_material_demo)
    result = CliRunner().invoke(
        app,
        [
            "demo",
            "--profile",
            "ringcentral-video",
            "--package",
            "ringcentral-video",
            "--flow",
            "meeting-controls-tour",
            "--language",
            "zh-CN",
            "--tone",
            "friendly",
            "--dry-run",
        ],
    )

    assert result.exit_code != 0
    assert "ringcentral-video" in result.output
    assert "speech provider fake" in result.output
    assert "Chinese / Friendly" in result.output
    assert called is False


def test_demo_reports_available_flows_when_flow_is_missing() -> None:
    result = CliRunner().invoke(
        app,
        [
            "demo",
            "--profile",
            "ringcentral-video",
            "--package",
            "ringcentral-video",
            "--flow",
            "missing-flow",
            "--dry-run",
        ],
    )

    assert result.exit_code != 0
    assert "Unknown demo flow: missing-flow" in result.output
    assert "Available flows:" in result.output
    assert "meeting-control-map-demo" in result.output


def test_controller_dry_run_loads_profile_package_and_flow() -> None:
    result = CliRunner().invoke(
        app,
        [
            "controller",
            "--profile",
            "ringcentral-video-bind-speaker",
            "--package",
            "ringcentral-video",
            "--flow",
            "meeting-control-map-demo",
            "--dry-run",
        ],
    )

    assert result.exit_code == 0
    assert "Loaded profile: ringcentral-video-bind-speaker" in result.stdout
    assert "Loaded package: ringcentral-video" in result.stdout
    assert "Loaded flow: meeting-control-map-demo" in result.stdout
    assert "Controller dry run complete." in result.stdout


def test_controller_reports_available_flows_when_flow_is_missing() -> None:
    result = CliRunner().invoke(
        app,
        [
            "controller",
            "--profile",
            "ringcentral-video-bind-speaker",
            "--package",
            "ringcentral-video",
            "--flow",
            "missing-flow",
            "--dry-run",
        ],
    )

    assert result.exit_code != 0
    assert "Unknown demo flow: missing-flow" in result.output
    assert "Available flows:" in result.output


def test_controller_passes_language_and_tone_to_runtime(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[PresenterVoiceSettings] = []

    def fake_run_controller(*_args: object, voice: PresenterVoiceSettings | None = None) -> None:
        assert voice is not None
        calls.append(voice)

    monkeypatch.setattr("ai_presenter.cli.run_controller", fake_run_controller)

    result = CliRunner().invoke(
        app,
        [
            "controller",
            "--profile",
            "ringcentral-video-bind-speaker",
            "--package",
            "ringcentral-video",
            "--flow",
            "meeting-control-map-demo",
            "--language",
            "English",
            "--tone",
            "mentor",
        ],
    )

    assert result.exit_code == 0
    assert "Loaded voice: English / Coach" in result.stdout
    assert calls == [PresenterVoiceSettings(language="en", tone="coach")]


def test_controller_rejects_unsupported_profile_voice_before_runtime(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    called = False

    def fake_run_controller(*_args: object, **_kwargs: object) -> None:
        nonlocal called
        called = True

    monkeypatch.setattr("ai_presenter.cli.run_controller", fake_run_controller)
    result = CliRunner().invoke(
        app,
        [
            "controller",
            "--profile",
            "ringcentral-video",
            "--package",
            "ringcentral-video",
            "--flow",
            "meeting-control-map-demo",
            "--language",
            "zh-CN",
            "--tone",
            "friendly",
            "--dry-run",
        ],
    )

    assert result.exit_code != 0
    assert "speech provider fake" in result.output
    assert "Chinese / Friendly" in result.output
    assert called is False


def test_demo_rejects_unknown_language_before_runtime(monkeypatch: pytest.MonkeyPatch) -> None:
    called = False

    def fake_run_material_demo(*_args: object, **_kwargs: object) -> None:
        nonlocal called
        called = True

    monkeypatch.setattr("ai_presenter.cli.run_material_demo", fake_run_material_demo)
    result = CliRunner().invoke(
        app,
        [
            "demo",
            "--profile",
            "ringcentral-video",
            "--package",
            "ringcentral-video",
            "--flow",
            "meeting-controls-tour",
            "--language",
            "es",
            "--dry-run",
        ],
    )

    assert result.exit_code != 0
    assert "Unsupported presenter language: es" in result.output
    assert called is False


def test_controller_rejects_unknown_tone_before_runtime(monkeypatch: pytest.MonkeyPatch) -> None:
    called = False

    def fake_run_controller(*_args: object, **_kwargs: object) -> None:
        nonlocal called
        called = True

    monkeypatch.setattr("ai_presenter.cli.run_controller", fake_run_controller)
    result = CliRunner().invoke(
        app,
        [
            "controller",
            "--profile",
            "ringcentral-video-bind-speaker",
            "--package",
            "ringcentral-video",
            "--flow",
            "meeting-control-map-demo",
            "--tone",
            "shouty",
            "--dry-run",
        ],
    )

    assert result.exit_code != 0
    assert "Unsupported presenter tone: shouty" in result.output
    assert called is False


def test_flows_lists_material_package_demo_flows() -> None:
    result = CliRunner().invoke(app, ["flows", "--package", "ringcentral-video"])

    assert result.exit_code == 0
    assert "Package: ringcentral-video" in result.stdout
    assert "- meeting-control-map-demo: Meeting Control Map" in result.stdout
    assert "steps" in result.stdout


def test_localization_report_outputs_ringcentral_chinese_coverage() -> None:
    result = CliRunner().invoke(
        app,
        ["localization-report", "--package", "ringcentral-video"],
    )

    assert result.exit_code == 0
    assert "Package: ringcentral-video" in result.stdout
    assert "Language: zh" in result.stdout
    assert "- meeting-controls-tour: 22/22 narration localized" in result.stdout
    assert "- localized questions: 12/12" in result.stdout
    assert "- localized answers: 12/12" in result.stdout
    assert "questionAliases.zh present on 15/27 entrypoints (49 aliases)" in result.stdout
    assert "Localization report: 51/51 demo steps" in result.stdout
    assert "Loaded profile" not in result.stdout


def test_localization_report_outputs_japanese_demo_and_qa_coverage() -> None:
    result = CliRunner().invoke(
        app,
        ["localization-report", "--package", "ringcentral-video", "--language", "ja"],
    )

    assert result.exit_code == 0
    assert "Language: ja" in result.stdout
    assert "Localization report: 51/51 demo steps" in result.stdout
    assert "- vbg-blur-demo: 4/4 narration localized" in result.stdout
    assert "- meeting-basics-demo: 3/3 narration localized" in result.stdout
    assert "- meeting-controls-tour: 22/22 narration localized" in result.stdout
    assert "- meeting-control-map-demo: 22/22 narration localized" in result.stdout
    assert "missing:" not in result.stdout
    assert "missing: explain-leave" not in result.stdout
    assert "- localized questions: 12/12" in result.stdout
    assert "- localized answers: 12/12" in result.stdout
    assert "questionAliases.ja present on 13/27 entrypoints (34 aliases)" in result.stdout


def test_localization_report_require_complete_passes_for_chinese() -> None:
    result = CliRunner().invoke(
        app,
        [
            "localization-report",
            "--package",
            "ringcentral-video",
            "--language",
            "zh",
            "--require-complete",
        ],
    )

    assert result.exit_code == 0
    assert "Localization report: 51/51 demo steps" in result.stdout
    assert "Localization coverage incomplete" not in result.stdout


def test_localization_report_require_complete_passes_for_japanese() -> None:
    result = CliRunner().invoke(
        app,
        [
            "localization-report",
            "--package",
            "ringcentral-video",
            "--language",
            "ja",
            "--require-complete",
        ],
    )

    assert result.exit_code == 0
    assert "Language: ja" in result.stdout
    assert "Localization report: 51/51 demo steps" in result.stdout
    assert "- vbg-blur-demo: 4/4 narration localized" in result.stdout
    assert "- meeting-basics-demo: 3/3 narration localized" in result.stdout
    assert "- meeting-controls-tour: 22/22 narration localized" in result.stdout
    assert "- meeting-control-map-demo: 22/22 narration localized" in result.stdout
    assert "missing:" not in result.stdout
    assert "missing: explain-leave" not in result.stdout
    assert "- localized questions: 12/12" in result.stdout
    assert "- localized answers: 12/12" in result.stdout
    assert "Localization coverage incomplete for ja." not in result.stdout


def test_entrypoints_lists_material_package_entrypoints_by_area() -> None:
    result = CliRunner().invoke(
        app,
        ["entrypoints", "--package", "ringcentral-video", "--area", "Meeting toolbar"],
    )

    assert result.exit_code == 0
    assert "Package: ringcentral-video" in result.stdout
    assert "ringcentral.video.toolbar.audio" in result.stdout
    assert "ringcentral.video.toolbar.leave" in result.stdout
    assert "ringcentral.video.top.meeting-info" not in result.stdout


def test_acceptance_draft_outputs_entrypoint_template() -> None:
    result = CliRunner().invoke(
        app,
        [
            "acceptance-draft",
            "--package",
            "ringcentral-video",
            "--entrypoint",
            "ringcentral.video.toolbar.chat",
        ],
    )

    assert result.exit_code == 0
    assert "Draft only" in result.stdout
    assert "Package: `ringcentral-video`" in result.stdout
    assert "ringcentral.video.toolbar.chat" in result.stdout
    assert "- Privacy notes:" in result.stdout
    assert "- Locator updates needed:" in result.stdout
    assert "Loaded profile" not in result.stdout


def test_acceptance_draft_outputs_flow_template() -> None:
    result = CliRunner().invoke(
        app,
        [
            "acceptance-draft",
            "--package",
            "ringcentral-video",
            "--flow",
            "meeting-control-map-demo",
        ],
    )

    assert result.exit_code == 0
    assert "meeting-control-map-demo" in result.stdout
    assert "Meeting Control Map" in result.stdout
    assert "ringcentral.video.main.add-coworkers" in result.stdout


def test_acceptance_draft_rejects_no_open_step_entrypoint() -> None:
    result = CliRunner().invoke(
        app,
        [
            "acceptance-draft",
            "--package",
            "ringcentral-video",
            "--entrypoint",
            "ringcentral.video.more.recording",
        ],
    )

    assert result.exit_code != 0
    output = " ".join(result.output.split())
    assert "ringcentral.video.more.recording" in output
    assert "has no" in output
    assert "executable" in output
    assert "open steps" in output
    assert "confirmation" in output
    assert "workflow" in output
    assert "Manual RingCentral Acceptance Draft" not in output
    assert "### Manual Acceptance Fields" not in output


def test_acceptance_draft_refusal_does_not_write_output_file(tmp_path: Path) -> None:
    output_path = tmp_path / "blocked-draft.md"

    result = CliRunner().invoke(
        app,
        [
            "acceptance-draft",
            "--package",
            "ringcentral-video",
            "--entrypoint",
            "ringcentral.video.toolbar.leave",
            "--output",
            str(output_path),
        ],
    )

    assert result.exit_code != 0
    output = " ".join(result.output.split())
    assert "ringcentral.video.toolbar.leave" in output
    assert "has no" in output
    assert "executable" in output
    assert "open steps" in output
    assert "confirmation" in output
    assert "workflow" in output
    assert not output_path.exists()


def test_acceptance_draft_requires_target() -> None:
    result = CliRunner().invoke(app, ["acceptance-draft", "--package", "ringcentral-video"])

    assert result.exit_code != 0
    assert "Provide at least one target" in result.output


def test_acceptance_draft_rejects_missing_flow_with_available_flows() -> None:
    result = CliRunner().invoke(
        app,
        ["acceptance-draft", "--package", "ringcentral-video", "--flow", "missing-flow"],
    )

    assert result.exit_code != 0
    assert "Unknown demo flow: missing-flow" in result.output
    assert "Available flows:" in result.output


def test_acceptance_draft_can_write_to_output_file(tmp_path: Path) -> None:
    output_path = tmp_path / "acceptance-draft.md"

    result = CliRunner().invoke(
        app,
        [
            "acceptance-draft",
            "--package",
            "ringcentral-video",
            "--entrypoint",
            "ringcentral.video.main.add-coworkers",
            "--output",
            str(output_path),
        ],
    )

    assert result.exit_code == 0
    assert f"Wrote acceptance draft: {output_path}" in result.stdout
    text = output_path.read_text(encoding="utf-8")
    assert "ringcentral.video.main.add-coworkers" in text
    assert "Draft only" in text


def test_acceptance_draft_rejects_existing_output_file(tmp_path: Path) -> None:
    output_path = tmp_path / "acceptance-draft.md"
    output_path.write_text("existing draft", encoding="utf-8")

    result = CliRunner().invoke(
        app,
        [
            "acceptance-draft",
            "--package",
            "ringcentral-video",
            "--entrypoint",
            "ringcentral.video.main.add-coworkers",
            "--output",
            str(output_path),
        ],
    )

    assert result.exit_code != 0
    assert "Output file already exists" in result.output
    assert output_path.read_text(encoding="utf-8") == "existing draft"


def test_acceptance_draft_rejects_acceptance_runs_output_file(tmp_path: Path) -> None:
    output_path = tmp_path / "acceptance-runs.md"

    result = CliRunner().invoke(
        app,
        [
            "acceptance-draft",
            "--package",
            "ringcentral-video",
            "--entrypoint",
            "ringcentral.video.main.add-coworkers",
            "--output",
            str(output_path),
        ],
    )

    assert result.exit_code != 0
    assert "Refusing to write acceptance draft to acceptance-runs.md" in result.output
    assert not output_path.exists()


def test_validation_targets_lists_ringcentral_targets() -> None:
    result = CliRunner().invoke(
        app,
        ["validation-targets", "--package", "ringcentral-video", "--priority", "P0"],
    )

    assert result.exit_code == 0
    assert "Package: ringcentral-video" in result.stdout
    assert "validation-checklist-index.md" in result.stdout
    assert "rcv-add-coworkers-modal" in result.stdout
    assert "rcv-controller-chat-question" in result.stdout
    assert "Loaded profile" not in result.stdout


def test_validation_targets_detail_outputs_draft_command() -> None:
    result = CliRunner().invoke(
        app,
        [
            "validation-targets",
            "--package",
            "ringcentral-video",
            "--target",
            "rcv-add-coworkers-modal",
        ],
    )

    assert result.exit_code == 0
    assert "ringcentral.video.main.add-coworkers" in result.stdout
    assert "Modal close" in result.stdout
    assert "invite links" in result.stdout
    assert (
        "ai-presenter acceptance-draft --package ringcentral-video "
        "--entrypoint ringcentral.video.main.add-coworkers"
    ) in result.stdout


def test_validation_targets_mixed_target_outputs_flow_and_entrypoint_draft_command() -> None:
    result = CliRunner().invoke(
        app,
        [
            "validation-targets",
            "--package",
            "ringcentral-video",
            "--target",
            "rcv-controller-chat-question",
        ],
    )

    assert result.exit_code == 0
    assert "flows: meeting-control-map-demo" in result.stdout
    assert "entrypoints: ringcentral.video.toolbar.chat" in result.stdout
    assert (
        "ai-presenter acceptance-draft --package ringcentral-video "
        "--flow meeting-control-map-demo "
        "--entrypoint ringcentral.video.toolbar.chat "
        '--checklist-target "P0 Controller queued Chat question"'
    ) in result.stdout


def test_validation_targets_rejects_unknown_target_with_available_ids() -> None:
    result = CliRunner().invoke(
        app,
        [
            "validation-targets",
            "--package",
            "ringcentral-video",
            "--target",
            "missing-target",
        ],
    )

    assert result.exit_code != 0
    assert "Unknown validation target: missing-target" in result.output
    assert "rcv-add-coworkers-modal" in result.output


def test_validation_targets_rejects_unknown_checklist_reference(tmp_path: Path) -> None:
    checklist_path = tmp_path / "validation-checklist-index.md"
    checklist_path.write_text(
        "\n".join(
            [
                "# Validation Checklist",
                "",
                "## Priority Checklist",
                "",
                "| Priority | Route Or Group | Entrypoints | Current State | Validate | Cleanup | Privacy Boundary | Record Result |",
                "| --- | --- | --- | --- | --- | --- | --- | --- |",
                "| P0 | Missing route | `ringcentral.video.missing` | Missing | Validate | Cleanup | Privacy | `acceptance-runs.md` |",
            ]
        ),
        encoding="utf-8",
    )

    result = CliRunner().invoke(
        app,
        [
            "validation-targets",
            "--package",
            "ringcentral-video",
            "--checklist",
            str(checklist_path),
        ],
    )

    assert result.exit_code != 0
    assert "ringcentral.video.missing" in result.output


def test_validation_targets_include_blocked_lists_do_not_execute_routes() -> None:
    result = CliRunner().invoke(
        app,
        ["validation-targets", "--package", "ringcentral-video", "--include-blocked"],
    )

    assert result.exit_code == 0
    assert "rcv-recording" in result.stdout
    assert "rcv-leave-end-meeting" in result.stdout
    assert "ringcentral.video.more.recording" in result.stdout
    assert "ringcentral.video.toolbar.leave" in result.stdout
    assert "Do not execute" in result.stdout


def test_validation_targets_blocked_target_omits_draft_command() -> None:
    result = CliRunner().invoke(
        app,
        [
            "validation-targets",
            "--package",
            "ringcentral-video",
            "--include-blocked",
            "--target",
            "rcv-recording",
        ],
    )

    assert result.exit_code == 0
    assert "rcv-recording" in result.stdout
    assert "blocked:" in result.stdout
    assert "Do not execute" in result.stdout
    assert "draft:" not in result.stdout
    assert "acceptance-draft" not in result.stdout


def test_voices_lists_language_tone_choices() -> None:
    result = CliRunner().invoke(app, ["voices"])

    assert result.exit_code == 0
    assert "Languages:" in result.stdout
    assert "English aliases:" in result.stdout
    assert "Chinese aliases:" in result.stdout
    assert "Japanese aliases:" in result.stdout
    assert "Tones:" in result.stdout
    assert "Coach aliases:" in result.stdout
    assert "Support aliases:" in result.stdout
    assert "calm" in result.stdout
    assert "recovery-focused" in result.stdout


def test_voices_catalog_output_is_ascii_safe_for_legacy_windows_console() -> None:
    result = CliRunner().invoke(app, ["voices"])

    assert result.exit_code == 0
    assert result.stdout.isascii()


def test_voices_profile_reports_supported_and_unsupported_languages() -> None:
    result = CliRunner().invoke(app, ["voices", "--profile", "ringcentral-video"])

    assert result.exit_code == 0
    assert "Profile: ringcentral-video" in result.stdout
    assert "Configured speech provider: fake" in result.stdout
    assert "English / Professional: supported via fake" in result.stdout
    assert "Chinese / Professional: unsupported" in result.stdout
    assert "Japanese / Professional: unsupported" in result.stdout


def test_voices_profile_reports_local_asset_status(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "ai_presenter.cli.check_voice_asset_availability",
        lambda *_args, **_kwargs: VoiceAssetAvailability(
            status="OK",
            route="windows-sapi-zh",
            detail="speech=windows-sapi-zh found installed SAPI voice matching Huihui",
        ),
    )

    result = CliRunner().invoke(app, ["voices", "--profile", "ringcentral-video-bind-speaker"])

    assert result.exit_code == 0
    assert "assets OK" in result.stdout
    assert "Huihui" in result.stdout


def test_voices_targeted_incompatible_profile_voice_exits_nonzero() -> None:
    result = CliRunner().invoke(
        app,
        ["voices", "--profile", "ringcentral-video", "--language", "zh-CN", "--tone", "friendly"],
    )

    assert result.exit_code == 1
    assert "Selected voice: Chinese / Friendly" in result.stdout
    assert "speech provider fake" in result.stdout


def test_voices_targeted_missing_assets_exits_nonzero(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "ai_presenter.cli.check_voice_asset_availability",
        lambda *_args, **_kwargs: VoiceAssetAvailability(
            status="FAIL",
            route="windows-sapi-zh",
            detail="speech=windows-sapi-zh requires installed SAPI voice matching Huihui",
        ),
    )

    result = CliRunner().invoke(
        app,
        ["voices", "--profile", "ringcentral-video-bind-speaker", "--language", "zh-CN"],
    )

    assert result.exit_code == 1
    assert "Selected voice assets unavailable" in result.stdout
    assert "Huihui" in result.stdout


def test_doctor_loads_profile_package_and_flow(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(diagnostics, "_iter_process_executable_paths", lambda process_name: [])

    result = CliRunner().invoke(
        app,
        [
            "doctor",
            "--profile",
            "ringcentral-video-bind-speaker",
            "--package",
            "ringcentral-video",
            "--flow",
            "meeting-control-map-demo",
        ],
    )

    assert result.exit_code == 0
    assert "[OK] profile: loaded ringcentral-video-bind-speaker" in result.stdout
    assert "[OK] package: loaded ringcentral-video" in result.stdout
    assert "[OK] package profile support" in result.stdout
    assert "[OK] question aliases:" in result.stdout
    assert "87 package-owned aliases have no cross-entrypoint duplicates" in result.stdout
    assert "[OK] qa questions:" in result.stdout
    assert "71 Q&A question prompts have no cross-item duplicates" in result.stdout
    assert "[OK] qa alias overlap:" in result.stdout
    assert "71 Q&A question prompts have no unsafe package-owned alias overlaps" in result.stdout
    assert "[INFO] qa alias substring risk:" in result.stdout
    assert (
        "11 Q&A question prompts contain package-owned alias substrings outside "
        "related entrypoints"
    ) in result.stdout
    assert "[OK] explainer coverage" in result.stdout
    assert "[OK] demo flow: meeting-control-map-demo" in result.stdout
    assert "[OK] presenter context" in result.stdout
    assert "[WARN] RingCentral config" in result.stdout
    assert "localization:" not in result.stdout
    assert "Doctor completed:" in result.stdout


def test_doctor_warns_for_duplicate_question_aliases(tmp_path: Path) -> None:
    config_path = tmp_path / "config.ini"
    config_path.write_text("[General]\nDisableAffinityMask=true\n", encoding="utf-8")
    package_path = tmp_path / "duplicate-alias-package.yaml"
    package_path.write_text(
        """
appId: demo
appName: Demo
version: 1
profileIds: [ringcentral-video-bind-speaker]
operationEntrypoints:
  - id: demo.alpha
    title: Alpha
    area: Main
    purpose: Open alpha.
    questionAliases:
      en:
        - " Chat "
    openSteps: []
  - id: demo.bravo
    title: Bravo
    area: Main
    purpose: Open bravo.
    questionAliases:
      en:
        - chat
    openSteps: []
demoFlows: []
explainers:
  alpha:
    shortScript: Alpha.
    relatedEntrypointIds: [demo.alpha]
  bravo:
    shortScript: Bravo.
    relatedEntrypointIds: [demo.bravo]
manualControls: []
""",
        encoding="utf-8",
    )

    result = CliRunner().invoke(
        app,
        [
            "doctor",
            "--profile",
            "ringcentral-video-bind-speaker",
            "--package",
            str(package_path),
            "--ringcentral-config",
            str(config_path),
        ],
    )

    assert result.exit_code == 0
    assert "[WARN] question aliases:" in result.stdout
    assert "'chat' (languages: en) maps to demo.alpha, demo.bravo" in result.stdout
    assert "first match is demo.alpha" in result.stdout
    assert "1 warning, 0 failed" in result.stdout


def test_doctor_warns_for_duplicate_qa_questions(tmp_path: Path) -> None:
    config_path = tmp_path / "config.ini"
    config_path.write_text("[General]\nDisableAffinityMask=true\n", encoding="utf-8")
    package_path = tmp_path / "duplicate-qa-package.yaml"
    package_path.write_text(
        """
appId: demo
appName: Demo
version: 1
profileIds: [ringcentral-video-bind-speaker]
operationEntrypoints: []
demoFlows: []
qa:
  - question: Where is privacy?
    answer: First answer.
  - question: where is privacy?
    answer: Second answer.
manualControls: []
""",
        encoding="utf-8",
    )

    result = CliRunner().invoke(
        app,
        [
            "doctor",
            "--profile",
            "ringcentral-video-bind-speaker",
            "--package",
            str(package_path),
            "--ringcentral-config",
            str(config_path),
        ],
    )

    assert result.exit_code == 0
    assert "[WARN] qa questions:" in result.stdout
    assert "'where is privacy?' (languages: en)" in result.stdout
    assert "first match is #1 Where is privacy?" in result.stdout
    assert "1 warning, 0 failed" in result.stdout


def test_doctor_warns_when_qa_question_shadows_entrypoint_alias(tmp_path: Path) -> None:
    config_path = tmp_path / "config.ini"
    config_path.write_text("[General]\nDisableAffinityMask=true\n", encoding="utf-8")
    package_path = tmp_path / "qa-alias-overlap-package.yaml"
    package_path.write_text(
        """
appId: demo
appName: Demo
version: 1
profileIds: [ringcentral-video-bind-speaker]
operationEntrypoints:
  - id: demo.chat
    title: Chat
    area: Main
    purpose: Open chat.
    questionAliases:
      en:
        - chat
    openSteps: []
demoFlows: []
explainers:
  chat:
    shortScript: Chat.
    relatedEntrypointIds: [demo.chat]
qa:
  - question: chat
    answer: Explain chat without opening it.
manualControls: []
""",
        encoding="utf-8",
    )

    result = CliRunner().invoke(
        app,
        [
            "doctor",
            "--profile",
            "ringcentral-video-bind-speaker",
            "--package",
            str(package_path),
            "--ringcentral-config",
            str(config_path),
        ],
    )

    assert result.exit_code == 0
    assert "[WARN] qa alias overlap:" in result.stdout
    assert "'chat' (Q&A languages: en; alias languages: en)" in result.stdout
    assert "shadows demo.chat" in result.stdout
    assert "first match is Q&A #1 chat" in result.stdout
    assert "1 warning, 0 failed" in result.stdout


def test_doctor_reports_qa_alias_substring_risk_as_info(tmp_path: Path) -> None:
    config_path = tmp_path / "config.ini"
    config_path.write_text("[General]\nDisableAffinityMask=true\n", encoding="utf-8")
    package_path = tmp_path / "qa-alias-substring-package.yaml"
    package_path.write_text(
        """
appId: demo
appName: Demo
version: 1
profileIds: [ringcentral-video-bind-speaker]
operationEntrypoints:
  - id: demo.chat
    title: Chat
    area: Main
    purpose: Open chat.
    questionAliases:
      en:
        - chat
    openSteps: []
demoFlows: []
explainers:
  chat:
    shortScript: Chat.
    relatedEntrypointIds: [demo.chat]
qa:
  - question: Can you read chat messages?
    answer: Explain chat privacy without opening it.
manualControls: []
""",
        encoding="utf-8",
    )

    result = CliRunner().invoke(
        app,
        [
            "doctor",
            "--profile",
            "ringcentral-video-bind-speaker",
            "--package",
            str(package_path),
            "--ringcentral-config",
            str(config_path),
        ],
    )

    assert result.exit_code == 0
    assert "[INFO] qa alias substring risk:" in result.stdout
    assert "'can you read chat messages?'" in result.stdout
    assert "contains aliases for demo.chat" in result.stdout
    assert "1 info, 0 warnings, 0 failed" in result.stdout


def test_doctor_accepts_language_and_tone_voice_preflight(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(diagnostics, "_iter_process_executable_paths", lambda process_name: [])
    monkeypatch.setattr(
        diagnostics,
        "check_voice_asset_availability",
        lambda *_args, **_kwargs: VoiceAssetAvailability(
            status="OK",
            route="windows-sapi-zh",
            detail="speech=windows-sapi-zh found installed SAPI voice matching Huihui",
        ),
    )

    result = CliRunner().invoke(
        app,
        [
            "doctor",
            "--profile",
            "ringcentral-video-bind-speaker",
            "--language",
            "zh-CN",
            "--tone",
            "friendly",
        ],
    )

    assert result.exit_code == 0
    assert "[OK] voice: Chinese / Friendly supported via speech=windows-sapi-zh" in result.stdout
    assert "[OK] voice assets:" in result.stdout


def test_doctor_require_localization_fails_without_package(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(diagnostics, "_iter_process_executable_paths", lambda process_name: [])

    result = CliRunner().invoke(
        app,
        [
            "doctor",
            "--profile",
            "ringcentral-video-bind-speaker",
            "--require-localization",
        ],
    )

    assert result.exit_code == 1
    assert (
        "[FAIL] localization: --require-localization requires --package"
        in result.stdout
    )


def test_doctor_require_localization_passes_for_chinese_package(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(diagnostics, "_iter_process_executable_paths", lambda process_name: [])
    monkeypatch.setattr(
        diagnostics,
        "check_voice_asset_availability",
        lambda *_args, **_kwargs: VoiceAssetAvailability(
            status="OK",
            route="windows-sapi-zh",
            detail="speech=windows-sapi-zh found installed SAPI voice matching Huihui",
        ),
    )

    result = CliRunner().invoke(
        app,
        [
            "doctor",
            "--profile",
            "ringcentral-video-bind-speaker",
            "--package",
            "ringcentral-video",
            "--language",
            "zh-CN",
            "--tone",
            "friendly",
            "--require-localization",
        ],
    )

    assert result.exit_code == 0
    assert "[OK] localization: required zh localization complete" in result.stdout


def test_doctor_require_localization_defaults_to_chinese_when_no_voice_selected(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(diagnostics, "_iter_process_executable_paths", lambda process_name: [])

    result = CliRunner().invoke(
        app,
        [
            "doctor",
            "--profile",
            "ringcentral-video-bind-speaker",
            "--package",
            "ringcentral-video",
            "--require-localization",
        ],
    )

    assert result.exit_code == 0
    assert "[OK] localization: required zh localization complete" in result.stdout


def test_doctor_rejects_unsupported_profile_voice(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(diagnostics, "_iter_process_executable_paths", lambda process_name: [])

    result = CliRunner().invoke(
        app,
        ["doctor", "--profile", "ringcentral-video", "--language", "zh-CN"],
    )

    assert result.exit_code == 1
    assert "[FAIL] voice:" in result.stdout
    assert "speech provider fake" in result.stdout


def test_doctor_rejects_package_that_does_not_support_profile(tmp_path: Path) -> None:
    package_path = tmp_path / "demo-package.yaml"
    package_path.write_text(
        """
appId: demo
appName: Demo
version: 1
profileIds: [other-profile]
operationEntrypoints:
  - id: demo.overview
    title: Overview
    area: Main
    purpose: Explain the surface
    openSteps: []
demoFlows: []
manualControls: []
""",
        encoding="utf-8",
    )

    result = CliRunner().invoke(
        app,
        ["doctor", "--profile", "ringcentral-video-bind-speaker", "--package", str(package_path)],
    )

    assert result.exit_code == 1
    assert "[FAIL] package profile support" in result.stdout
    assert "does not list profile ringcentral-video-bind-speaker" in result.stdout


def test_doctor_accepts_ringcentral_config_with_disable_affinity_mask(tmp_path: Path) -> None:
    config_path = tmp_path / "config.ini"
    config_path.write_text("[General]\nDisableAffinityMask=true\n", encoding="utf-8")

    result = CliRunner().invoke(
        app,
        [
            "doctor",
            "--profile",
            "ringcentral-video-bind-speaker",
            "--ringcentral-config",
            str(config_path),
        ],
    )

    assert result.exit_code == 0
    assert "[OK] RingCentral config" in result.stdout
    assert "DisableAffinityMask=true" in result.stdout


def test_doctor_rejects_ringcentral_config_without_disable_affinity_mask(tmp_path: Path) -> None:
    config_path = tmp_path / "config.ini"
    config_path.write_text("DisableAffinityMask=false\n", encoding="utf-8")

    result = CliRunner().invoke(
        app,
        [
            "doctor",
            "--profile",
            "ringcentral-video-bind-speaker",
            "--ringcentral-config",
            str(config_path),
        ],
    )

    assert result.exit_code == 1
    assert "[FAIL] RingCentral config" in result.stdout
    assert "expected DisableAffinityMask=true" in result.stdout


def test_doctor_rejects_openai_profile_without_required_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("AI_PRESENTER_OPENAI_NARRATION_MODEL", raising=False)
    monkeypatch.setattr(diagnostics, "_iter_process_executable_paths", lambda process_name: [])

    result = CliRunner().invoke(
        app,
        ["doctor", "--profile", "profiles/ringcentral-video-openai.example.yaml"],
    )

    assert result.exit_code == 1
    assert "[FAIL] provider environment" in result.stdout
    assert "OPENAI_API_KEY" in result.stdout
    assert "AI_PRESENTER_OPENAI_NARRATION_MODEL" in result.stdout


def test_resolve_profile_id_from_non_repo_working_directory(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    resolved = resolve_profile("ringcentral-video")

    assert resolved == REPO_PROFILE_DIR / "ringcentral-video.yaml"


def test_resolve_material_package_id_from_non_repo_working_directory(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    resolved = resolve_material_package("ringcentral-video")

    assert resolved == REPO_PACKAGE_DIR / "ringcentral-video.yaml"


def test_packaged_profile_copy_matches_repo_profile() -> None:
    assert (PACKAGE_PROFILE_DIR / "ringcentral-video.yaml").read_text(encoding="utf-8") == (
        REPO_PROFILE_DIR / "ringcentral-video.yaml"
    ).read_text(encoding="utf-8")


def test_cli_run_requires_profile() -> None:
    result = CliRunner().invoke(app, ["run"])

    assert result.exit_code != 0
    assert "--profile" in result.output


def test_run_rejects_missing_profile() -> None:
    result = CliRunner().invoke(app, ["run", "--profile", "missing", "--dry-run"])

    assert result.exit_code != 0
    assert "Profile not found: missing" in result.output
