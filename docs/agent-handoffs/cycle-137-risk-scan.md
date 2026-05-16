# Cycle 137 Risk Scan: Spanish Runtime And Docs Overclaim Boundaries

Date: 2026-05-16
Cycle: 137
Scope: risk scan only for the next small optimization. This handoff is the
only intended edit. Do not change source, tests, package YAML, durable docs,
generated artifacts, staging, commits, or `.coverage` in this scan.

## Baseline Read

Current Spanish state is narrow and easy to overstate:

- Required Spanish package localization is complete for required RingCentral
  Video demo narration and Q&A: `51/51` demo steps, `12/12` Q&A questions, and
  `12/12` Q&A answers.
- Spanish package-owned query aliases are broad enough for curated location
  routing: `questionAliases.es` covers `26/27` entrypoints with `69` aliases.
- Optional Spanish entrypoint display metadata remains partial, not complete:
  `localizedTitles.es` and `localizedPurposes.es` are present on `5/27`
  entrypoints.
- Runtime Spanish is supported only through OpenAI-backed speech profiles, such
  as `profiles/ringcentral-video-openai.example.yaml`.
- Fake, local Windows SAPI, local Piper, `windows-sapi-en`, and
  `windows-sapi-zh` routes must still reject Spanish before runtime.
- Spanish local SAPI/Piper support and live RingCentral Video Spanish
  acceptance remain unproven until a separate implementation and dated
  acceptance run prove them.

README currently has reasonable boundary wording:

- It says Spanish package localization is complete.
- It says `--language es` is runtime-selectable only with OpenAI-backed speech
  profiles.
- It says local SAPI and Piper routes do not support Spanish yet.
- It says Spanish output requires OpenAI-backed speech.

Most durable docs also preserve the boundary. One date-sensitive risk is
`docs/knowledge/ringcentral-video/runtime-safety-routing.md`, which says
current package signals were "verified on 2026-05-17". For this handoff, the
required date baseline is 2026-05-16. Treat that future date as suspect wording
unless a later cycle has real dated evidence.

## Recommended Safe Scope

Safest next optimization: docs wording polish only, focused on preventing
overclaims.

Recommended slice:

- Clarify README or durable docs where a reader might confuse package
  localization with runtime voice support.
- If correcting the future verification date, change only the date wording and
  keep the evidence claim scoped to commands actually run on 2026-05-16.
- Prefer wording that says Spanish required package localization is complete
  while optional entrypoint display metadata remains partial at `5/27`.
- Keep OpenAI-backed Spanish runtime support separate from local SAPI/Piper
  support and from live RingCentral acceptance.
- Keep `entrypoints --language es` described as package-local display metadata
  inspection only.

Acceptable alternate small scope:

- Add a README example for:

```powershell
.\.venv\Scripts\ai-presenter.exe entrypoints --package ringcentral-video --language es
```

- The text around it must say it inspects package-local localized/fallback
  entrypoint display copy.
- It must also say it does not validate runtime voice support, local voice
  assets, provider readiness, controller behavior, or live RingCentral
  acceptance.

## Explicit No-Go Areas

Do not include any of the following in a small docs optimization:

- Runtime provider expansion for Spanish local SAPI or Piper.
- Any claim that Spanish works with local voice routes.
- Any claim that OpenAI-backed Spanish runtime support proves live RingCentral
  Spanish demo readiness.
- Any live acceptance-run entry unless a real current manual or automated run
  was performed and recorded with date, environment, route, commands or manual
  steps, and result.
- Changes to `validate_profile_voice`, provider resolution, voice catalog,
  doctor runtime language semantics, controller language options, or demo
  launch behavior.
- Changes to Q&A matching, alias precedence, localized metadata matching,
  safety gating, or interrupt creation.
- Changing `--require-complete` to include optional `localizedTitles.es` or
  `localizedPurposes.es`.
- Broad Spanish alias expansion, especially for action, content-reading,
  recording, notes/transcript, participants, invite, chat, share, reaction, hand
  raise, mic, camera, or leave/end prompts.
- Staging, committing, deleting, regenerating, or touching `.coverage`.

## Wording Risks

### README Compression

Risk: medium-high. README is where precise lifecycle language can get shortened
into an overclaim.

Avoid:

- "Spanish is fully localized."
- "Spanish works locally."
- "Spanish voice support is complete."
- "Spanish live demo is ready."
- "Spanish RingCentral acceptance passed."
- "All Spanish entrypoints are localized."

