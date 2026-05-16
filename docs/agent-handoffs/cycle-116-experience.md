# Cycle 116 Experience Handoff: Alias Discipline And Evidence Boundaries

Date: 2026-05-16
Scope: experience synthesis only. This handoff creates only this file and does not edit production code, tests, package YAML, profiles, coverage artifacts, Codex home files, or git history.

## What Happened

Cycle 116 had four plausible directions:

- Add a tone alias that maps to an existing canonical tone.
- Add a new canonical tone.
- Complete or expand Spanish report-only package coverage.
- Enable Spanish as a runtime presenter language.

The implementation chose the smallest runtime-facing move: `executive`, `briefing`, and `boardroom` now normalize to the existing `formal` tone. That was the right experience call for this cycle because the user value was operator vocabulary, not a new behavior contract. The change improves the command surface without moving RingCentral safety policy, package localization, provider routing, controller readiness, or live acceptance claims.

The important implementation lesson is that the first exploratory red-test path, runtime Spanish, was product-adjacent but not cycle-safe. The handoffs made clear that Spanish was still partial package data: reportable through localization tooling, but not ready to be accepted as a runtime presenter language. Removing those exploratory tests before landing the tone alias kept the final diff honest.

## Choosing The Slice

Use a tone alias when the requested phrase is only a different way to ask for an existing style. `executive`, `briefing`, and `boardroom` fit under `formal`: polished, structured, business-ready. A tone alias should be visible in alias lists and CLI catalog output, but it should not change route matching, `can_operate`, interrupt behavior, provider selection, package content, or safety Q&A.

Use a new canonical tone only when the style is materially different from existing tones and needs its own durable label, description, tests, and controller/CLI behavior. That is a larger UX contract. It should include route-invariance checks so a style selection cannot become a policy selection by accident.

Use Spanish report-only work when the goal is package comprehension, localization metrics, or answer coverage without promising spoken Spanish runtime behavior. The demand handoff's Spanish Q&A completion slice remains valuable: it would make Spanish safety answers meaningful while keeping `localization-report --language es --require-complete` incomplete until demo narration is also ready.

Use Spanish runtime only when the runtime contract is ready end to end: `PresenterVoiceSettings(language="es")`, `voices`, `demo`, `doctor`, controller options, provider compatibility, no-match wording, package fallback behavior, and docs all need a coherent story. Current Spanish package coverage and voice readiness do not support that yet.

## Evidence Boundaries

Keep evidence labels narrow:

- Unit tests for tone aliases prove normalization, public alias metadata, and CLI catalog rendering.
- `localization-report` proves package localization coverage for a requested language; it does not prove runtime speech support.
- `localization-report --require-complete` is a completeness gate for required package coverage; Spanish should keep failing there until demo narration and Q&A coverage are intentionally complete.
- `voices` proves the public runtime language and tone catalog for the current build; in this cycle it should still list English, Chinese, and Japanese as runtime languages.
- `doctor` proves configured local diagnostics for the selected profile/package/flow; it is not live RingCentral acceptance.
- Live RingCentral acceptance requires dated manual or automated evidence against the current app route. This cycle did not add that evidence.

The README change is evidence-safe because it only documents an alias that now exists and normalizes to a current canonical tone. It does not claim Spanish runtime support, Spanish demo readiness, or live RingCentral validation.

## Avoiding Exploratory Test Drift

Exploratory red tests are useful when they reveal the true shape of the problem, but they should not remain in the tree unless they describe the chosen implementation contract. In this cycle, Spanish runtime tests helped confirm the risk, then had to be removed because the landed change was a tone alias, not a runtime-language expansion.

Good cycle hygiene here means:

- Keep failing tests only for the behavior being implemented in this slice.
- Remove speculative tests for deferred designs before the final green run.
- Do not add skipped or xfailed tests as placeholders for a future Spanish runtime unless the team explicitly wants a tracked design marker.
- Do not let a README or handoff say "Spanish supported" when the evidence only says "Spanish package coverage can be reported."
- Keep `.coverage` out of scope. If local test runs update it, leave it unstaged and do not reset it without an explicit owner request.

The focused test set in the implementation handoff matched the landed alias behavior: voice normalization, public alias metadata, and ASCII-safe CLI catalog output. That is the right size for an alias slice.

## Current Diff Read

The current textual diff matches the implementation handoff:

- `src/ai_presenter/runtime/voice.py` adds `executive`, `briefing`, and `boardroom` as aliases for `formal`.
- `tests/unit/test_voice.py` proves those aliases normalize to `formal` and are exposed through `presenter_tone_aliases()`.
- `tests/unit/test_cli.py` proves `executive` appears in `voices` output.
- `README.md` updates the tone-alias example to include `executive`.

The worktree also has a modified `.coverage` artifact. This experience handoff does not stage, delete, regenerate, or reset it.

## Guidance For The Next Agent

If the next user ask is tone vocabulary, first try to map it to an existing canonical tone. Prefer alias additions over canonical tone proliferation unless the desired style changes the generated instruction in a distinct way.

If the next user ask is Spanish support, ask which layer they mean. Spanish Q&A/report coverage is safe and narrow. Spanish runtime support is a larger compatibility slice and should not be inferred from package YAML alone.

If the next user ask is RingCentral evidence, name the evidence level before editing: unit, localization report, doctor, dry-run, manual acceptance, or live acceptance. That simple naming step prevents documentation from drifting beyond what was actually verified.

## Lightweight Validation For This Handoff

Commands run after creating this file:

```powershell
rg -n "[ \t]$" docs\agent-handoffs\cycle-116-experience.md
rg -n "TB[D]|TO[D]O|fill in detail[s]" docs\agent-handoffs\cycle-116-experience.md
git diff --check -- docs\agent-handoffs\cycle-116-experience.md
git ls-files --others --exclude-standard docs\agent-handoffs\cycle-116-experience.md
git status --short --untracked-files=all
```

Observed results:

- The trailing-whitespace scan found no matches.
- The placeholder scan found no matches.
- `git diff --check -- docs\agent-handoffs\cycle-116-experience.md` passed.
- `git ls-files --others --exclude-standard docs\agent-handoffs\cycle-116-experience.md` listed this handoff as an untracked new file.
- `git status --short --untracked-files=all` shows this new handoff plus pre-existing out-of-scope changes: `.coverage`, `README.md`, `src/ai_presenter/runtime/voice.py`, `tests/unit/test_cli.py`, `tests/unit/test_voice.py`, and the other Cycle 116 handoffs. Those files were left untouched by this experience subagent.
