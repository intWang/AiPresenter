# Cycle 022 Technical Scan: RingCentral Video Localized And Tone Content

Date: 2026-05-16

## Scope

Scan target: implementation path for expanding `RingCentralVideo` localized and tone-aware package content.

Safety boundary for this scan: no production, package, or test edits. This handoff is the only file created.

## Current Architecture And Relevant Files

- `packages/ringcentral-video.yaml`
  - Current source for RingCentral Video app material: `profileIds`, `operationEntrypoints`, `demoFlows`,
    `explainers`, `qa`, and `manualControls`.
  - Current package shape: 27 entrypoints, 4 demo flows, and 3 Q&A entries.
  - Current localized coverage:
    - `meeting-control-map-demo`: all 22 steps have `narration.localizedText.zh`.
    - `vbg-blur-demo`: 0 of 4 steps have localized narration.
    - `meeting-basics-demo`: 0 of 3 steps have localized narration.
    - `meeting-controls-tour`: 0 of 22 steps have localized narration.
    - 5 entrypoints have package-owned `questionAliases.zh`: background, share, invite, chat, leave.
    - 1 of 3 Q&A items has `localizedQuestions.zh` and `localizedAnswers.zh`.
- `src/ai_presenter/packages/models.py`
  - `CamelModel` uses `extra="forbid"`, so new YAML fields require schema updates.
  - `OperationEntrypoint.question_aliases` maps `questionAliases` to `dict[str, list[str]]`.
  - `DemoStepNarration.localized_text` maps `localizedText` to `dict[str, str]`.
  - `QuestionAnswer.localized_questions` and `localized_answers` map `localizedQuestions` and
    `localizedAnswers`.
  - `MaterialPackage.validate_entrypoint_references()` builds read-only entrypoint indexes, normalizes
    package-owned question aliases, validates flow step entrypoint references, and validates explainer/Q&A
    `relatedEntrypointIds`.
- `src/ai_presenter/runtime/questions.py`
  - Q&A matching checks English `question` plus all `localizedQuestions`.
  - Q&A answers use `localizedAnswers[voice.language]` when present; localized answers are returned directly, without
    tone prefixes or concise truncation.
  - Entrypoint alias matching checks package-owned `questionAliases` first, then falls back to the hard-coded
    `_ENTRYPOINT_ALIASES` table.
  - Entrypoint answers are rendered from English `title: purpose` through `render_presenter_text()`.
  - `can_operate` is still determined from English entrypoint id/title/purpose risky words, so adding localized
    aliases should not make risky routes operable.
- `src/ai_presenter/runtime/voice.py`
  - Supported languages are currently `en` and `zh`.
  - Supported tones are `professional`, `conversational`, `concise`, `friendly`, `coach`, and `formal`.
  - Language/tone aliases normalize before runtime use, for example `zh-CN -> zh`, `warm -> friendly`, and
    `mentor -> coach`.
  - `render_narration_text()` prefers `narration.localized_text[settings.language]` when present.
  - Localized narration only gets tone handling for `concise`, via first-sentence truncation.
  - Non-localized Chinese fallback is not translation; it performs a small replacement map and optional tone prefix.
  - SAPI voice rate only varies for Chinese `conversational`, `friendly`, and `concise`.
- `tests/unit/test_material_packages.py`
  - Already validates localized Q&A support, package-owned aliases, read-only alias indexes, explainer coverage, and
    complete `meeting-control-map-demo` Chinese localized narration.
- `tests/unit/test_questions.py`
  - Already validates localized Q&A matching, package-owned alias precedence, longest alias wins, legacy alias fallback,
    risky route non-operability, and canonical language/tone logging.
- `tests/unit/test_cli.py`
  - Already validates CLI language/tone pass-through for `demo` and `controller`, normalized voice labels, unsupported
    profile voice rejection, `voices`, and `doctor` voice preflight.
  - No CLI change is required for a content-only RingCentral localization expansion.

## Recommended Minimal Slice

Use the existing schema first. Expand package-owned content in `packages/ringcentral-video.yaml` and add focused tests.
Do not add tone-specific YAML fields in the first slice.

