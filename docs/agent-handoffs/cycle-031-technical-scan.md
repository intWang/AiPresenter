# Cycle 031 Technical Scan: Next Small AiPresenter Slice

Date: 2026-05-16
Role: technical discovery
Scope: review-only; no production code edits

## Recommendation

Implement **controller operator summary rows** next.

This is the best small technical slice among the three candidates because Cycle 005/Cycle 020 already created the pure controller view-model boundary, and the current Tk controller still renders that rich state as one long summary string. Splitting it into stable rows gives immediate live-operator value without changing RingCentral routes, question matching, provider behavior, or acceptance evidence.

The next implementation should be UI polish with a pure data seam:

- add a small row dataclass and `controller_operator_summary_rows(view_model)` helper in `src/ai_presenter/runtime/controller_view_model.py`;
- keep `render_controller_operator_summary()` for compatibility or implement it by joining the new rows;
- wire `run_controller()` in `src/ai_presenter/runtime/controller.py` to render the row values in a compact `LabelFrame` instead of a single packed label;
- keep button enablement, Start/Submit safety, voice readiness checks, and question flow behavior unchanged.

## Current State

The controller has the right data but not the right presentation:

- `src/ai_presenter/runtime/controller_view_model.py:22` defines `ControllerOperatorSnapshot`.
- `src/ai_presenter/runtime/controller_view_model.py:57` defines `ControllerOperatorViewModel` with source, target, flow, voice, voice-readiness, scan, run, question, buttons, and disabled reasons.
- `src/ai_presenter/runtime/controller_view_model.py:121` renders all of that into one string:
  `Source | Target | Flow | Voice | Voice assets | Scan | Question | Actions`.
- `src/ai_presenter/runtime/controller.py:557` stores this in one `operator_summary` `StringVar`.
- `src/ai_presenter/runtime/controller.py:616` sets the summary from the pure renderer.
- `src/ai_presenter/runtime/controller.py:863-864` places status and operator summary as two simple labels before the target controls.
- `tests/unit/test_controller_view_model.py` already covers readiness labels, disabled reasons, and summary behavior.

That means the next slice can be small: no new runtime policy and no new controller state machine.

## Expected Implementation Shape

1. Add row primitives in `controller_view_model.py`.

   Suggested shape:

   ```python
   @dataclass(frozen=True)
   class ControllerOperatorSummaryRow:
       key: str
       label: str
       value: str
   ```

   Then expose:

   ```python
   def controller_operator_summary_rows(
       view_model: ControllerOperatorViewModel,
   ) -> tuple[ControllerOperatorSummaryRow, ...]:
       ...
   ```

   Recommended rows:

   - `target`: `Target` -> `<source_label> | <target_label>`
   - `flow`: `Flow` -> `<flow_label or ->`
   - `voice`: `Voice` -> `<voice_label> | assets: <voice_readiness_label>`
   - `state`: `State` -> `<run_label> | scan: <scan_label>`
   - `question`: `Question` -> `<question_label>`
   - optional `actions`: `Actions` -> joined Start/Submit blocked reasons, only when at least one reason exists

   Keep labels short and stable so tests and future UI refinements can target them.

2. Preserve the existing string renderer.

   `render_controller_operator_summary()` is used by tests and currently by `run_controller()`. The least disruptive path is to reimplement it from the row helper, or keep it unchanged while adding row tests. If reimplemented, preserve the important substrings currently asserted by `test_render_operator_summary_includes_action_reasons_only_when_blocked`.

3. Wire Tk with a compact row panel.

   In `run_controller()`:

   - replace `operator_summary = tk.StringVar(...)` with a dict/list of row `StringVar`s;
   - create a small `LabelFrame(frame, text="Operator Summary", padx=8, pady=8)` after the status label;
   - render each row as label/value columns with `grid(sticky="w")`, giving the value column `weight=1`;
   - update the row variables inside `refresh_operator_view()`;
   - avoid nested card-like UI or a large redesign.

   Keep `root.geometry("720x500")` unless the row panel clearly needs a tiny height bump. The chat history can absorb the vertical space, so broad layout churn should not be necessary.

## Tests To Add Or Update

Primary tests:

- `tests/unit/test_controller_view_model.py`
  - add `test_operator_summary_rows_split_core_fields`;
  - add `test_operator_summary_rows_include_actions_only_when_blocked`;
  - assert row keys/labels are stable and values include target, flow, voice readiness, scan state, question state, and disabled action reasons.

