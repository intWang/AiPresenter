import json
import subprocess
import sys
from pathlib import Path

import pytest
from typer.testing import CliRunner

import ai_presenter.cli as cli
from ai_presenter.cli import app
from ai_presenter.cli import REPO_PACKAGE_DIR
from ai_presenter.cli import PACKAGE_PROFILE_DIR
from ai_presenter.cli import REPO_PROFILE_DIR
from ai_presenter.cli import resolve_material_package
from ai_presenter.cli import resolve_profile
from ai_presenter.runtime import diagnostics
from ai_presenter.runtime.voice import PRESENTER_LANGUAGE_CHOICES
from ai_presenter.runtime.voice import PresenterVoiceSettings
from ai_presenter.runtime.voice import presenter_language_aliases
from ai_presenter.runtime.voice_assets import VoiceAssetAvailability


VALIDATION_TARGETS_NON_EVIDENCE_NOTE = (
    "Note: repo-derived planning list only; not live acceptance evidence."
)
VALIDATION_TARGETS_EVIDENCE_REMINDER = (
    "Evidence reminder: P0/P1 manual evidence is metadata-first. "
    "Prefer UIA/window metadata and sanitized product-control labels; screenshots require "
    "a clear verification need and privacy review path; redact or omit private meeting "
    "content before recording results."
)
VALIDATION_TARGETS_CHECKLIST_SOURCE = (
    "Checklist: "
    + str(Path("docs/knowledge/ringcentral-video/validation-checklist-index.md"))
)
VALIDATION_TARGETS_EVIDENCE_SOURCE = (
    "Evidence: " + str(Path("docs/knowledge/ringcentral-video/evidence-index.md"))
)
VALIDATION_TARGETS_ACCEPTANCE_SOURCE = (
    "Acceptance runs: "
    + str(Path("docs/knowledge/ringcentral-video/acceptance-runs.md"))
    + " (auto-discovered)"
)


def assert_acceptance_draft_boundary(text: str) -> None:
    assert "Draft only" in text
    assert "not acceptance evidence" in text
    assert "No live RingCentral action has been performed by this helper." in text
    lowered = text.casefold()
    assert "accepted" not in lowered
    assert "passed" not in lowered
    assert "live validated" not in lowered


def assert_acceptance_draft_refusal_boundary(text: str) -> None:
    assert "Manual RingCentral Acceptance Draft" not in text
    assert "### Manual Acceptance Fields" not in text
    assert "Wrote acceptance draft" not in text
    lowered = text.casefold()
    assert "accepted" not in lowered
    assert "passed" not in lowered
    assert "live validated" not in lowered


def test_cli_help_renders() -> None:
    result = CliRunner().invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "AI presenter" in result.stdout


def test_validation_targets_help_explains_acceptance_runs_guard_source() -> None:
    result = CliRunner().invoke(app, ["validation-targets", "--help"])

    assert result.exit_code == 0
    assert "--acceptance-runs" in result.stdout
    assert "Accepted evidence guard source" in result.stdout
    assert "selected" in result.stdout
    assert "acceptance-runs source" in result.stdout
    assert "not live" in result.stdout
    assert "evidence." in result.stdout


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
    assert "Loaded flow: meeting-controls-tour (22 steps)" in result.stdout


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
    assert "Loaded flow: meeting-control-map-demo (22 steps)" in result.stdout
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
            "fr",
            "--dry-run",
        ],
    )

    assert result.exit_code != 0
    assert "Unsupported presenter language: fr" in result.output
    assert called is False


def test_demo_openai_profile_accepts_spanish_dry_run() -> None:
    result = CliRunner().invoke(
        app,
        [
            "demo",
            "--profile",
            "profiles/ringcentral-video-openai.example.yaml",
            "--package",
            "ringcentral-video",
            "--flow",
            "meeting-control-map-demo",
            "--language",
            "es",
            "--dry-run",
        ],
    )

    assert result.exit_code == 0
    assert "Loaded voice: Spanish / Professional" in result.stdout
    assert "Dry run complete." in result.stdout


def test_controller_openai_profile_accepts_spanish_dry_run() -> None:
    result = CliRunner().invoke(
        app,
        [
            "controller",
            "--profile",
            "profiles/ringcentral-video-openai.example.yaml",
            "--package",
            "ringcentral-video",
            "--flow",
            "meeting-control-map-demo",
            "--language",
            "es",
            "--dry-run",
        ],
    )

    assert result.exit_code == 0
    assert "Loaded voice: Spanish / Professional" in result.stdout
    assert "Controller dry run complete." in result.stdout


def test_demo_rejects_spanish_local_profile_before_runtime(
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
            "ringcentral-video-bind-speaker",
            "--package",
            "ringcentral-video",
            "--flow",
            "meeting-control-map-demo",
            "--language",
            "es",
            "--dry-run",
        ],
    )

    assert result.exit_code != 0
    assert "Spanish / Professional" in result.output
    assert "speech provider" in result.output
    assert "windows-sapi-en" in result.output
    assert "openai" in result.output
    assert "Unsupported presenter language" not in result.output
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
    assert "- localized questions: 16/16" in result.stdout
    assert "- localized answers: 16/16" in result.stdout
    assert "questionAliases.zh present on 15/27 entrypoints (49 aliases)" in result.stdout
    assert "localizedTitles.zh present on 0/27 entrypoints" in result.stdout
    assert "localizedPurposes.zh present on 0/27 entrypoints" in result.stdout
    assert "Localization report: 51/51 demo steps" in result.stdout
    assert "Loaded profile" not in result.stdout