Recommended package edits:

- Add `narration.localizedText.zh` to every step in:
  - `vbg-blur-demo`
  - `meeting-basics-demo`
  - `meeting-controls-tour`
- Add `localizedQuestions.zh` and `localizedAnswers.zh` to the remaining Q&A items:
  - `Can the presenter describe shared-screen content?`
  - `How can I bring people into the meeting?`
- Move the remaining RingCentral Chinese aliases out of runtime-only fallback and into package-owned
  `questionAliases.zh`, especially:
  - participants
  - audio
  - video
  - settings
  - recording
  - notes
  - reactions
  - raise hand
  - network quality
  - meeting information
- Keep English `narration.text` ASCII. Existing tests intentionally assert the primary narration text remains ASCII.
- Keep risky routes explain-only or non-operable. Localization should improve matching and narration, not expand safe
  automation behavior.

Key recommendation: treat `localizedText.zh` as carefully authored Chinese scripts, and treat `tone` as runtime
delivery style. The current schema is language-keyed, not language-plus-tone-keyed, so per-tone localized scripts would
be a separate schema change rather than a YAML-only content pass.

## Optional Second Slice For True Per-Tone Copy

If product requirements need distinct localized wording for `friendly`, `coach`, or `formal`, add a schema-backed field
in a separate cycle. A possible shape:

```yaml
localizedToneText:
  zh:
    friendly: ...
    coach: ...
```

That would require model, renderer, and tests in `models.py`, `voice.py`, and `test_voice.py`. Do not mix that with the
first content-expansion slice unless the requirement is explicit.

## Exact Tests To Add

Add to `tests/unit/test_material_packages.py`:

- `test_ringcentral_demo_flows_have_chinese_localized_narration`
  - Load `packages/ringcentral-video.yaml`.
  - For `vbg-blur-demo`, `meeting-basics-demo`, `meeting-controls-tour`, and `meeting-control-map-demo`, assert every
    step has nonblank `step.narration.localized_text["zh"]`.
  - Assert each localized script contains at least one CJK character.
  - Keep existing `step.narration.text.encode("ascii")` coverage for English source text.
- `test_ringcentral_all_qa_items_have_chinese_localized_questions_and_answers`
  - Assert every `package.qa` item has nonblank `localized_questions["zh"]` and nonblank `localized_answers["zh"]`.
  - Assert every Q&A still has at least one valid `related_entrypoint_ids` value.
- `test_ringcentral_package_owns_chinese_aliases_for_question_routes`
  - Assert package-owned aliases exist for the RingCentral ids currently covered only by `_ENTRYPOINT_ALIASES`, at
    minimum participants, audio, video, settings, recording, notes, reactions, raise hand, network quality, and
    meeting information.
  - Assert aliases are indexed through `package.entrypoint_question_aliases` with casefolded normalized values.

Add to `tests/unit/test_questions.py`:

- `test_ringcentral_chinese_questions_match_package_aliases_without_legacy_table`
  - Load the RingCentral package.
  - Monkeypatch `questions_module._ENTRYPOINT_ALIASES` to `{}`.
  - Ask Chinese questions for participants, audio, video, settings, recording, notes, reactions, raise hand, network,
    meeting info, chat, share, invite, background, and leave.
  - Assert each maps to the expected `entrypoint_id`.
- `test_ringcentral_localized_shared_screen_qa_returns_chinese_answer`
  - Ask the Chinese equivalent of "Can the presenter describe shared-screen content?" with
    `PresenterVoiceSettings(language="zh", tone="professional")`.
  - Assert `entrypoint_id == "ringcentral.video.toolbar.share"`, `can_operate is False`, and the answer is not the
    English fallback.
- `test_ringcentral_localized_invite_qa_returns_chinese_answer_and_stays_non_operable`
  - Ask the Chinese equivalent of "How can I bring people into the meeting?"
  - Assert `entrypoint_id == "ringcentral.video.toolbar.invite"` and `can_operate is False`.