Existing tests that should keep passing:

- `tests/unit/test_controller_view_model.py`
- `tests/unit/test_controller.py`

No new `PresenterController` runner test is needed for the narrow slice because runtime behavior should not change. If the implementation introduces a helper to initialize row variables, keep it pure enough to test without starting Tk.

## Verification Commands

RED for the new row helper before implementation:

```powershell
.\.venv\Scripts\python -m pytest tests\unit\test_controller_view_model.py::test_operator_summary_rows_split_core_fields tests\unit\test_controller_view_model.py::test_operator_summary_rows_include_actions_only_when_blocked --no-cov
```

Focused GREEN:

```powershell
.\.venv\Scripts\python -m pytest tests\unit\test_controller_view_model.py tests\unit\test_controller.py --no-cov
.\.venv\Scripts\python -m ruff check src\ai_presenter\runtime\controller_view_model.py src\ai_presenter\runtime\controller.py tests\unit\test_controller_view_model.py tests\unit\test_controller.py
.\.venv\Scripts\python -m mypy src\ai_presenter\runtime\controller_view_model.py src\ai_presenter\runtime\controller.py
```

Recommended smoke, if a human wants to inspect the UI without clicking RingCentral:

```powershell
.\.venv\Scripts\ai-presenter controller --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo
```

Do not run live RingCentral route actions as part of this slice unless a human explicitly asks for manual acceptance.

## Risks And Guardrails

- **Tk layout risk:** adding rows can shrink the chat history or make long values wrap poorly. Keep labels short, values left-aligned, and avoid making the controller taller unless necessary.
- **Runtime behavior drift:** this slice must not change `PresenterController`, `submit_question()`, `start()`, voice asset checking, or scan safety. It should only change how the already-built view model is displayed.
- **Overlong disabled reasons:** voice asset failure text can be long. The row value should tolerate long text better than the current one-line summary, but future visual QA may still be useful.
- **Test brittleness:** assert stable row keys and meaningful substrings, not the exact full joined summary string unless preserving backward compatibility.

## Candidate Comparison

### RingCentral Safety Presenter Skill

Value: useful and aligned with the user's skill-improvement goal, but less immediately verifiable than the controller UI slice.

Concrete implementation path:

- add `presenter/skills/ringcentral-safety.md`;
- add `src/ai_presenter/presenter/skills/ringcentral-safety.md` as the packaged copy because `pyproject.toml:43` includes `ai_presenter = ["profiles/*.yaml", "presenter/*.md", "presenter/skills/*.md"]`;
- add the skill to all RingCentral profiles that currently load `app-director.md` and `live-explainer.md`:
  - `profiles/ringcentral-video.yaml`
  - `profiles/ringcentral-video-bind-speaker.yaml`
  - `profiles/ringcentral-video-codex-cli-speaker.yaml`
  - `profiles/ringcentral-video-openai.example.yaml`
  - `profiles/ringcentral-video-piper-speaker.yaml`
  - `src/ai_presenter/profiles/ringcentral-video.yaml`
- update `tests/unit/test_config_loader.py` and `tests/unit/test_presenter_context.py` expectations;
- add an OpenAI or Codex CLI provider prompt assertion proving the new skill text is included.

Good source material:

- `docs/knowledge/ringcentral-video/privacy-matrix.md:5` default policy.
- `docs/knowledge/ringcentral-video/privacy-matrix.md:23-36` sensitive surfaces.
- `docs/knowledge/ringcentral-video/validation-checklist-index.md:32-37` Do Not Execute Yet recording/leave rows.
- `docs/knowledge/ringcentral-video/evidence-index.md:167` high-impact recording/leave risk.
- `packages/ringcentral-video.yaml` presenter notes and Q&A safety copy.

Risks:

- Behavior change is mainly prompt/context quality; unit tests can prove loading but not that model narration always follows it.
- There are duplicate root and packaged profile/skill files to keep in sync.
- Keep this as prompt discipline only; do not change route `can_operate` policy in the same slice.

Focused verification if this slice is chosen:

