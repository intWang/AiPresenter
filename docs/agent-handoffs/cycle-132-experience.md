# Cycle 132 Experience Synthesis: Spanish Entrypoint Copy Pilot

Date: 2026-05-16
Cycle: 132
Scope: experience synthesis only. This file is the only intended edit from this
agent. Do not stage or commit.

## Product Lesson

Cycle132 turned the Cycle131 localized entrypoint display schema from unused
infrastructure into the first real Spanish user-facing RingCentral entrypoint
answers. The important product lesson is that a tiny, carefully chosen content
seed is more useful than another broad readiness claim: two natural Spanish
fallback answers expose the value, prove the pattern, and keep the safety surface
small enough to review.

The implemented pilot chose:

- `ringcentral.video.overview`
- `ringcentral.video.top.network-quality`

That choice favored passive/diagnostic surfaces over privacy-sensitive or
state-changing controls. It also preserved the visible truth of the product:
Spanish Q&A and narration are complete, Spanish aliases route most location
questions, but Spanish entrypoint title/purpose copy is only `2/27`.

## Pattern For Future RingCentral Additions

For each new localized entrypoint copy addition:

1. Add only display fields under the selected entrypoint:
   - `localizedTitles: { es: "..." }`
   - `localizedPurposes: { es: "..." }`
2. Do not change canonical `title`, `purpose`, `questionAliases`,
   `questionPolicy`, `openSteps`, cleanup behavior, presenter notes,
   `relatedEntrypointIds`, Q&A, or demo narration in the same content slice.
3. Keep `localizedTitles` and `localizedPurposes` out of matching, routing,
   alias expansion, diagnostics matching, safety gating, and controller
   interrupt creation.
4. Add exact package assertions for the localized title/purpose copy.
5. Update optional localization report count expectations only by the number of
   seeded entrypoints.
6. Add or reuse answer-rendering tests proving Spanish output uses localized
   title and purpose, while unseeded entrypoints still use the Spanish alias
   label plus canonical English purpose fallback.
7. Preserve Q&A-first behavior for privacy, safety, and state-changing prompts.

The Cycle132 tests now provide a template:

- `test_ringcentral_spanish_entrypoint_copy_pilot_is_present`
- `test_ringcentral_localization_status_reports_complete_spanish_package`
- `test_ringcentral_spanish_entrypoint_answer_uses_localized_pilot_copy`
- `test_ringcentral_spanish_unseeded_entrypoint_keeps_alias_label_fallback`
- `test_localization_report_outputs_complete_spanish_package`

## Spanish Copy Guardrails

Use neutral, Latin America-friendly Spanish. Keep localized purposes concise,
usually one sentence, and preserve visible RingCentral UI labels when the user
must find the same thing on screen.

Good patterns:

- Use "reunion" only if a file must stay ASCII; otherwise current package
  content already uses UTF-8 Spanish with accents.
- Use "panel", "barra superior", "barra de herramientas", "controles",
  "enlace", "cifrado", "transcripcion", and "revisar" naturally.
- Preserve visible labels such as `Network quality`, `Share`, `Chat`,
  `Participants`, `More`, `Meeting information`, `Meeting ID`, and
  `Notes and Transcript` when those are the UI labels the user must locate.
- Prefer bounded capability verbs such as "presenta", "abre", "muestra",
  "permite revisar", and "ayuda a confirmar".
- For diagnostics, describe observed metrics. Do not imply root-cause analysis.

Safety boundaries:

- Chat copy must not imply messages are read by default.
- Participants copy must not imply names, roles, or identities are read by
  default.
- Meeting information copy must not expose meeting IDs, links, dial-in details,
  host names, or encryption values by default.
- Notes/transcript copy must not imply starting notes, recording,
  transcription, summarization, or transcript reading.
- Recording, invite/link, leave, mute/camera, share, report, and
  participant-management copy should wait for focused safety tests.
- Do not use Spanish localized display copy to claim full localization,
  production readiness, local Spanish speech support, or live RingCentral
  acceptance.

## Claims Still Unproven

- Full Spanish entrypoint localization remains unproven: coverage is `2/27`,
  not `27/27`.
- Live RingCentral UI acceptance remains unproven by this cycle.
- Spanish audio/runtime behavior beyond the existing OpenAI-backed boundary
  remains unproven.
- Local Spanish SAPI/Piper support remains unproven.
- CLI `entrypoints --language` inspection was not implemented.
- Localized title/purpose copy remains display-only; no evidence supports using
  it as matcher input.
- Network quality copy does not prove that AiPresenter can diagnose or fix call
  instability; it only points users to diagnostic metrics.
- Unit tests do not prove live audio devices, real OpenAI credentials, network
  calls, or a live RingCentral window.

## Suggested Cycle133 Options

1. Add the next small Spanish entrypoint copy slice for one or two safe
   RingCentral controls, with safety tests first. Best candidates are still
   low-risk display or diagnostic surfaces. Use extra care before choosing
   `Chat` or `Participants`, and include explicit privacy wording if selected.
2. Add CLI `entrypoints --language` inspection as a read-only authoring aid.
   Keep default English output unchanged, accept package-local languages without
   runtime voice normalization, and avoid implying live operation safety.
3. Add a durable localization authoring doc for `localizedTitles` and
   `localizedPurposes`, including Spanish style, display-only semantics, report
   counts, and no-go examples.
4. Expand matcher-boundary and Q&A precedence tests around localized display
   copy, especially for phrases that appear only in localized title/purpose and
   should not route.
5. Defer full `27/27` Spanish entrypoint copy until several small slices have
   proven the review pattern on safe and then moderately sensitive surfaces.

## Verification Commands Worth Reusing

```powershell
.\.venv\Scripts\python.exe -m pytest tests\unit\test_material_packages.py tests\unit\test_questions.py tests\unit\test_cli.py -q --no-cov
```

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language es --require-complete
```

```powershell
.\.venv\Scripts\ruff check --no-cache packages tests
```

```powershell
rg -n "localizedTitles:|localizedPurposes:" packages\ringcentral-video.yaml
```

```powershell
git diff --check
git status --short
```

Expected Cycle132 signals to preserve unless Cycle133 intentionally changes
them:

- `localizedTitles.es present on 2/27 entrypoints`
- `localizedPurposes.es present on 2/27 entrypoints`
- `questionAliases.es present on 26/27 entrypoints (69 aliases)`
- Spanish required localization remains complete for demo narration and Q&A.
- `.coverage` may appear modified from prior verification and should not be
  staged as part of these handoff/content cycles.

## Current Diff Summary

At synthesis time, the worktree summary showed:

- `.coverage` modified.
- `packages/ringcentral-video.yaml` modified with four localized display fields.
- `tests/unit/test_cli.py` updated for `2/27` optional report counts.
- `tests/unit/test_material_packages.py` added package/count assertions.
- `tests/unit/test_questions.py` added localized rendering and unseeded fallback
  assertions.

No source, tests, packages, staging, or commits were changed by this synthesis
agent.
