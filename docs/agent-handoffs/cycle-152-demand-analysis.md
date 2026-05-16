# Cycle 152 Demand Analysis: Empathetic Support Tone Alias

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`

## Decision

Recommendation: add `empathetic` as an alias for canonical tone `support`.
Do not add a new canonical tone in the next smallest product-valuable slice.
Do not switch away from tone work unless the cycle goal changes from tone
expansion to broader RingCentral Video localization or acceptance evidence.

Cycle151 completed the Spanish alias/display slice and explicitly kept tone
work separate. The deferred technical scan suggestion, `empathetic -> support`,
is now the best small follow-up because it expands the user-facing tone input
surface without creating a new behavior mode, provider route, package claim, or
RingCentral acceptance boundary.

## User Value

RingCentral Video demos often include recovery moments: audio does not connect,
screen sharing is unclear, a participant cannot find a control, a host needs to
explain recording consent, or a user asks a troubleshooting question while the
meeting surface is still visible. Operators naturally describe the desired
voice as empathetic in these moments. Today, the product already has the right
canonical behavior under `support`: calm, diagnostic, recovery-focused, and
reassuring. Adding `empathetic` lets users express that intent directly while
keeping output consistent with the existing support behavior.

This supports both user goals:

- It expands tone types in a meaningful way by increasing accepted tone
  vocabulary and `voices` discoverability.
- It optimizes AiPresenter for RingCentral Video by improving support and
  recovery phrasing for meeting-control demos without overclaiming live product
  readiness.

A new canonical `empathetic` tone is not the smallest valuable step. It would
need a new `PresenterTone` value, labels, descriptions, render behavior, CLI
catalog expectations, controller menu behavior, tests, and possibly localized
tone decisions. That extra surface is not justified until there is a distinct
behavior that differs from `support`.

Doing something else, such as another Spanish package-local smoke test, may be
useful later but is not the next product-valuable tone expansion. Cycle151
already handled the clearer Spanish alias gap, and the remaining deferred item
is a narrow tone alias that directly advances tone vocabulary.

## Recommended Minimum Scope

Implement an alias-only tone slice:

1. Add `empathetic` to the support-family aliases so it normalizes to canonical
   `support`.
2. Keep `tone_label("empathetic") == "Support"` through existing canonical
   normalization.
3. Keep `presenter_tone_description("empathetic")` returning the existing
   support description.
4. Ensure `ai-presenter voices` lists `empathetic` in the support alias catalog.
5. Add focused tests for runtime normalization, public alias ordering, and CLI
   catalog visibility.

Expected implementation footprint for the next worker:

- `src/ai_presenter/runtime/voice.py`
- `tests/unit/test_voice.py`
- `tests/unit/test_cli.py`

No package, profile, README, source outside runtime voice, or existing docs
need to change for this minimum slice.

## Why Not A New Canonical Tone

`support` already owns the behavior users would expect from an empathetic
RingCentral Video helper:

- recovery-oriented wording for troubleshooting;
- reassuring pacing for confusing meeting-control moments;
- slower Chinese SAPI rate behavior for support-like delivery;
- existing prompt description that already includes calm and reassuring traits;
- public aliases such as `supportive`, `helpdesk`, `troubleshooting`,
  `recovery`, `calm`, `steady`, and `reassuring`.

Promoting `empathetic` to canonical would create an artificial distinction
without a separate product promise. If future evidence shows users need a
non-troubleshooting emotional support mode, define that behavior first and then
consider a new canonical tone. This cycle should not invent that broader mode.

## Do Not Touch

- Do not edit `.coverage`.
- Do not revert or clean up other workers' changes.
- Do not add a new `PresenterTone` canonical value.
- Do not rename or split canonical `support`.
- Do not change provider routing, speech provider compatibility, SAPI/Piper
  behavior, OpenAI behavior, local asset checks, or profile YAML.
- Do not edit package YAML, RingCentral Video entrypoints, Q&A, localized copy,
  or acceptance evidence.
- Do not edit README or existing docs for this alias-only slice unless a future
  task explicitly asks for documentation changes.
- Do not claim live RingCentral Video acceptance, provider availability, audio
  quality validation, or meeting-control readiness from this alias work.
- Do not combine this with Spanish alias, runtime language, or localization
  work.

## Acceptance Criteria

The implementation is complete only when these repo-local contracts hold:

- `PresenterVoiceSettings(tone="empathetic").tone == "support"`.
- `tone_label("empathetic") == "Support"`.
- `presenter_tone_description("empathetic")` returns the existing support
  description.
- `presenter_tone_aliases("empathetic")` returns the support alias tuple and
  includes `empathetic` in stable order after the current support-family aliases.
- `ai-presenter voices` exits `0` and lists `empathetic` under support aliases.
- Existing expanded tone rendering remains unchanged: English support text still
  uses the support prefix, localized Japanese/Spanish text still avoids English
  prefixes, and Chinese support rate behavior remains as-is.
- Focused voice and CLI tests pass.
- `git diff --check` passes for the implementation files.
- Final diff excludes `.coverage`, packages, profiles, README, existing docs,
  and unrelated source or test files.

Suggested focused verification for the implementation worker:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_voice.py tests\unit\test_cli.py -k "expanded_tones or presenter_tone_aliases or voices_lists_language_tone_choices"
git diff --check -- src\ai_presenter\runtime\voice.py tests\unit\test_voice.py tests\unit\test_cli.py
git status --short
```

This demand-analysis document itself only requires document hygiene:

```powershell
rg -n "[ \t]+$" docs\agent-handoffs\cycle-152-demand-analysis.md
git diff --check -- docs\agent-handoffs\cycle-152-demand-analysis.md
```

## Implementation Handoff Prompt

```text
Cycle152 implementation task. You are not alone in the repo; do not revert
other workers' edits and do not touch `.coverage`.

Repository: C:\Users\rcadmin\Documents\Repos\AiPresenter

Goal: implement the smallest product-valuable tone expansion by adding
`empathetic` as an alias for canonical presenter tone `support`.

Read first:
- docs/agent-handoffs/cycle-152-demand-analysis.md
- docs/agent-handoffs/cycle-151-technical-scan.md
- docs/agent-handoffs/cycle-151-technical-development.md
- src/ai_presenter/runtime/voice.py
- tests/unit/test_voice.py
- tests/unit/test_cli.py around `voices`

Scope:
- Use a test-first alias-only change.
- Add `PresenterVoiceSettings(tone="empathetic").tone == "support"`.
- Extend the public support alias tuple so `presenter_tone_aliases("empathetic")`
  includes `empathetic` in stable order after the current support-family aliases.
- Extend the `voices` catalog test so `empathetic` appears in stdout.
- Implement the runtime change by adding `"empathetic": "support"` to
  `_TONE_ALIASES`, grouped with the other support aliases.

Do not:
- Add a new canonical tone.
- Change support tone rendering, descriptions, labels, provider routing, SAPI
  rates, profiles, package YAML, README, existing docs, or live RingCentral
  evidence.
- Combine this with Spanish alias, runtime language, localization, or acceptance
  work.
- Touch `.coverage`.

Acceptance:
- Focused tests pass:
  `$env:PYTHONDONTWRITEBYTECODE='1'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_voice.py tests\unit\test_cli.py -k "expanded_tones or presenter_tone_aliases or voices_lists_language_tone_choices"`
- `git diff --check -- src\ai_presenter\runtime\voice.py tests\unit\test_voice.py tests\unit\test_cli.py` passes.
- The final diff is limited to the expected runtime voice and focused test files.
```
