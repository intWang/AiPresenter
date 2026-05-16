# Cycle 141 Risk Scan: Spanish Display Metadata Routing Guard

Date: 2026-05-17
Cycle: 141
Scope: risk scan for the candidate task to add a test/doc guard proving Spanish
`localizedTitles.es` and `localizedPurposes.es` remain display-only metadata and
do not alter question routing.

This scan owns only this handoff. Do not revert or normalize concurrent source,
test, package, docs, `.coverage`, or handoff edits made by others.

## Read Basis

- Project metadata: `pyproject.toml`
- Package data: `packages/ringcentral-video.yaml`
- Question matcher: `src/ai_presenter/runtime/questions.py`
- Package model and match-candidate construction:
  `src/ai_presenter/packages/models.py`
- Existing tests: `tests/unit/test_questions.py`,
  `tests/unit/test_material_packages.py`, and `tests/unit/test_cli.py`
- Durable docs: `docs/knowledge/language-lifecycle.md`,
  `docs/knowledge/ringcentral-video/source-index.md`, and
  `docs/knowledge/ringcentral-video/runtime-safety-routing.md`
- Recent handoffs: Cycle 140 risk, technical, and implementation handoffs

There is no root `package.json` in this checkout; the Python project metadata is
in `pyproject.toml`. Initial `git status --short` showed a pre-existing
modified `.coverage` artifact only. During verification, a concurrent
`tests/unit/test_questions.py` edit appeared with Spanish routing/display tests;
this scan did not modify or revert it.

## Current State Observed

- Spanish required package localization is complete for RingCentral Video:
  `51/51` demo steps, `12/12` localized Q&A questions, and `12/12` localized
  Q&A answers.
- Spanish package-owned query aliases remain the routing surface:
  `questionAliases.es` covers `26/27` entrypoints with `69` aliases.
- Optional Spanish display metadata is intentionally partial:
  `localizedTitles.es` and `localizedPurposes.es` are present on `8/27`
  entrypoints.
- `OperationEntrypoint.title_for_language()` and `purpose_for_language()` render
  localized display text for answers and CLI inspection.
- `MaterialPackage._build_entrypoint_match_candidates()` currently builds token
  candidates from canonical `id`, `title`, `area`, and `purpose` only. It does
  not include `localizedTitles` or `localizedPurposes`.
- Runtime question answering routes Q&A first, then package-owned
  `questionAliases`, then legacy aliases, then canonical token scoring.
- Existing tests already cover some of the boundary:
  `test_entrypoint_localized_title_and_purpose_do_not_affect_match_candidates()`
  verifies candidate tokens exclude localized title/purpose terms, and
  `test_localized_entrypoint_title_alone_does_not_create_a_match()` verifies a
  localized title alone does not route in a synthetic package.
- The notable guard gap is runtime matching for localized purpose-only text and
  a durable doc sentence that says localized titles/purposes are display-only,
  not query metadata.

## Risk: False Confidence

Risk: medium.

Count tests and answer-rendering tests can make this area look safer than it is.
They prove Spanish display metadata exists and renders, but they do not prove it
is absent from routing. The candidate guard should not rely only on:

- localization-report counts;
- `entrypoints --language es` output;
- answer text using localized labels after a route has already matched through
  an alias;
- durable docs saying `8/27` display metadata is present.

Those checks are useful, but they are not routing guards. A routing guard must
drive `answer_question()` against localized display text without aliases and
assert no `entrypoint_id`, no operation permission, and no interrupt.

## Risk: Overfitting To One Spanish Phrase

Risk: medium-high.

A single phrase such as `Donde esta el menu de camara?` is a poor sentinel for
this boundary because it already belongs to the curated Spanish alias path. It
would continue to route even if `localizedTitles` and `localizedPurposes` stayed
display-only.

Real RingCentral display strings also contain canonical routing tokens:

- `Menu de camara` overlaps canonical English title token `menu`.
- `Fondo desde More` contains `More`, which is already an area/control token.
- Background-related Spanish copy may include literal product labels such as
  `Background`, `Blur`, or `Settings`.

That means real-package negative probes can produce confusing results. A robust
test should use a tiny synthetic `MaterialPackage` with:

- no `questionAliases`;
- canonical `title`, `area`, and `purpose` that do not share tokens with the
  Spanish localized title or purpose;
- one localized title-only probe and one localized purpose-only probe;
- at least one unaccented Spanish probe to keep the Latin-diacritic normalizer
  boundary visible without depending on a real RingCentral alias.

Then a separate real-package positive test can continue to prove curated
`questionAliases.es` still route the intended RingCentral questions.

## Risk: Accidental Matching Expansion

Risk: high if source changes appear.

The candidate task should be a guard-hardening pass, not a matcher expansion.
No source change is expected. No package YAML change is expected.

No-go patterns:

- adding `localized_titles`, `localized_purposes`,
  `title_for_language("es")`, or `purpose_for_language("es")` to
  `_build_entrypoint_match_candidates()`;
- adding localized title/purpose strings to
  `entrypoint_question_aliases_by_match_order`;