def test_localization_report_explains_readiness_boundaries() -> None:
    result = CliRunner().invoke(
        app,
        ["localization-report", "--package", "ringcentral-video", "--language", "es"],
    )

    assert result.exit_code == 0
    assert "Readiness boundary:" in result.stdout
    assert "This report checks package localization text only." in result.stdout
    assert "Use --language with voices, doctor, demo, or controller" in result.stdout
    assert "Live RingCentral acceptance requires a dated acceptance run." in (
        result.stdout
    )


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
    assert "- localized questions: 16/16" in result.stdout
    assert "- localized answers: 16/16" in result.stdout
    assert "questionAliases.ja present on 13/27 entrypoints (34 aliases)" in result.stdout
    assert "localizedTitles.ja present on 0/27 entrypoints" in result.stdout
    assert "localizedPurposes.ja present on 0/27 entrypoints" in result.stdout


def test_localization_report_outputs_complete_spanish_package() -> None:
    result = CliRunner().invoke(
        app,
        ["localization-report", "--package", "ringcentral-video", "--language", "es"],
    )

    assert result.exit_code == 0
    assert "Language: es" in result.stdout
    assert "- vbg-blur-demo: 4/4 narration localized" in result.stdout
    assert "- meeting-basics-demo: 3/3 narration localized" in result.stdout
    assert "- meeting-controls-tour: 22/22 narration localized" in result.stdout
    assert "- meeting-control-map-demo: 22/22 narration localized" in result.stdout
    assert "Localization report: 51/51 demo steps" in result.stdout
    assert "- localized questions: 16/16" in result.stdout
    assert "- localized answers: 16/16" in result.stdout
    assert "questionAliases.es present on 26/27 entrypoints (69 aliases)" in result.stdout
    assert "localizedTitles.es present on 8/27 entrypoints" in result.stdout
    assert "localizedPurposes.es present on 8/27 entrypoints" in result.stdout
    assert "Localization coverage incomplete" not in result.stdout


def test_localization_report_normalizes_spanish_language_aliases() -> None:
    result = CliRunner().invoke(
        app,
        ["localization-report", "--package", "ringcentral-video", "--language", "Spanish"],
    )

    assert result.exit_code == 0
    assert "Language: es" in result.stdout
    assert "- vbg-blur-demo: 4/4 narration localized" in result.stdout
    assert "- meeting-basics-demo: 3/3 narration localized" in result.stdout
    assert "- meeting-controls-tour: 22/22 narration localized" in result.stdout
    assert "- meeting-control-map-demo: 22/22 narration localized" in result.stdout
    assert "Localization report: 51/51 demo steps" in result.stdout
    assert "- localized questions: 16/16" in result.stdout
    assert "- localized answers: 16/16" in result.stdout
    assert "questionAliases.es present on 26/27 entrypoints (69 aliases)" in result.stdout
    assert "localizedTitles.es present on 8/27 entrypoints" in result.stdout
    assert "localizedPurposes.es present on 8/27 entrypoints" in result.stdout
    assert "Localization coverage incomplete" not in result.stdout


def test_package_language_alias_normalization_is_documented() -> None:
    lifecycle_text = Path("docs/knowledge/language-lifecycle.md").read_text(
        encoding="utf-8"
    )
    normalized_lifecycle_text = " ".join(lifecycle_text.split())

    assert cli.resolve_package_language_key("Spanish") == "es"
    assert cli.resolve_package_language_key("es-MX") == "es"
    assert cli.resolve_package_language_key("es-419") == "es"
    assert cli.resolve_package_language_key("Espa\u00f1ol") == "es"
    assert cli.resolve_package_language_key("zh-CN") == "zh"
    assert cli.resolve_package_language_key("de") == "de"
    assert "raw language-key lookup" not in normalized_lifecycle_text
    assert "known presenter language aliases" in normalized_lifecycle_text
    assert "Unknown package-only keys remain raw" in normalized_lifecycle_text
    assert "resolved package key" in normalized_lifecycle_text
    assert (
        "reports `51/51` demo steps, `16/16` Q&A questions, and `16/16` Q&A answers"
        in normalized_lifecycle_text
    )