- `test_ringcentral_concise_localized_qa_behavior_is_explicit`
  - Decide expected behavior before implementation.
  - If localized Q&A should remain fully authored, assert `tone="concise"` still returns the full localized answer.
  - If localized Q&A should mirror narration, update `_qa_answer_text()` to apply concise truncation and assert only
    the first sentence is returned.

Add to `tests/unit/test_voice.py`:

- `test_render_narration_text_uses_new_ringcentral_localized_flow_copy`
  - Load the package and pick one newly localized step from `meeting-controls-tour`.
  - Assert `render_narration_text(step.narration, PresenterVoiceSettings(language="zh"))` returns the `zh` script.
- `test_ringcentral_new_localized_narration_concise_uses_first_sentence`
  - Pick a newly localized multi-sentence step.
  - Assert `tone="concise"` returns only the first localized sentence.

No new `tests/unit/test_cli.py` tests are required for the first content-only slice. Add CLI tests only if the
implementation expands supported languages, supported tones, voice labels, or profile compatibility behavior.

## Risks And Guardrails

- Schema drift: because package models forbid extra fields, do not add new YAML keys for tone variants without a model
  update.
- Runtime fallback quality: non-localized Chinese entrypoint answers are not real translation. Add package-localized
  Q&A and aliases for user-facing quality, and prefer localized demo narration for scripted flows.
- Tone semantics: `localizedText` currently supports only language, not tone. The only localized narration tone effect
  is `concise` truncation.
- Q&A tone inconsistency: localized Q&A answers currently bypass all tone handling. Make that behavior explicit in
  tests before expanding content broadly.
- Alias collisions: short aliases such as "settings" or broad Chinese equivalents can route to the wrong entrypoint.
  Prefer specific aliases, rely on longest-alias matching, and add question tests for ambiguous areas.
- Legacy alias drift: package aliases take precedence, but the hard-coded legacy table can hide missing package data.
  The monkeypatch test above prevents accidental dependence on runtime fallback.
- Safety regression: risky route matching is English-token based. Do not rename ids/titles/purposes or remove words such
  as share, invite, leave, record, start, stop, toggle, mute, or unmute without retesting `can_operate`.
- Encoding: keep package/docs/tests UTF-8. Avoid asserting localized strings through legacy Windows console output;
  existing CLI voice catalog tests intentionally stay ASCII-safe.

## Implementation Order

1. Add focused failing tests in `test_material_packages.py`, `test_questions.py`, and `test_voice.py`.
2. Add package-owned `questionAliases.zh` for missing RingCentral question routes.
3. Add `localizedQuestions.zh` and `localizedAnswers.zh` to the two remaining Q&A items.
4. Add `localizedText.zh` to all steps in `vbg-blur-demo`, `meeting-basics-demo`, and `meeting-controls-tour`.
5. Re-run focused tests and adjust only package content unless tests expose a real runtime behavior decision.
6. Only consider model/runtime changes if the team explicitly requires per-tone localized copy or concise localized Q&A
   truncation.

## Verification Commands

Focused future implementation checks:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py tests\unit\test_questions.py tests\unit\test_voice.py
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_cli.py
.\.venv\Scripts\python -m ruff check --no-cache src\ai_presenter\packages src\ai_presenter\runtime tests\unit\test_material_packages.py tests\unit\test_questions.py tests\unit\test_voice.py tests\unit\test_cli.py
.\.venv\Scripts\python -m mypy --no-incremental src tests
git diff --check -- packages\ringcentral-video.yaml src\ai_presenter\runtime\questions.py src\ai_presenter\runtime\voice.py tests\unit\test_material_packages.py tests\unit\test_questions.py tests\unit\test_voice.py tests\unit\test_cli.py
```

Scan-only verification:

```powershell
git diff --check -- docs\agent-handoffs\cycle-022-technical-scan.md
git status --short -- docs\agent-handoffs\cycle-022-technical-scan.md
```

## Key Technical Recommendation

Make Cycle 022 a package-content expansion using the existing localized fields. Fill RingCentral Video's missing
Chinese scripts, Q&A localizations, and package-owned aliases first; add tests that prove the package no longer depends
on the legacy runtime alias table. Defer true per-tone localized copy until there is an explicit schema requirement.