- changing `_match_entrypoint_alias()`, `_match_package_entrypoint_alias()`, or
  `_score_entrypoint_match()` so localized display text becomes a route source;
- adding more Spanish aliases just to make or stabilize the guard;
- changing Q&A-first precedence, `questionPolicy`, `_can_operate()`, or
  interrupt creation;
- changing `packages/ringcentral-video.yaml` under this candidate task.

The safer invariant is: localized titles/purposes may alter answer labels and
CLI display output after a route is found, but they must not help find the route.

## Risk: Optional Metadata Treated As Required

Risk: medium.

`localizedTitles.es` and `localizedPurposes.es` are intentionally partial and
optional at `8/27`. The candidate doc guard should not accidentally promote
them into required localization.

No-go patterns:

- changing `--require-complete` to fail on missing `localizedTitles.es` or
  `localizedPurposes.es`;
- describing all Spanish entrypoint display metadata as complete;
- replacing required package localization counts with optional display counts;
- making `doctor --require-localization` require optional entrypoint title or
  purpose metadata;
- rewriting historical handoffs only to update old `5/27` or `8/27` snapshots.

Acceptable docs wording:

- Spanish required package localization is complete for demo narration and Q&A.
- Spanish package-owned aliases are query metadata.
- Spanish optional entrypoint display metadata remains partial at `8/27`.
- `localizedTitles` and `localizedPurposes` are display/inspection metadata,
  not route eligibility, alias coverage, or required-localization gates.

## Risk: Live And Runtime Overclaims

Risk: high around wording.

This guard can prove only local package/matcher behavior. It cannot prove live
RingCentral Video behavior or runtime voice readiness.

Do not claim:

- Spanish local SAPI support;
- Spanish Piper support;
- fake/local bind-speaker Spanish runtime readiness;
- virtual microphone or speaker routing in a live meeting;
- live RingCentral Video route acceptance;
- current-build locator reliability for `More`, audio menu, video menu,
  Background, Settings, or any privacy-sensitive surface;
- device switching, camera switching, Blur selection, or background privacy
  state.

The current runtime boundary remains: Spanish presenter output is supported only
through OpenAI-backed profiles, while local SAPI/Piper/fake/bind-speaker routes
must reject Spanish before runtime. Live RingCentral acceptance still requires a
separate dated acceptance run.

## Recommended Guard Shape

Implementation should be small and test/doc only.

Suggested test target:

- Add a synthetic runtime test in `tests/unit/test_questions.py` that creates an
  entrypoint with Spanish `localizedTitles` and `localizedPurposes`, no
  `questionAliases`, and no canonical token overlap.
- Parameterize at least:
  - a localized title-only Spanish prompt;
  - a localized purpose-only Spanish prompt;
  - an unaccented variant of one localized prompt.
- Assert `response.entrypoint_id is None`, `response.can_operate is False`, and
  `create_question_interrupt_step(package, response) is None` if session import
  boundaries make that convenient.
- Keep the existing candidate-token unit assertion in
  `tests/unit/test_material_packages.py`; extending it is fine, but it is not a
  substitute for the runtime `answer_question()` guard.

Suggested doc target:

- Add one explicit boundary sentence to
  `docs/knowledge/language-lifecycle.md` or
  `docs/knowledge/ringcentral-video/runtime-safety-routing.md`:
  `localizedTitles` and `localizedPurposes` are display/inspection metadata and
  must not be treated as query aliases, route candidates, operation permission,
  or required-localization gates.

Do not touch package YAML, source matcher code, provider code, profiles, live
acceptance docs, or historical handoffs for this candidate.

## Verification To Require

Focused tests:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py::test_localized_entrypoint_title_alone_does_not_create_a_match
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_entrypoint_localized_title_and_purpose_do_not_affect_match_candidates
```

After the new test name exists, run it directly with the two existing sentinels.

Recommended focused regression set:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py tests\unit\test_material_packages.py::test_entrypoint_localized_title_and_purpose_do_not_affect_match_candidates tests\unit\test_cli.py::test_localization_report_outputs_complete_spanish_package tests\unit\test_cli.py::test_localization_report_require_complete_passes_for_spanish_package
.\.venv\Scripts\ruff.exe check --no-cache tests\unit\test_questions.py tests\unit\test_material_packages.py tests\unit\test_cli.py
git diff --check
git status --short
```

Expected status after implementation: only the focused test/doc files changed,
plus the pre-existing `.coverage` artifact if it remains dirty. Source code,
`packages/ringcentral-video.yaml`, profiles, and runtime docs outside the
chosen boundary doc should stay untouched.

## Go/No-Go Recommendation

Go, with tight constraints.

This is a good Cycle141 task if it adds a narrow synthetic runtime guard and one
durable boundary sentence while leaving source code and package YAML untouched.
It reduces the exact risk created by recent Spanish display-copy expansion:
future agents can see that localized entrypoint display copy is allowed to
render, but not allowed to route.

No-go if the task expands matching behavior, adds aliases, changes package
counts, makes optional display metadata required, edits provider/runtime voice
selection, or claims live RingCentral acceptance. No-go if the guard only tests
one real Spanish phrase that already routes through curated aliases or canonical
tokens.