def test_language_lifecycle_matrix_matches_runtime_language_contract() -> None:
    lifecycle_text = Path("docs/knowledge/language-lifecycle.md").read_text(
        encoding="utf-8"
    )
    normalized_lifecycle_text = " ".join(lifecycle_text.split())

    for label, language in PRESENTER_LANGUAGE_CHOICES:
        aliases = ", ".join(
            f"`{alias}`" for alias in presenter_language_aliases(language)
        )
        assert f"| `{language}` | {label} |" in lifecycle_text
        assert aliases in lifecycle_text

    for phrase in (
        "## Current Language State Matrix",
        "package-localization complete",
        "runtime presenter language",
        "provider compatibility",
        "live acceptance evidence",
        "`--localization-language` checks package text",
        "`--language` selects runtime presenter voice",
        "English is the default runtime voice language",
        "Chinese can use OpenAI speech or `windows-sapi-zh`",
        "Japanese requires OpenAI speech",
        "Spanish requires OpenAI speech",
        "local SAPI/Piper Spanish remains future work",
        "local fake, Piper, and Windows SAPI profiles must reject `--language es`",
        "Package-only text is never live acceptance evidence",
        "Live acceptance requires a dated acceptance run",
        (
            "profile/provider compatibility is checked separately when `--language es` "
            "selects a Spanish runtime voice"
        ),
    ):
        assert phrase in normalized_lifecycle_text


def test_entrypoints_language_marker_contract_is_documented() -> None:
    readme_text = Path("README.md").read_text(encoding="utf-8")
    lifecycle_text = Path("docs/knowledge/language-lifecycle.md").read_text(
        encoding="utf-8"
    )
    normalized_readme_text = " ".join(readme_text.split())
    normalized_lifecycle_text = " ".join(lifecycle_text.split())

    assert (
        "entrypoints --package ringcentral-video --language es"
        in normalized_readme_text
    )
    assert "Spanish" in normalized_readme_text
    assert "es-MX" in normalized_readme_text
    assert "Language: es" in normalized_readme_text
    assert "(title: localized)" in normalized_readme_text
    assert "(title: fallback)" in normalized_readme_text
    assert "not evidence of runtime Spanish readiness" in normalized_readme_text
    assert "matcher expansion" in normalized_readme_text
    assert "provider availability" in normalized_readme_text
    assert "live RingCentral Video acceptance" in normalized_readme_text

    assert "For Spanish inputs such as `es`, `Spanish`, and `es-MX`" in lifecycle_text
    assert "Language: es" in normalized_lifecycle_text
    assert "(title: localized)" in normalized_lifecycle_text
    assert "(title: fallback)" in normalized_lifecycle_text
    assert "display-source labels only" in normalized_lifecycle_text
    assert "not evidence of runtime Spanish readiness" in normalized_lifecycle_text
    assert "matcher expansion" in normalized_lifecycle_text
    assert "provider compatibility" in normalized_lifecycle_text
    assert "live RingCentral Video acceptance" in normalized_lifecycle_text

    overclaim_patterns = (
        "`--language es` is runtime-selectable",
        "entrypoints --language es proves",
        "entrypoints --language es supports Spanish",
        "entrypoints --language es validates runtime",
    )
    for overclaim in overclaim_patterns:
        assert overclaim not in normalized_readme_text


def test_localization_report_keeps_unknown_package_language_key_raw() -> None:
    result = CliRunner().invoke(
        app,
        ["localization-report", "--package", "ringcentral-video", "--language", "de"],
    )

    assert result.exit_code == 0
    assert "Language: de" in result.stdout
    assert "Localization report: 0/51 demo steps" in result.stdout
    assert "Invalid value" not in result.output
    assert "Unsupported presenter language" not in result.output


def test_localization_report_outputs_french_package_seed() -> None:
    result = CliRunner().invoke(
        app,
        ["localization-report", "--package", "ringcentral-video", "--language", "fr"],
    )

    assert result.exit_code == 0
    assert "Language: fr" in result.stdout
    assert "- meeting-basics-demo: 3/3 narration localized" in result.stdout
    assert "- vbg-blur-demo: 4/4 narration localized" in result.stdout
    assert "Localization report: 7/51 demo steps" in result.stdout
    assert "- localized questions: 3/16" in result.stdout
    assert "- localized answers: 3/16" in result.stdout
    assert "questionAliases.fr present on 1/27 entrypoints (2 aliases)" in result.stdout
    assert "localizedTitles.fr present on 0/27 entrypoints" in result.stdout
    assert "localizedPurposes.fr present on 0/27 entrypoints" in result.stdout
    assert "Use --language with voices, doctor, demo, or controller" in result.stdout
    assert "Unsupported presenter language" not in result.output


def test_localization_report_require_complete_fails_for_french_seed() -> None:
    result = CliRunner().invoke(
        app,
        [
            "localization-report",
            "--package",
            "ringcentral-video",
            "--language",
            "fr",
            "--require-complete",
        ],
    )

    assert result.exit_code == 1
    assert "Language: fr" in result.stdout
    assert "- meeting-basics-demo: 3/3 narration localized" in result.stdout
    assert "- vbg-blur-demo: 4/4 narration localized" in result.stdout
    assert "Localization report: 7/51 demo steps" in result.stdout
    assert "- localized questions: 3/16" in result.stdout
    assert "- localized answers: 3/16" in result.stdout
    assert "Localization coverage incomplete for fr." in result.stdout
    assert "Unsupported presenter language" not in result.output


