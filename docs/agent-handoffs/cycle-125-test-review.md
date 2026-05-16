# Cycle 125 Test Review

Date: 2026-05-17

## Findings

- P3 - `docs/agent-handoffs/cycle-125-technical-scan.md:28`, `docs/agent-handoffs/cycle-125-technical-scan.md:100`, `docs/agent-handoffs/cycle-125-technical-scan.md:101`, and `docs/agent-handoffs/cycle-125-technical-scan.md:137` still describe the post-implementation expectation as `27/27` Spanish alias entrypoints and `72` aliases. The current implementation, tests, CLI output, and implementation handoff intentionally settle on `26/27` and `69` because `ringcentral.video.settings.background.blur` is left without a Spanish alias. This is not a runtime blocker, but it is a documentation/count inconsistency that can mislead the next acceptance or cleanup pass.

No P1/P2 code findings. I did not find evidence that the runtime matching tweak breaks exact Q&A, special safety Q&A, or fragment Q&A precedence. I also did not find evidence that Spanish runtime support was enabled.

## Verification

- Reviewed the uncommitted diff for:
  - `packages/ringcentral-video.yaml`
  - `src/ai_presenter/runtime/questions.py`
  - `tests/unit/test_cli.py`
  - `tests/unit/test_diagnostics.py`
  - `tests/unit/test_material_packages.py`
  - `tests/unit/test_questions.py`
  - `docs/agent-handoffs/cycle-125-*.md`
  - `docs/agent-handoffs/cycle-125-experience.md`, which is consistent with the implemented `26/27`, `69`, and `156` counts.
- Checked runtime order in `src/ai_presenter/runtime/questions.py`: exact Q&A, recording/notes safety heuristics, entrypoint-title guard, and Q&A fragment checks still run before the new package-alias guard. The new guard only skips the final fuzzy Q&A token fallback when a package-owned alias is present, allowing entrypoint alias matching to handle the prompt afterward.
- Reviewed Spanish aliases for obvious duplicate, overly short, and high-risk broad forms. The added aliases are mostly location/control-label phrases. Sensitive routes remain guarded by `answerOnly`, empty `openSteps`, or `_RISKY_ENTRYPOINT_WORDS` behavior.
- Ran focused tests:
  - `.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_spanish_seed_qa_and_aliases_are_present tests\unit\test_material_packages.py::test_ringcentral_package_owns_spanish_aliases_for_location_routes tests\unit\test_material_packages.py::test_ringcentral_localization_status_reports_complete_spanish_package tests\unit\test_questions.py::test_ringcentral_spanish_location_questions_match_package_aliases_without_legacy_table tests\unit\test_questions.py::test_ringcentral_spanish_safety_questions_stay_qa_first_with_aliases tests\unit\test_diagnostics.py::test_diagnostics_reports_question_aliases_ok_for_ringcentral_package tests\unit\test_cli.py::test_localization_report_outputs_complete_spanish_package tests\unit\test_cli.py::test_doctor_loads_profile_package_and_flow`
  - Result: `11 passed`.
- Ran Spanish question tests:
  - `.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py -k "spanish"`
  - Result: `8 passed, 164 deselected`.
- Ran CLI localization checks:
  - `.\.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language es`
  - Result: reports `51/51` demo steps, `12/12` localized questions, `12/12` localized answers, and `questionAliases.es present on 26/27 entrypoints (69 aliases)`.
  - `.\.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language es --require-complete`
  - Result: exits `0` with the same counts.
- Ran runtime Spanish boundary check:
  - `.\.venv\Scripts\ai-presenter demo --profile ringcentral-video --package ringcentral-video --flow meeting-controls-tour --language es --dry-run`
  - Result: exits `1` with `Unsupported presenter language: es`.
- Ran doctor package-only Spanish boundary check:
  - `.\.venv\Scripts\ai-presenter doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo --require-localization --localization-language es`
  - Result: localization is OK, question aliases report `156 package-owned aliases`, Q&A overlap remains OK, substring risk remains INFO at `11`, and runtime language support fails as expected because `es` is package-only.
- Ran `git diff --check`.
  - Result: no whitespace errors reported; only CRLF conversion warnings for touched text files.
- Ran a small routing probe for representative Spanish privacy/action/location prompts. Safety prompts for chat/participants privacy, shared content, recording, and reaction/raise-hand remained non-operable; location prompts for chat, participants, notes, and leave routed to their intended entrypoints with current `can_operate` policy.

## Residual risks

- Matching remains accent-sensitive because package normalization is `strip().casefold()` only. Users typing unaccented Spanish variants may miss package aliases unless other token matching catches them.
- The new runtime guard is intentionally language-agnostic: any package-owned alias substring, regardless of alias language, suppresses only the final fuzzy Q&A token fallback. Existing focused tests cover the current Spanish risk examples, but future broad aliases in any language could make this guard more consequential.
- Some sensitive aliases include English UI labels and route names such as `share`, `invite`, `start recording`, `notes and transcript`, and `leave`. Current `can_operate` and tests keep them non-operable where required, but future changes to `_RISKY_ENTRYPOINT_WORDS`, `questionPolicy`, or `openSteps` could raise the blast radius.
- `.coverage` is modified in the worktree. It was present before this review and should not be staged for this cycle unless explicitly desired.

## Recommendation

Accept the code/test behavior for Cycle 125 after acknowledging or cleaning up the technical-scan count mismatch. The runtime tweak is narrowly scoped, Spanish runtime support remains disabled, and the focused tests plus CLI checks cover the main Q&A-first and package-local alias risks.
