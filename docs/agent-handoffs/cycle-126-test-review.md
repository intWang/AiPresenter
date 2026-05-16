# Cycle 126 Test Review: Latin Diacritic Folding Shared Normalization

Date: 2026-05-17
Role: test and code review subagent

## Findings

1. P2: `normalize_question_prompt()` uses `unicodedata.normalize("NFKD", ...)` over the whole string before selectively dropping combining marks after Latin base characters. The mark-dropping itself is Latin-scoped, but `NFKD` also performs compatibility decomposition for non-Latin text. A direct probe shows half-width Japanese input is normalized to standard Katakana and now matches package aliases:
   - `'\uff81\uff6c\uff6f\uff84\uff8a\uff9f\uff88\uff99\u306f\u3069\u3053\u3067\u3059\u304b'` routes to `ringcentral.video.toolbar.chat`.
   - The full-width equivalent also routes to `ringcentral.video.toolbar.chat`.
   This may be acceptable as a broader Japanese normalization improvement, but it is outside the stated "Latin diacritic folding" scope and the current tests only assert ordinary CJK strings survive unchanged. If the intended boundary is truly "do not width-fold Japanese/Kana", use canonical decomposition (`NFD`) or decompose/fold Latin characters only. If width folding is acceptable, add an explicit test and document that compatibility folding is part of the match key.

No blocking findings found for Q&A-first precedence, diagnostics/runtime consistency, Spanish runtime support, or documented counts.

## Main-session resolution

- Added `test_halfwidth_japanese_input_is_not_folded_into_package_alias` to
  reproduce the P2 concern through the real `answer_question()` path.
- Confirmed the test failed under `NFKD`: halfwidth Japanese input matched the
  fullwidth Japanese package alias.
- Changed the canonicalizer to use `NFD`, preserving Latin accent folding while
  avoiding compatibility width folding for Japanese aliases.
- Re-ran the focused normalization, Q&A precedence, diagnostics, affected unit,
  full pytest, ruff, mypy, and RingCentralVideo CLI boundary checks before
  landing Cycle 126.

## Verification

- Reviewed current uncommitted diff for:
  - `src/ai_presenter/packages/models.py`
  - `src/ai_presenter/runtime/questions.py`
  - `src/ai_presenter/runtime/diagnostics.py`
  - `src/ai_presenter/runtime/voice.py`
  - `tests/unit/test_material_packages.py`
  - `tests/unit/test_questions.py`
  - `tests/unit/test_diagnostics.py`
  - `tests/unit/test_cli.py`
  - `docs/agent-handoffs/cycle-126-*.md`
- `.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py tests\unit\test_questions.py tests\unit\test_diagnostics.py`
  - Result: `307 passed in 57.40s`.
- `.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_cli.py::test_localization_report_outputs_complete_spanish_package tests\unit\test_cli.py::test_localization_report_require_complete_passes_for_spanish_package tests\unit\test_cli.py::test_demo_rejects_unknown_language_before_runtime tests\unit\test_cli.py::test_doctor_loads_profile_package_and_flow tests\unit\test_cli.py::test_doctor_require_localization_accepts_package_only_spanish_language`
  - Result: `5 passed in 1.77s`.
- `.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language es`
  - Result: exit `0`; reports `51/51` demo steps, `12/12` Q&A questions, `12/12` Q&A answers, and `questionAliases.es` on `26/27` entrypoints with `69 aliases`.
- `.\.venv\Scripts\ai-presenter.exe demo --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo --language es --dry-run`
  - Result: expected exit `1`; output contains `Unsupported presenter language: es`.
- `.\.venv\Scripts\ai-presenter.exe doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo`
  - Result: exit `0`; `156` package-owned aliases, `84` Q&A prompts, `1 info`, `0 warnings`, `0 failed`.
- `.\.venv\Scripts\ai-presenter.exe doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --require-localization --localization-language es`
  - Result: expected exit `1`; Spanish localization is OK, runtime language support fails because `es` remains package-only.
- `git diff --check`
  - Result: exit `0`; only CRLF conversion warnings for touched files.
- Direct Q&A-first probes:
  - `Puede AiPresenter enviar una reaccion o levantar la mano de forma segura?` returns the authored Reactions/Raise hand Q&A text, `entrypoint_id=None`, `can_operate=False`.
  - `Puede leer los mensajes del chat o los nombres de participantes?` returns the authored privacy Q&A text, `entrypoint_id=None`, `can_operate=False`.
  - `Como manejo la grabacion de la reunion de forma segura?` returns the recording safety Q&A, `entrypoint_id=ringcentral.video.more.recording`, `can_operate=False`.
  - `Donde esta el menu de camara en la reunion?` routes to `ringcentral.video.toolbar.video-menu`, `can_operate=True`.

## Residual risks

- Current tests cover accented Spanish folding and ordinary Japanese/Chinese preservation, but not the compatibility-normalization boundary introduced by `NFKD` for half-width Katakana, full-width Latin, ligatures, or other compatibility characters.
- Q&A-first unaccented tests verify `entrypoint_id` and `can_operate`; direct probes confirmed authored Q&A text for the highest-risk `None` routes, but the assertions could be stronger if future reviewers want test evidence rather than review evidence.
- No full repository test suite was run. The review focused on the touched runtime/package/diagnostics/tests plus CLI boundary checks.
- `.coverage` is modified in the working tree and remains an unstaged local artifact.

## Recommendation

Conditional go. The shared normalization design is aligned across package aliases, Q&A candidates, runtime question normalization, diagnostics, tokenization, and legacy aliases; Q&A-first behavior is preserved; Spanish runtime remains unsupported; and counts are consistent with Cycle 126 docs.

Before landing, decide whether `NFKD` compatibility folding for Japanese/full-width forms is intended. If not, tighten the canonicalizer to avoid width folding. If it is intended, add explicit tests that lock in the widened behavior so it is not an accidental side effect hidden inside a Latin diacritic slice.