def test_localization_report_require_complete_passes_for_spanish_package() -> None:
    result = CliRunner().invoke(
        app,
        [
            "localization-report",
            "--package",
            "ringcentral-video",
            "--language",
            "es",
            "--require-complete",
        ],
    )

    assert result.exit_code == 0
    assert "Language: es" in result.stdout
    assert "- vbg-blur-demo: 4/4 narration localized" in result.stdout
    assert "- meeting-basics-demo: 3/3 narration localized" in result.stdout
    assert "- meeting-controls-tour: 22/22 narration localized" in result.stdout
    assert "- meeting-control-map-demo: 22/22 narration localized" in result.stdout
    assert "Localization report: 51/51 demo steps" in result.stdout
    assert "- localized questions: 16/16" in result.stdout
    assert "- localized answers: 16/16" in result.stdout
    assert "Localization coverage incomplete for es." not in result.stdout


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
    assert "- localized questions: 16/16" in result.stdout
    assert "- localized answers: 16/16" in result.stdout
    assert "Localization coverage incomplete for ja." not in result.stdout


def test_entrypoints_lists_material_package_entrypoints_by_area() -> None:
    result = CliRunner().invoke(
        app,
        ["entrypoints", "--package", "ringcentral-video", "--area", "Meeting toolbar"],
    )

    assert result.exit_code == 0
    assert "Package: ringcentral-video" in result.stdout
    assert (
        "- ringcentral.video.toolbar.audio: Microphone control [Meeting toolbar]"
    ) in result.stdout
    assert "- ringcentral.video.toolbar.leave: Leave meeting [Meeting toolbar]" in result.stdout
    assert "ringcentral.video.top.meeting-info" not in result.stdout
    assert "(title:" not in result.stdout
    assert "purpose:" not in result.stdout


def _assert_entrypoint_display_marker(
    output: str,
    *,
    entrypoint_id: str,
    area: str,
    title_source: str,
    purpose_source: str,
) -> None:
    lines = output.splitlines()
    line_prefix = f"- {entrypoint_id}: "
    for index, line in enumerate(lines):
        if not line.startswith(line_prefix):
            continue
        assert f"[{area}] (title: {title_source})" in line
        assert index + 1 < len(lines)
        purpose_line = lines[index + 1]
        assert purpose_line.startswith("  purpose: ")
        assert purpose_line.endswith(f"({purpose_source})")
        return
    raise AssertionError(f"{entrypoint_id} not found in entrypoints output")


def test_entrypoints_language_inspects_ringcentral_localized_and_fallback_copy() -> None:
    top_bar_result = CliRunner().invoke(
        app,
        [
            "entrypoints",
            "--package",
            "ringcentral-video",
            "--area",
            "Meeting top bar",
            "--language",
            "es",
        ],
    )

    assert top_bar_result.exit_code == 0
    assert "Language: es" in top_bar_result.stdout
    assert (
        "- ringcentral.video.top.network-quality: Calidad de red "
        "[Meeting top bar] (title: localized)"
    ) in top_bar_result.stdout
    assert (
        "  purpose: Abre Network quality para revisar packet loss, jitter y latency "
        "de Share, video y audio cuando la reuni\u00f3n se siente inestable. (localized)"
    ) in top_bar_result.stdout
    assert (
        "- ringcentral.video.top.views: Diseño de vista "
        "[Meeting top bar] (title: localized)"
    ) in top_bar_result.stdout
    assert (
        "  purpose: Abre Views para revisar Gallery view o Full screen en tu vista "
        "local sin cambiar audio, video ni participantes. (localized)"
    ) in top_bar_result.stdout
    assert (
        "- ringcentral.video.top.meeting-info: Meeting information "
        "[Meeting top bar] (title: fallback)"
    ) in top_bar_result.stdout
    assert (
        "  purpose: Open meeting details including meeting title, host, meeting ID, "
        "copy link, dial-in info, encryption, and end-to-end encryption option. (fallback)"
    ) in top_bar_result.stdout
    assert (
        "- ringcentral.video.top.report-issue: Report issue "
        "[Meeting top bar] (title: fallback)"
    ) in top_bar_result.stdout
    assert "ringcentral.video.toolbar.audio" not in top_bar_result.stdout

    toolbar_result = CliRunner().invoke(
        app,
        [
            "entrypoints",
            "--package",
            "ringcentral-video",
            "--area",
            "Meeting toolbar",
            "--language",
            "es",
        ],
    )

    assert toolbar_result.exit_code == 0
    _assert_entrypoint_display_marker(
        toolbar_result.stdout,
        entrypoint_id="ringcentral.video.toolbar.audio-menu",
        area="Meeting toolbar",
        title_source="localized",
        purpose_source="localized",
    )
    _assert_entrypoint_display_marker(
        toolbar_result.stdout,
        entrypoint_id="ringcentral.video.toolbar.video-menu",
        area="Meeting toolbar",
        title_source="localized",
        purpose_source="localized",
    )
    assert (
        "- ringcentral.video.toolbar.more: Más acciones "
        "[Meeting toolbar] (title: localized)"
    ) in toolbar_result.stdout
    assert (
        "  purpose: Abre More para mostrar acciones adicionales de la reunión y "
        "explicar su ubicación sin iniciar grabaciones ni otros cambios. (localized)"
    ) in toolbar_result.stdout
    _assert_entrypoint_display_marker(
        toolbar_result.stdout,
        entrypoint_id="ringcentral.video.toolbar.audio",
        area="Meeting toolbar",
        title_source="fallback",
        purpose_source="fallback",
    )

    more_menu_result = CliRunner().invoke(
        app,
        [
            "entrypoints",
            "--package",
            "ringcentral-video",
            "--area",
            "More menu",
            "--language",
            "es",
        ],
    )

    assert more_menu_result.exit_code == 0
    _assert_entrypoint_display_marker(
        more_menu_result.stdout,
        entrypoint_id="ringcentral.video.more.background",
        area="More menu",
        title_source="localized",
        purpose_source="localized",
    )
    assert (
        "- ringcentral.video.more.settings: Ajustes [More menu] (title: localized)"
    ) in more_menu_result.stdout
    assert (
        "  purpose: Abre Settings para revisar opciones de audio, video, Background, "
        "Translation, Join preferences y General sin cambiar configuraciones ni leer "
        "datos privados. (localized)"
    ) in more_menu_result.stdout
    _assert_entrypoint_display_marker(
        more_menu_result.stdout,
        entrypoint_id="ringcentral.video.more.recording",
        area="More menu",
        title_source="fallback",
        purpose_source="fallback",
    )


