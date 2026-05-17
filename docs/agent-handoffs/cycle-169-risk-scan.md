# Cycle 169 Risk/Test Scan: Full-Screen Views Routing

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`
Latest inspected commit: `62929a1`
Role: Cycle169 risk/test-scan subagent

## Scope

- Reviewed the two candidate slices from repo evidence: full-screen/views routing and Meeting information encryption-status Q&A.
- Chose full-screen/views routing as the safer and higher-value Cycle169 target.
- Wrote only this handoff: `docs/agent-handoffs/cycle-169-risk-scan.md`.
- Did not edit code, tests, package YAML, staging, commits, or `.coverage`.
- Did not run the full suite. Used read-only `git`, `rg`, file reads, and tiny no-bytecode routing/diagnostic probes.
- Current dirty file observed before this scan: `.coverage`; leave it untouched.
- Final status also showed concurrent work in `packages/ringcentral-video.yaml`, `tests/unit/test_cli.py`, `tests/unit/test_diagnostics.py`, `tests/unit/test_questions.py`, and untracked `docs/agent-handoffs/cycle-169-demand-analysis.md`. I did not edit, revert, or validate those files.

## Why This Slice

Full-screen/views routing is safer than encryption-status Q&A because it should only open the local `Views` layout menu. It does not read or summarize private meeting metadata.

It is also higher value in the current tree because `packages/ringcentral-video.yaml` already has English full-screen aliases under `ringcentral.video.top.views`, and `tests/unit/test_questions.py` already asserts four full-screen prompts route to the Views menu. Current routing still leaves common variants such as `Go full screen` and `Enter full screen mode` falling to Screen sharing, and current diagnostics probes report alias counts that differ from existing test expectation strings.

Encryption-status Q&A remains valid backlog, but it is privacy-sensitive and already has Cycle168 demand/risk coverage. Do not mix it with this layout-routing slice.

## Current Evidence

Current no-bytecode route probe at `62929a1`:

| Prompt | Current route | `can_operate` | Interrupt | Notes |
| --- | --- | --- | --- | --- |
| `Show full screen` | `ringcentral.video.top.views` | `True` | yes | Covered by current unit test. |
| `Switch to full screen` | `ringcentral.video.top.views` | `True` | yes | Covered by current unit test. |
| `Where is full screen?` | `ringcentral.video.top.views` | `True` | yes | Covered by current unit test. |
| `Full screen view` | `ringcentral.video.top.views` | `True` | yes | Covered by current unit test. |
| `Go full screen` | `ringcentral.video.toolbar.share` | `False` | no | Wrong surface; Share steals the `screen` token. |
| `Enter full screen mode` | `ringcentral.video.toolbar.share` | `False` | no | Wrong surface; Share steals the `screen` token. |
| `Share screen` | `ringcentral.video.toolbar.share` | `False` | no | Correct negative control. |
| `Can you share system audio?` | `ringcentral.video.toolbar.share` | `False` | no | Correct screen-sharing safety Q&A. |

Current diagnostics probe:

- Package-owned aliases: `161`.
- Q&A question prompts: `178`.
- Q&A alias overlaps: `178`.
- Q&A alias substring-risk prompts: `11`.

## Risk Matrix

| Risk | Likelihood | Impact | Recommended guard |
| --- | --- | --- | --- |
| Full-screen prompts regress to Screen sharing | Medium | Medium | Assert representative full-screen prompts route to `ringcentral.video.top.views` and reject `Screen sharing:` answer text. |
| Broad `screen` alias steals screen-share safety prompts | High if broad alias is added | High | Do not add `screen`, `show screen`, `share screen`, `display`, or other generic screen aliases. Keep controls for Share prompts. |
| Imperative full-screen wording implies the layout changed | Medium | Medium | Answer copy should say `View layout menu:` and tests should reject completed-action claims such as `switched`, `entered full screen`, or `full screen is on`. |
| Question interrupt opens more than the Views menu | Low/Medium | High | Assert the entrypoint has one `clickWindowRelative` open step targeting `Views` with `cleanup: escape`; do not add steps that select `Full screen`. |
| Coordinate route is repo-tested but not live-accepted | Medium | Medium | Keep route tests focused, then require manual bounds/DPI validation before promoting acceptance evidence. |
| Diagnostics/doctor count strings stay stale | High in current tree | Medium | Recompute counts after final alias inventory; current probe says `161` aliases, `178` Q&A prompts, `11` substring-risk prompts. |
| Full-screen slice mixes with encryption/security Q&A | Medium | High | Do not edit Meeting information Q&A, host/security Q&A, `questionPolicy`, or runtime matchers in this slice. |
| Localized aliases are added without localization strategy | Low/Medium | Medium | Keep Cycle169 English-only unless explicit localized prompts and tests are added together. |

## Recommended Assertions

For current positive controls and any added full-screen variants:

```python
assert response.entrypoint_id == "ringcentral.video.top.views"
assert response.entrypoint_id != "ringcentral.video.toolbar.share"
assert response.can_operate is True
assert create_question_interrupt_step(package, response) is not None
assert response.answer_text.startswith("View layout menu:")
assert "Screen sharing:" not in response.answer_text
```

For state-change restraint:

```python
lowered = response.answer_text.casefold()
assert "entered full screen" not in lowered
assert "switched to full screen" not in lowered
assert "full screen is on" not in lowered
assert "changed your layout" not in lowered
```

For the entrypoint itself:

```python
entrypoint = package.entrypoint_by_id("ringcentral.video.top.views")
assert entrypoint.question_policy != "answerOnly"
assert len(entrypoint.open_steps) == 1
assert entrypoint.open_steps[0].target == "Views"
assert entrypoint.open_steps[0].match.cleanup == "escape"
```

If the goal is to close the remaining observed gap, add `Go full screen` and `Enter full screen mode` to the focused test. Decide whether to add two exact aliases or replace the four exact aliases with one narrow `full screen` alias; do not add generic screen aliases.

## Positive Controls

- `Show full screen`
- `Switch to full screen`
- `Where is full screen?`
- `Full screen view`
- `Go full screen` if included in the final slice
- `Enter full screen mode` if included in the final slice
- `Switch to gallery view`
- `Change meeting layout`

All should route to `ringcentral.video.top.views`, open only the Views menu, and avoid saying the Full screen option was selected.

## Negative Controls

- `Share screen`, `Share my screen`, `Can you describe what's on screen?`, `Can you share system audio?`, and `Share computer audio` should remain screen-sharing safety responses, non-operable, with no interrupt.
- `meeting information`, `where is the meeting ID`, and `where is the meeting link` should remain Meeting information answer-only lookups.
- `What is the encryption status?`, `Is this meeting encrypted?`, `Read the encryption details`, and `Copy the encryption details` should stay outside this slice.
- `Participants`, `Background settings`, `Where are captions?`, and recording prompts should keep their existing routes.
- Host/security prompts from Cycle168 should remain under participant host-control Q&A and should not become Views or Share prompts.

