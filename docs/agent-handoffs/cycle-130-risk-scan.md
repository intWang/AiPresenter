# Cycle 130 Risk Scan: Spanish Q&A Output Quality

Date: 2026-05-16
Cycle: 130
Scope: risk scan only for improving Spanish Q&A output quality after Cycle129.
This file is the only intended edit for this task. Do not edit source code,
tests, package YAML, profiles, durable docs, generated artifacts, staging, or
commits from this scan.

## Executive Boundary

Cycle129 proved a limited runtime boundary: Spanish is runtime-selectable with
OpenAI-backed speech profiles, while Spanish local SAPI/Piper support and live
RingCentral acceptance remain unproven. Cycle130 should not broaden that claim.
The next improvement is narrower: make Spanish Q&A answers sound intentional,
complete, and safe when the Q&A matcher finds a package answer or an entrypoint.

Safe Cycle130 wording:

- Spanish Q&A output quality is being improved for authored RingCentral Video
  package answers and fallback entrypoint answers.
- Spanish runtime speech remains OpenAI-backed only.
- Spanish package localization can be complete while Q&A output still contains
  intentional product/control names such as RingCentral Video, Participants,
  Chat, Share, Settings, or Notes and Transcript.
- Live RingCentral Spanish acceptance remains unproven unless a dated run
  records profile, flow, provider, audio, UI state, and result.

Avoid wording such as "Spanish is fully localized", "Spanish is accepted",
"all RingCentral output is Spanish", or "live Spanish Q&A is validated" unless
separate evidence proves exactly that.

## Current Risk Surface

- `src/ai_presenter/runtime/questions.py`
  - Q&A matches use `localizedAnswers[voice.language]` when present.
  - No-match fallback has a Spanish string:
    `No encontre un control que coincida en el contexto activo de la app.`
  - Entrypoint fallback still builds `"{entrypoint.title}: {entrypoint.purpose}"`
    and then applies voice tone. For Spanish, this can produce mixed-language
    answers because entrypoint titles and purposes are English.
  - `can_operate` is guarded by `questionPolicy`, missing open steps, and risky
    words. That safety boundary must survive copy improvements.

- `packages/ringcentral-video.yaml`
  - Spanish package content is broad, but package YAML is the product knowledge
    source. Bulk edits here can accidentally change routing, safety policy,
    control behavior, or existing English/ZH/JA expectations.
  - Some Spanish package strings intentionally keep UI labels in English. That
    is not automatically a localization failure when the actual RingCentral UI
    label is English.

- `src/ai_presenter/packages/models.py`
  - Question normalization strips Latin diacritics, so accented and unaccented
    Spanish prompts should route the same way. Do not expand this into fuzzy
    semantic matching, stemming, transliteration, or cross-language matching.

## Specific Risks And Guardrails

### Accidental Overclaiming Of Full Localization

Risk: Spanish Q&A polish is described as full UI/application localization.

Guardrail: frame the work as Spanish Q&A copy quality and matcher behavior for
authored RingCentral Video material. Keep product names and observed UI labels
unchanged when they mirror the UI. Require evidence before claiming every
entrypoint, control, narration, error, diagnostic, CLI message, and live UI state
is Spanish.

### Editing Package YAML Without Review

Risk: improving copy by directly changing `packages/ringcentral-video.yaml`
without a review plan changes matcher behavior or safety policy under the cover
of localization polish.

Guardrail: treat package YAML edits as product-content changes, not mechanical
translation. Any package YAML change needs a focused diff review for
`questionPolicy`, `openSteps`, `relatedEntrypointIds`, risky controls,
localized questions, localized answers, and alias ordering. Do not combine broad
YAML edits with runtime/controller changes.

### Mixed-Language Entrypoint Fallback

Risk: Spanish questions that match an entrypoint but not an authored Q&A answer
return English `title: purpose` text. That can look like Spanish support failed
even though routing succeeded.

Guardrail: either add a Spanish-specific entrypoint answer path or add authored
Spanish Q&A for high-value prompts. Tests should distinguish acceptable English
UI labels from fallback English prose. If no Spanish copy exists, prefer an
honest Spanish fallback over machine-like mixed output.

### Safety Of Risky Controls

Risk: Spanish quality improvements make risky controls sound actionable, or
Spanish aliases route directly to operations for recording, invite, share,
mute/unmute, camera toggle, raise hand, leave, meeting info, notes/transcript,
or chat/participant privacy prompts.

Guardrail: Q&A-first safety answers must remain answer-only where appropriate.
`questionPolicy: answerOnly`, `_RISKY_ENTRYPOINT_WORDS`, and
`create_question_interrupt_step()` behavior should remain language invariant
unless a specific safer Spanish rule is added with tests.

### No-Match Fallback Copy Quality