@pytest.mark.parametrize("language_alias", ["Spanish", "es-MX"])
def test_entrypoints_language_normalizes_spanish_alias_for_display_metadata(
    language_alias: str,
) -> None:
    result = CliRunner().invoke(
        app,
        [
            "entrypoints",
            "--package",
            "ringcentral-video",
            "--area",
            "Meeting toolbar",
            "--language",
            language_alias,
        ],
    )

    assert result.exit_code == 0
    assert "Language: es" in result.stdout
    _assert_entrypoint_display_marker(
        result.stdout,
        entrypoint_id="ringcentral.video.toolbar.audio-menu",
        area="Meeting toolbar",
        title_source="localized",
        purpose_source="localized",
    )
    _assert_entrypoint_display_marker(
        result.stdout,
        entrypoint_id="ringcentral.video.toolbar.video-menu",
        area="Meeting toolbar",
        title_source="localized",
        purpose_source="localized",
    )
    _assert_entrypoint_display_marker(
        result.stdout,
        entrypoint_id="ringcentral.video.toolbar.audio",
        area="Meeting toolbar",
        title_source="fallback",
        purpose_source="fallback",
    )

    more_menu_result = CliRunner().invoke(
        app,
        [
            "entrypoints",
            "--package",
            "ringcentral-video",
            "--area",
            "More menu",
            "--language",
            language_alias,
        ],
    )

    assert more_menu_result.exit_code == 0
    assert "Language: es" in more_menu_result.stdout
    _assert_entrypoint_display_marker(
        more_menu_result.stdout,
        entrypoint_id="ringcentral.video.more.background",
        area="More menu",
        title_source="localized",
        purpose_source="localized",
    )
    _assert_entrypoint_display_marker(
        more_menu_result.stdout,
        entrypoint_id="ringcentral.video.more.recording",
        area="More menu",
        title_source="fallback",
        purpose_source="fallback",
    )


def test_entrypoints_language_uses_package_local_metadata_without_runtime_voice_validation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_runtime_voice_call(*args: object, **kwargs: object) -> None:
        raise AssertionError("entrypoints --language must not inspect runtime voices")

    monkeypatch.setattr(cli, "resolve_voice_settings", fail_runtime_voice_call)
    monkeypatch.setattr(cli, "validate_cli_voice_profile", fail_runtime_voice_call)
    monkeypatch.setattr(cli, "resolve_speech_provider_name", fail_runtime_voice_call)
    monkeypatch.setattr(cli, "check_voice_asset_availability", fail_runtime_voice_call)

    package_path = tmp_path / "package-local-entrypoints.yaml"
    package_path.write_text(
        """
appId: demo
appName: Demo
version: 1
profileIds: [ringcentral-video]
operationEntrypoints:
  - id: demo.panel
    title: Panel
    area: Main
    purpose: Explain panel.
    localizedTitles:
      de: Bereich
    localizedPurposes:
      de: Erklaert den Bereich.
    openSteps: []
demoFlows: []
manualControls: []
""",
        encoding="utf-8",
    )

    result = CliRunner().invoke(
        app,
        ["entrypoints", "--package", str(package_path), "--language", "de"],
    )

    assert result.exit_code == 0
    assert "Package: demo" in result.stdout
    assert "Language: de" in result.stdout
    assert "- demo.panel: Bereich [Main] (title: localized)" in result.stdout
    assert "  purpose: Erklaert den Bereich. (localized)" in result.stdout


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
    assert_acceptance_draft_boundary(result.stdout)
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
    assert_acceptance_draft_boundary(result.stdout)
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
    assert_acceptance_draft_refusal_boundary(output)


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
    assert_acceptance_draft_refusal_boundary(output)
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
    assert_acceptance_draft_boundary(text)
    assert "acceptance evidence" not in result.stdout.casefold()


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
    assert_acceptance_draft_refusal_boundary(result.output)
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
    assert_acceptance_draft_refusal_boundary(result.output)
    assert not output_path.exists()