## Diagnostics Count Guidance

Use the final package inventory, not stale baseline numbers:

- Current observed package-owned aliases at `62929a1`: `161`.
- Current observed Q&A question prompts: `178`.
- Current observed Q&A alias-overlap prompts: `178`.
- Current observed Q&A alias substring-risk prompts: `11`.

Expected movements:

- Keeping the current four full-screen aliases means diagnostics/doctor tests should expect `161 package-owned aliases`.
- Replacing those four exact aliases with one narrow `full screen` alias would move alias count to `158`.
- Adding `Go full screen` and `Enter full screen mode` as exact aliases on top of the current four would move alias count to `163`.
- Adding only tests for already-routing prompts should not change any count.
- This slice should not change Q&A prompt totals. If Meeting information encryption prompts are added separately, `178 -> 185` for the seven-prompt encryption set, but that is out of scope here.

Update count assertions together in:

- `tests/unit/test_diagnostics.py::test_diagnostics_reports_question_aliases_ok_for_ringcentral_package`
- `tests/unit/test_cli.py::test_doctor_loads_profile_package_and_flow`

Keep `qa questions`, `qa alias overlap`, and `qa alias substring risk` strings unchanged unless diagnostics output changes after the final alias inventory is loaded.

## Final Verification Checklist

- Confirm full-screen aliases live only under `ringcentral.video.top.views`.
- Confirm no generic `screen` alias was added.
- Confirm `ringcentral.video.toolbar.share` keeps screen-sharing safety Q&A precedence.
- Confirm `Go full screen` and `Enter full screen mode` are either intentionally covered or intentionally left as known fallback gaps.
- Confirm the interrupt opens only the Views menu and does not select Full screen.
- Confirm no Meeting information encryption/status Q&A, host/security Q&A, runtime matcher, or `questionPolicy` change is mixed into this slice.
- Confirm diagnostics/doctor alias counts match the actual final inventory.
- Run focused verification only, with coverage and pytest cache disabled:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py::test_ringcentral_full_screen_questions_route_to_view_layout tests\unit\test_questions.py::test_ringcentral_english_screen_sharing_questions_stay_qa_first
```

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_diagnostics.py::test_diagnostics_reports_question_aliases_ok_for_ringcentral_package tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_questions_ok_for_ringcentral_package tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_alias_overlap_ok_for_ringcentral_package tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_alias_substring_info_for_ringcentral_package tests\unit\test_cli.py::test_doctor_loads_profile_package_and_flow
```

- Run `git diff --check` on touched files before staging in any implementation pass.
- Run `git status --short` and keep `.coverage` unstaged.
- Do not run the full suite unless the coordinator explicitly asks.