Risk: the current Spanish no-match copy is functional but rough and
ASCII-only. Polishing it can accidentally remove the non-operable boundary or
introduce tone prefixes that sound like a live action was attempted.

Guardrail: no-match Spanish should be concise, natural, and explicitly scoped to
the active app context. It must keep `entrypoint_id is None`,
`can_operate is False`, and no interrupt step.

### Preserving English/ZH/JA Behavior

Risk: Spanish-specific normalization, aliases, or answer selection changes
regress existing English, Chinese, or Japanese routes.

Guardrail: keep `localizedAnswers` fallback behavior deterministic, preserve
existing package-owned alias precedence, preserve Chinese/Japanese safety Q&A,
and avoid global tokenization changes unless the full multilingual matcher
suite is updated.

### Avoiding Live Acceptance Claims

Risk: Q&A unit tests or dry-run controller tests are used as acceptance evidence
for live RingCentral behavior or real OpenAI audio quality.

Guardrail: unit tests may prove routing, copy selection, safety flags, and no
live provider construction. They do not prove live audio, live RingCentral UI
operation, or production acceptance.

## Must-Have Tests

Before accepting Cycle130 Spanish Q&A quality work, require focused tests for:

- Spanish authored Q&A answers: accented and unaccented Spanish prompts match
  the intended Q&A item and return `localizedAnswers.es`, not English fallback.
- Spanish entrypoint fallback: a Spanish alias that has no authored Q&A answer
  does not return raw English `title: purpose` prose unless that behavior is
  explicitly accepted and documented as UI-label-preserving.
- Spanish no-match fallback: unknown Spanish and English prompts with
  `voice.language == "es"` return polished Spanish copy, no English fallback,
  `entrypoint_id is None`, `can_operate is False`, and no interrupt step.
- Risky Spanish controls: recording, invite, share screen, mute/unmute, camera,
  raise hand/reactions, leave meeting, meeting information, notes/transcript,
  chat privacy, and participant-name prompts remain non-operable when the
  English/ZH/JA equivalents are non-operable.
- Accent folding: Spanish prompts with accents and without accents route the
  same way, without changing Chinese or Japanese normalization behavior.
- Entry-point alias precedence: package-owned aliases still beat legacy aliases,
  longest aliases still win, and equal-length aliases keep source order.
- English/ZH/JA regression coverage: existing tests for localized Chinese Q&A,
  Japanese safety questions, English privacy gates, and tone-invariant sensitive
  routing still pass.
- Controller question path: Spanish OpenAI `submit_question()` forwards
  `PresenterVoiceSettings(language="es")` and starts only safe
  `question-answer-demo` flows for operable matches.
- No live calls: Q&A and controller tests use fake runners/providers and do not
  construct real OpenAI clients or touch live RingCentral windows.

Suggested focused command:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py tests\unit\test_controller.py::test_presenter_controller_starts_spanish_openai_question_demo_when_idle tests\unit\test_controller_view_model.py::test_spanish_openai_view_model_is_startable_without_local_assets
```

Run broader guardrails before staging any implementation:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_voice.py tests\unit\test_cli.py tests\unit\test_diagnostics.py tests\unit\test_questions.py tests\unit\test_controller.py tests\unit\test_controller_view_model.py
git diff --check
git status --short
```

## No-Go Conditions

Do not accept Cycle130 Spanish Q&A work if any of these are true:

- The change claims full Spanish localization, live acceptance, or local
  SAPI/Piper Spanish support from Q&A tests.
- Package YAML is edited broadly without review of routing, safety policy,
  aliases, related entrypoints, and existing localized answers.
- Spanish entrypoint fallback still emits confusing English prose for common
  Spanish prompts and the implementation neither fixes nor explicitly documents
  that limitation.
- Any risky Spanish prompt becomes operable when its English/ZH/JA counterpart
  is answer-only or non-operable.
- No-match fallback can create an interrupt step, set `can_operate=True`, or
  imply the presenter attempted live UI operation.
- English, Chinese, or Japanese Q&A tests fail or are weakened to make Spanish
  pass.
- Tests require real OpenAI credentials, network access, live RingCentral UI, or
  live audio to prove ordinary Q&A copy quality.
- `doctor`, `voices`, `demo --dry-run`, or `controller --dry-run` output is used
  as live acceptance evidence.
- `.coverage` or unrelated worktree edits are staged as part of the scan.

## Review Notes For Implementers

Prefer the smallest copy-quality change that makes Spanish Q&A output honest:
authored Spanish answers for high-value prompts, or a localized entrypoint
fallback if the generic path is the problem. Keep safety separate from copy.
When a Spanish answer intentionally names English UI text, tests should assert
the surrounding prose is Spanish while the UI label remains unchanged.