def test_validation_targets_lists_ringcentral_targets() -> None:
    result = CliRunner().invoke(
        app,
        ["validation-targets", "--package", "ringcentral-video", "--priority", "P0"],
    )

    assert result.exit_code == 0
    assert "Package: ringcentral-video" in result.stdout
    assert VALIDATION_TARGETS_CHECKLIST_SOURCE in result.stdout
    assert VALIDATION_TARGETS_EVIDENCE_SOURCE in result.stdout
    assert VALIDATION_TARGETS_ACCEPTANCE_SOURCE in result.stdout
    assert VALIDATION_TARGETS_NON_EVIDENCE_NOTE in result.stdout
    assert result.stdout.count(VALIDATION_TARGETS_EVIDENCE_REMINDER) == 1
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
    assert VALIDATION_TARGETS_CHECKLIST_SOURCE in result.stdout
    assert VALIDATION_TARGETS_EVIDENCE_SOURCE in result.stdout
    assert "ringcentral.video.main.add-coworkers" in result.stdout
    assert VALIDATION_TARGETS_NON_EVIDENCE_NOTE in result.stdout
    assert result.stdout.index(VALIDATION_TARGETS_EVIDENCE_REMINDER) < result.stdout.index(
        "draft:"
    )
    assert "Modal close" in result.stdout
    assert "invite links" in result.stdout
    assert (
        "ai-presenter acceptance-draft --package ringcentral-video "
        "--entrypoint ringcentral.video.main.add-coworkers"
    ) in result.stdout