```powershell
.\.venv\Scripts\python -m pytest tests\unit\test_config_loader.py tests\unit\test_presenter_context.py tests\unit\test_openai_provider.py::test_narration_instructions_include_presenter_soul_and_memory tests\unit\test_codex_cli_provider.py::test_codex_cli_prompt_includes_presenter_soul_and_memory --no-cov
.\.venv\Scripts\python -m ruff check tests\unit\test_config_loader.py tests\unit\test_presenter_context.py tests\unit\test_openai_provider.py tests\unit\test_codex_cli_provider.py
.\.venv\Scripts\python -m mypy src\ai_presenter\runtime\presenter_context.py src\ai_presenter\config
```

### Q&A Matcher Performance Index

Value: real future performance hygiene, but lower urgency now because Cycle 008 already added validated entrypoint and package-owned alias indexes.

Current hot spots:

- `src/ai_presenter/runtime/questions.py:210` scans Q&A items and rebuilds localized question lists for each question.
- `src/ai_presenter/runtime/questions.py:239` rebuilds `_qa_questions(item)` each call.
- `src/ai_presenter/runtime/questions.py:253` still scores every entrypoint when alias matching misses.
- `src/ai_presenter/runtime/questions.py:313` tokenizes title/id/area/purpose on every fallback match.
- `src/ai_presenter/packages/models.py:103-105` already has private entrypoint, flow, and package alias indexes.

Potential implementation shape:

- add private `QuestionAnswerCandidate` records to `MaterialPackage` with original question text, normalized text, token set, and item index;
- add private `EntrypointMatchCandidate` records with precomputed title/id/area/purpose token sets;
- update `_match_qa()` and `_score_entrypoint_match()` to consume candidates instead of rebuilding strings/tokens;
- preserve Q&A-before-entrypoint precedence, localized answer behavior, longest alias precedence, package alias before legacy alias, and `can_operate` safety.

Risks:

- Subtle precedence regressions are more likely than with the controller row slice.
- Avoid wall-clock performance assertions; use structural tests for precomputed candidate fields and existing behavior regressions.
- Pydantic private index copy/revalidation caveats still matter; use `with_demo_flow()` or full validation when altering package shape.

Focused verification if this slice is chosen:

```powershell
.\.venv\Scripts\python -m pytest tests\unit\test_questions.py tests\unit\test_material_packages.py tests\unit\test_package_demo.py --no-cov
.\.venv\Scripts\python -m ruff check src\ai_presenter\runtime\questions.py src\ai_presenter\packages\models.py tests\unit\test_questions.py tests\unit\test_material_packages.py
.\.venv\Scripts\python -m mypy src\ai_presenter\runtime\questions.py src\ai_presenter\packages\models.py
```

## Verification Performed During This Scan

Existing focused checks all passed:

```powershell
.\.venv\Scripts\python -m pytest tests\unit\test_controller_view_model.py tests\unit\test_controller.py --no-cov
```

Result: `48 passed in 9.33s`.

```powershell
.\.venv\Scripts\python -m pytest tests\unit\test_presenter_context.py tests\unit\test_config_loader.py tests\unit\test_openai_provider.py::test_narration_instructions_include_presenter_soul_and_memory tests\unit\test_codex_cli_provider.py::test_codex_cli_prompt_includes_presenter_soul_and_memory --no-cov
```

Result: `28 passed in 3.29s`.

```powershell
.\.venv\Scripts\python -m pytest tests\unit\test_questions.py --no-cov
```

Result: `32 passed in 8.99s`.

## Commands Used

```powershell
git status --short
Get-ChildItem docs\agent-handoffs | Sort-Object Name | Select-Object -Last 20
rg -n "operator|summary rows|summary|controller|questionAliases|entrypoint|skill|matcher|match" src tests docs packages -S
rg -n "skillPaths:|app-director|live-explainer" profiles src\ai_presenter\profiles tests\unit\test_config_loader.py tests\unit\test_presenter_context.py
Select-String -Path src\ai_presenter\runtime\controller.py -Pattern "operator_summary|refresh_operator_view|ControllerOperatorSnapshot|render_controller_operator_summary" -Context 3,5
Select-String -Path src\ai_presenter\runtime\questions.py -Pattern "def _match_qa|def _match_entrypoint|def _score_entrypoint_match|def _can_operate" -Context 1,8
```

## Out Of Scope For The Next Slice

- No live RingCentralVideo automation.
- No acceptance evidence promotion or `acceptance-runs.md` update.
- No changes to question matching semantics or route safety.
- No broad Tk redesign, no new frontend, no screenshots required.
- No change to language/tone support.