Prefer:

- "Spanish required package localization is complete for demo narration and
  Q&A."
- "Spanish optional entrypoint display metadata remains partial at `5/27`."
- "Spanish runtime speech requires an OpenAI-backed profile."
- "Local SAPI/Piper Spanish support remains future work."
- "Live RingCentral Spanish acceptance requires dated evidence."

### Verification Dates

Risk: medium. A future date can imply newer verification than actually exists.
The next docs owner should review any `2026-05-17` verification wording against
the requested 2026-05-16 baseline. If there is no real 2026-05-17 acceptance or
test run to cite, avoid using that date as proof.

Safe correction patterns:

- "Current expected package signals, documented as of 2026-05-16..."
- "Expected package signals..."
- "Current expected package signals, verified by the cycle's listed commands..."

Do not replace a future date with a false claim that every listed command was
rerun unless the next owner actually reruns those commands.

### Runtime Voice And Local Support

Risk: high. OpenAI-backed Spanish runtime support is real but limited. It must
not be described as:

- local SAPI readiness;
- Piper model readiness;
- fake-provider support;
- installed voice asset support;
- offline support;
- live RingCentral acceptance.

Local profiles should continue to fail Spanish runtime checks with a profile
voice compatibility error. Any docs change that suggests otherwise needs a
runtime implementation cycle, voice/provider tests, and explicit profile setup
instructions.

### Live RingCentral Acceptance

Risk: high. Runbooks and checklists are procedure, not proof. Spanish package
coverage and OpenAI dry-run behavior do not prove live RingCentral audio,
virtual microphone routing, UI locator behavior, panel cleanup, or meeting
state safety.

Any acceptance claim must cite a dated record in
`docs/knowledge/ringcentral-video/acceptance-runs.md` and include the current
RingCentral build, locale, DPI/window bounds when relevant, profile, language,
speech route, flow or route, and pass/fail result.

## Required Verification

For README or durable-doc wording only:

```powershell
rg -n "Spanish|es|OpenAI|SAPI|Piper|live acceptance|runtime-selectable|runtime language|2026-05-17|2026-05-16" README.md docs\knowledge docs\runbooks
git diff --check
git status --short
```

Expected status: only the intended docs file should be modified, plus any
pre-existing `.coverage` modification left untouched and unstaged.

For changing the future date or verification wording:

```powershell
rg -n "2026-05-17|verified on|Current expected package signals" docs\knowledge docs\runbooks README.md
git diff --check
git status --short
```

For adding a README `entrypoints --language es` example:

```powershell
.\.venv\Scripts\ai-presenter.exe entrypoints --package ringcentral-video --language es
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_cli.py::test_entrypoints_language_inspects_ringcentral_localized_and_fallback_copy tests\unit\test_cli.py::test_entrypoints_language_uses_package_local_metadata_without_runtime_voice_validation tests\unit\test_cli.py::test_localization_report_outputs_complete_spanish_package
git diff --check
git status --short
```

For any runtime language, provider, doctor, demo, or controller behavior change,
this risk scan is not enough. The next owner must add focused tests first and at
minimum run the Spanish OpenAI-positive and local-profile-negative CLI tests,
voice tests, diagnostics tests, and the relevant dry-run commands.

## Residual Risks

- Spanish optional entrypoint display metadata remains partial at `5/27`, so
  docs must keep distinguishing required package localization from complete
  entrypoint display localization.
- Spanish aliases and Q&A prompts cover curated package knowledge, not general
  semantic Spanish action understanding.
- OpenAI-backed Spanish runtime support depends on configured OpenAI profile
  behavior and does not prove local audio device routing in RingCentral.
- Live RingCentral route behavior remains mostly unaccepted for current builds,
  especially panel cleanup, More-menu ordering, media controls, share, notes,
  recording, reactions, raise hand, invite, chat, and participants surfaces.
- A date-only docs fix can make the prose less misleading, but it is not new
  verification evidence.
- `.coverage` is already modified in the worktree during this scan. Leave it
  unmodified and unstaged.

## Recommendation

Use Cycle 137 for a tiny docs-boundary correction: either fix the future-dated
verification wording or add a README package-local `entrypoints --language es`
inspection example with explicit caveats. Do not combine that with runtime
Spanish provider work, local voice support, package alias expansion, or live
RingCentral acceptance claims.
