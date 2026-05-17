# Cycle 181 Test Review

Date: 2026-05-17

## Red-Green Notes

Initial focused run after adding tests produced expected failures:

- Chinese `列出参会者` and `谁在会议里` routed operably to `ringcentral.video.toolbar.participants`.
- Chinese `读参会人名字` was non-operable but returned the generic no-match answer instead of privacy guidance.
- Japanese `参加者名を読んで` routed operably to the Participants panel.
- Spanish panel/list-plus-identity prompts were not consistently privacy-routed.
- Session/controller ja/es additions failed because the default profile does not support those speech providers.

After the runtime matcher update and test-scope correction, the focused slice passed:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -B -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests\unit\test_questions.py tests\unit\test_controller.py tests\unit\test_controller_session.py -k "localized_participant_identity or participants_panel_location_requests or chinese_questions_match_package_aliases_without_legacy_table or safe_mixed_meta_question or sensitive_mixed_meta_question or safe_mixed_presenter_meta_answer or sensitive_mixed_presenter_meta_answer"
```

Result: `54 passed, 481 deselected`.

Full verification after updating the legacy title-label test:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m mypy src tests
```

Results:

- `1159 passed, 1 warning`
- `All checks passed!`
- `Success: no issues found in 81 source files`

## Review Findings

- The runtime slice is intentionally constant-only and does not affect YAML diagnostics.
- Localized question-routing coverage now spans zh/ja/es for both safe panel navigation and identity rejection.
- Controller/session coverage stays on Chinese prompts because the default profile supports Chinese voice output through SAPI/OpenAI routes, while ja/es require an OpenAI profile.
- The Spanish safe panel answer uses the localized title `panel de participantes:`, so tests should not require `Participants panel:` for every language.
- Independent review reported no findings for the localized participant privacy diff.

## Residual Risks

- Accented Spanish variants should be expanded in a future cycle with direct tests using UTF-8 source strings.
- Bare localized participant aliases such as `参会者` and `参加者` remain operable; future product policy should decide whether bare terms mean panel navigation or disclosure.
- Live RingCentral acceptance was not run, because this cycle only changes offline routing and privacy boundaries.