def test_validation_targets_detail_outputs_entrypoint_draft_examples_for_group() -> None:
    result = CliRunner().invoke(
        app,
        [
            "validation-targets",
            "--package",
            "ringcentral-video",
            "--target",
            "rcv-top-bar-routes",
        ],
    )

    assert result.exit_code == 0
    assert "entrypoint draft examples:" in result.stdout
    assert (
        "draft: ai-presenter acceptance-draft --package ringcentral-video "
        '--checklist-target "P1 Top-bar coordinate routes"'
    ) in result.stdout
    assert (
        "- ai-presenter acceptance-draft --package ringcentral-video "
        "--entrypoint ringcentral.video.top.meeting-info "
        '--checklist-target "P1 Top-bar coordinate routes"'
    ) in result.stdout
    assert (
        "- ai-presenter acceptance-draft --package ringcentral-video "
        "--entrypoint ringcentral.video.top.report-issue "
        '--checklist-target "P1 Top-bar coordinate routes"'
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
    assert VALIDATION_TARGETS_NON_EVIDENCE_NOTE in result.stdout
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


def test_validation_targets_rejects_unbacked_accepted_evidence(
    tmp_path: Path,
) -> None:
    evidence_path = tmp_path / "evidence-index.md"
    acceptance_path = tmp_path / "acceptance-runs.md"
    evidence_text = Path("docs/knowledge/ringcentral-video/evidence-index.md").read_text(
        encoding="utf-8"
    )
    evidence_path.write_text(
        evidence_text.replace(
            "| `ringcentral.video.toolbar.chat` | Executable UIA route with toggle cleanup | `Observed` |",
            "| `ringcentral.video.toolbar.chat` | Executable UIA route with toggle cleanup | `Accepted` |",
        ),
        encoding="utf-8",
    )
    acceptance_path.write_text(
        Path("docs/knowledge/ringcentral-video/acceptance-runs.md").read_text(
            encoding="utf-8"
        ),
        encoding="utf-8",
    )

    result = CliRunner().invoke(
        app,
        [
            "validation-targets",
            "--package",
            "ringcentral-video",
            "--evidence",
            str(evidence_path),
            "--target",
            "rcv-controller-chat-question",
        ],
    )

    assert result.exit_code != 0
    assert "Accepted evidence for ringcentral.video.toolbar.chat" in result.output
    assert "dated passing live/manual acceptance run" in result.output
    assert "acceptance-runs.md" in result.output


def test_validation_targets_accepts_backed_accepted_evidence(
    tmp_path: Path,
) -> None:
    evidence_path = tmp_path / "evidence-index.md"
    acceptance_path = tmp_path / "acceptance-runs.md"
    evidence_text = Path("docs/knowledge/ringcentral-video/evidence-index.md").read_text(
        encoding="utf-8"
    )
    evidence_path.write_text(
        evidence_text.replace(
            "| `ringcentral.video.toolbar.chat` | Executable UIA route with toggle cleanup | `Observed` |",
            "| `ringcentral.video.toolbar.chat` | Executable UIA route with toggle cleanup | `Accepted` |",
        ),
        encoding="utf-8",
    )
    acceptance_path.write_text(
        """
# RingCentral Video Acceptance Runs

## 2026-05-17 09:00 Local - Manual RingCentral Acceptance

- Entrypoint IDs tested: `ringcentral.video.toolbar.chat`
- Steps executed: Opened and closed the Chat panel.
- Outcome: pass
- Accepted promotion eligible: yes
- Promotion rationale: Current build route passed and cleanup restored.
- Recovery: Chat panel closed and toolbar was usable again.
- Privacy notes: No chat content was read or captured.
""",
        encoding="utf-8",
    )

    result = CliRunner().invoke(
        app,
        [
            "validation-targets",
            "--package",
            "ringcentral-video",
            "--evidence",
            str(evidence_path),
            "--acceptance-runs",
            str(acceptance_path),
            "--target",
            "rcv-controller-chat-question",
        ],
    )

    assert result.exit_code == 0
    assert f"Acceptance runs: {acceptance_path} (explicit)" in result.stdout
    assert "ringcentral.video.toolbar.chat=Accepted" in result.stdout
    assert "Steps executed" not in result.stdout
    assert "Promotion rationale" not in result.stdout
    assert "Privacy notes" not in result.stdout


def test_validation_targets_rejects_missing_explicit_acceptance_runs(
    tmp_path: Path,
) -> None:
    evidence_path = tmp_path / "evidence-index.md"
    missing_acceptance_path = tmp_path / "missing-acceptance-runs.md"
    evidence_text = Path("docs/knowledge/ringcentral-video/evidence-index.md").read_text(
        encoding="utf-8"
    )
    evidence_path.write_text(
        evidence_text.replace(
            "| `ringcentral.video.toolbar.chat` | Executable UIA route with toggle cleanup | `Observed` |",
            "| `ringcentral.video.toolbar.chat` | Executable UIA route with toggle cleanup | `Accepted` |",
        ),
        encoding="utf-8",
    )

    result = CliRunner().invoke(
        app,
        [
            "validation-targets",
            "--package",
            "ringcentral-video",
            "--evidence",
            str(evidence_path),
            "--acceptance-runs",
            str(missing_acceptance_path),
            "--target",
            "rcv-controller-chat-question",
        ],
    )

    assert result.exit_code != 0
    assert missing_acceptance_path.name in result.output
    assert "ringcentral.video.toolbar.chat=Accepted" not in result.output


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
    assert VALIDATION_TARGETS_NON_EVIDENCE_NOTE in result.stdout
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
    assert "Spanish aliases:" in result.stdout
    assert "es-419" in result.stdout
    assert "latam-spanish" in result.stdout
    assert "latin-american-spanish" in result.stdout
    assert "espa\\xf1ol" in result.stdout
    assert "Tones:" in result.stdout
    assert "Coach aliases:" in result.stdout
    assert "Executive aliases:" in result.stdout
    assert "Instructor aliases:" in result.stdout
    assert "Support aliases:" in result.stdout
    assert "Careful aliases:" in result.stdout
    assert "calm" in result.stdout
    assert "empathetic" in result.stdout
    assert "executive" in result.stdout
    assert "boardroom" in result.stdout
    assert "trainer" in result.stdout
    assert "tutorial" in result.stdout
    assert "decision-oriented" in result.stdout
    assert "instructional" in result.stdout
    assert "context-setting" in result.stdout
    assert "recovery-focused" in result.stdout
    assert "privacy-aware" in result.stdout


def test_voices_catalog_output_is_ascii_safe_for_legacy_windows_console() -> None:
    result = CliRunner().invoke(app, ["voices"])

    assert result.exit_code == 0
    assert result.stdout.isascii()


def test_voices_catalog_explains_language_readiness_boundaries() -> None:
    result = CliRunner().invoke(app, ["voices"])

    assert result.exit_code == 0
    assert "Language readiness:" in result.stdout
    assert "--language selects a runtime presenter voice" in result.stdout
    assert "--profile checks speech provider compatibility and local voice assets" in (
        result.stdout
    )
    assert "Package localization and live acceptance are separate checks" in (
        result.stdout
    )


def test_voices_targeted_executive_alias_reports_canonical_tone() -> None:
    result = CliRunner().invoke(app, ["voices", "--tone", "briefing"])

    assert result.exit_code == 0
    assert "Selected voice: English / Executive" in result.stdout


def test_voices_targeted_instructor_alias_reports_canonical_tone() -> None:
    result = CliRunner().invoke(app, ["voices", "--tone", "tutorial"])

    assert result.exit_code == 0
    assert "Selected voice: English / Instructor" in result.stdout


def test_voices_profile_reports_supported_and_unsupported_languages() -> None:
    result = CliRunner().invoke(app, ["voices", "--profile", "ringcentral-video"])

    assert result.exit_code == 0
    assert "Profile: ringcentral-video" in result.stdout
    assert "Configured speech provider: fake" in result.stdout
    assert "English / Professional: supported via fake" in result.stdout
    assert "Chinese / Professional: unsupported" in result.stdout
    assert "Japanese / Professional: unsupported" in result.stdout
    assert "Spanish / Professional: unsupported" in result.stdout


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


def test_voices_reuses_profile_asset_checks_for_selected_route(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[str, str]] = []

    def fake_check_assets(
        _profile: object,
        voice: PresenterVoiceSettings,
    ) -> VoiceAssetAvailability:
        calls.append((voice.language, voice.tone))
        return VoiceAssetAvailability(
            status="OK",
            route=f"route-{voice.language}",
            detail=f"asset check {len(calls)} for {voice.language}",
        )

    monkeypatch.setattr(
        "ai_presenter.cli.check_voice_asset_availability",
        fake_check_assets,
    )

    result = CliRunner().invoke(
        app,
        [
            "voices",
            "--profile",
            "ringcentral-video-bind-speaker",
            "--language",
            "en-US",
            "--tone",
            "friendly",
        ],
    )

    assert result.exit_code == 0
    assert "Selected voice assets available" in result.stdout
    assert calls == [("en", "professional"), ("zh", "professional")]


def test_voices_targeted_incompatible_profile_voice_exits_nonzero() -> None:
    result = CliRunner().invoke(
        app,
        ["voices", "--profile", "ringcentral-video", "--language", "zh-CN", "--tone", "friendly"],
    )

    assert result.exit_code == 1
    assert "Selected voice: Chinese / Friendly" in result.stdout
    assert "speech provider fake" in result.stdout


def test_voices_targeted_openai_spanish_profile_is_supported() -> None:
    result = CliRunner().invoke(
        app,
        [
            "voices",
            "--profile",
            "profiles/ringcentral-video-openai.example.yaml",
            "--language",
            "es",
        ],
    )

    assert result.exit_code == 0
    assert "Selected voice: Spanish / Professional" in result.stdout
    assert "Selected voice supported via openai." in result.stdout


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
    assert "171 package-owned aliases have no cross-entrypoint duplicates" in result.stdout
    assert "[OK] qa questions:" in result.stdout
    assert "224 Q&A question prompts have no cross-item duplicates" in result.stdout
    assert "[OK] qa alias overlap:" in result.stdout
    assert "224 Q&A question prompts have no unsafe package-owned alias overlaps" in result.stdout
    assert "[INFO] qa alias substring risk:" in result.stdout
    assert (
        "11 Q&A question prompts contain package-owned alias substrings outside "
        "related entrypoints"
    ) in result.stdout
    assert "[OK] question policy:" in result.stdout
    assert (
        "2/27 entrypoints use answerOnly question policy: "
        "ringcentral.video.top.meeting-info, ringcentral.video.more.notes"
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
    assert "[OK] runtime language support: localization language zh" in result.stdout


def test_doctor_require_localization_accepts_spanish_runtime_language(
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
            "--localization-language",
            "es",
        ],
    )

    assert result.exit_code == 0
    assert "[OK] localization: required es localization complete" in result.stdout
    assert "51/51 demo steps" in result.stdout
    assert "16/16 Q&A questions" in result.stdout
    assert "16/16 Q&A answers" in result.stdout
    assert "[OK] runtime language support: localization language es" in result.stdout
    assert "Spanish" in result.stdout
    assert "Invalid value" not in result.output


def test_doctor_rejects_package_only_language_after_complete_localization(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(diagnostics, "_iter_process_executable_paths", lambda process_name: [])
    package_path = tmp_path / "package-only-language.yaml"
    package_path.write_text(
        """
appId: demo
appName: Demo
version: 1
profileIds: [ringcentral-video-bind-speaker]
operationEntrypoints:
  - id: demo.panel
    title: Panel
    area: Main
    purpose: Explain panel.
    openSteps: []
demoFlows:
  - id: demo-tour
    title: Demo tour
    goal: Show one localized package-only step.
    steps:
      - id: show-panel
        title: Show panel
        action:
          entrypointId: demo.panel
          operation: explain
        narration:
          text: This explains the panel.
          localizedText:
            de: Das erklaert das Panel.
qa:
  - question: Where is the panel?
    answer: The panel is on screen.
    localizedQuestions:
      de:
        - Wo ist das Panel?
    localizedAnswers:
      de: Das Panel ist auf dem Bildschirm.
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
            "--require-localization",
            "--localization-language",
            "de",
        ],
    )

    assert result.exit_code == 1
    assert "[OK] localization: required de localization complete" in result.stdout
    assert "1/1 demo steps" in result.stdout
    assert "1/1 Q&A questions" in result.stdout
    assert "[FAIL] runtime language support: localization language de" in result.stdout
    assert "presenter runtime does not support --language de" in result.stdout


def test_doctor_openai_profile_accepts_spanish_runtime_language(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config_path = tmp_path / "config.ini"
    config_path.write_text("DisableAffinityMask=true\n", encoding="utf-8")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("AI_PRESENTER_OPENAI_NARRATION_MODEL", "test-model")

    result = CliRunner().invoke(
        app,
        [
            "doctor",
            "--profile",
            "profiles/ringcentral-video-openai.example.yaml",
            "--package",
            "ringcentral-video",
            "--flow",
            "meeting-control-map-demo",
            "--language",
            "es",
            "--require-localization",
            "--ringcentral-config",
            str(config_path),
        ],
    )

    assert result.exit_code == 0
    assert "[OK] localization: required es localization complete" in result.stdout
    assert "[OK] runtime language support: localization language es" in result.stdout
    assert "[OK] voice: Spanish / Professional supported via speech=openai" in result.stdout


def test_doctor_require_localization_language_overrides_runtime_voice(
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
            "--language",
            "zh-CN",
            "--require-localization",
            "--localization-language",
            "es",
        ],
    )

    assert result.exit_code == 0
    assert "[OK] localization: required es localization complete" in result.stdout
    assert "51/51 demo steps" in result.stdout
    assert "[OK] runtime language support: localization language es" in result.stdout
    assert "[OK] voice: Chinese / Professional supported" in result.stdout


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
