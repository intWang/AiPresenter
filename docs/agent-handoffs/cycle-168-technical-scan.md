# Cycle 168 Technical Scan: RingCentral Video Full-Screen Layout Prompt

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`
Head inspected: `20de0da`

## Guardrails

This was a scan-only pass. I did not edit source, package YAML, tests, staging,
commits, or `.coverage`. The only intended write from this subagent is this
handoff file.

Initial `git status --short` showed `.coverage` modified. During the scan,
another worker added RingCentral Video security/lock Q&A edits in:

- `packages/ringcentral-video.yaml`
- `tests/unit/test_questions.py`
- `tests/unit/test_diagnostics.py`
- `tests/unit/test_cli.py`

I left those changes untouched. Current count notes below distinguish the clean
`20de0da` baseline from the in-progress dirty worktree where useful.

## Recommended Safe Target

Add a narrow English package-owned alias for `full screen` to the existing
`ringcentral.video.top.views` entrypoint.

This fixes a small layout routing gap outside the recent caption/privacy work:
full-screen prompts currently route to Screen sharing even though the package
models Full screen under the Views layout menu.

## Current Probe Results

Read-only probe path: load `packages/ringcentral-video.yaml`, call
`answer_question(...)`, then check `create_question_interrupt_step(...)`.

| Prompt | Current route | `can_operate` | Interrupt | Issue |
| --- | --- | --- | --- | --- |
| `Show full screen` | `ringcentral.video.toolbar.share` | `False` | no | Wrong surface: returns Screen sharing text. |
| `Go full screen` | `ringcentral.video.toolbar.share` | `False` | no | Wrong surface: returns Screen sharing text. |
| `Where is full screen?` | `ringcentral.video.toolbar.share` | `False` | no | Wrong surface for a layout lookup. |
| `Enter full screen mode` | `ringcentral.video.toolbar.share` | `False` | no | Wrong surface: Share steals the `screen` token. |
| `Switch to gallery view` | `ringcentral.video.top.views` | `True` | yes | Existing layout route works. |
| `Change meeting layout` | `ringcentral.video.top.views` | `True` | yes | Existing layout route works. |

The current behavior is not dangerous, because Share remains non-operable from
questions, but it gives the wrong guidance for a normal layout request.

## Exact Package Edit

In `packages/ringcentral-video.yaml`, under
`ringcentral.video.top.views`, add one English alias:

```yaml
  questionAliases:
    en:
    - full screen
    es:
    - menu de vista de reunion
```

Do not add broad aliases such as `screen`, `show screen`, `display`, or
`fullscreen share`. The point is to beat the Share token match only for the
specific local-layout phrase.

In-memory simulation with only this alias added routes these prompts to Views:

- `Show full screen`
- `Go full screen`
- `Where is full screen?`
- `Enter full screen mode`

Expected route for each: `entrypoint_id ==
"ringcentral.video.top.views"`, `can_operate is True`, and an interrupt step is
created for opening the Views popover. The route should not click Full screen
itself; it only opens the layout menu, which already has `cleanup: escape`.

## Exact Test Edits

Add a focused test in `tests/unit/test_questions.py`, near the other
RingCentral routing tests:

```python
@pytest.mark.parametrize(
    "question",
    [
        "Show full screen",
        "Go full screen",
        "Where is full screen?",
        "Enter full screen mode",
    ],
)
def test_ringcentral_full_screen_prompts_route_to_view_layout(question: str) -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    response = answer_question(
        package=package,
        question=question,
        voice=PresenterVoiceSettings(),
    )

    assert response.entrypoint_id == "ringcentral.video.top.views"
    assert response.can_operate is True
    assert create_question_interrupt_step(package, response) is not None
    assert response.answer_text.startswith("View layout menu:")
    assert "Screen sharing:" not in response.answer_text
```

Update alias-count expectations:

- `tests/unit/test_diagnostics.py::test_diagnostics_reports_question_aliases_ok_for_ringcentral_package`
  from `157 package-owned aliases...` to `158 package-owned aliases...`.
- `tests/unit/test_cli.py::test_doctor_loads_profile_package_and_flow`
  from `157 package-owned aliases...` to `158 package-owned aliases...`.

Do not update Q&A prompt count expectations for this full-screen slice. It adds
one entrypoint alias, not a Q&A prompt.

## Count Impact

Clean `20de0da` baseline:

- Package-owned aliases: `157 -> 158`
- Q&A question prompts: stays `173`
- Q&A alias overlap count: stays `173`
- Q&A alias substring risk: expected to stay `11`

Current dirty worktree with the concurrent security/lock Q&A edits:

- Package-owned aliases: `157 -> 158`
- Q&A question prompts: stays `178`
- Q&A alias overlap count: stays `178`
- Q&A alias substring risk: observed to stay `11`

In-memory diagnostics after adding only `full screen` to the current dirty
worktree:

```text
question aliases OK 158 package-owned aliases have no cross-entrypoint duplicates
qa questions OK 178 Q&A question prompts have no cross-item duplicates
qa alias overlap OK 178 Q&A question prompts have no unsafe package-owned alias overlaps
qa alias substring risk INFO 11 Q&A question prompts contain package-owned alias substrings outside related entrypoints
```

## Risks

- Adding `screen` as a broad alias would steal legitimate screen-sharing
  prompts. Use only `full screen`.
- The route becomes operable because Views is already operable from questions.
  That should only open the Views menu and then clean up with Escape; it must
  not click the Full screen item or claim the layout changed.
- This is package-routing evidence only. It does not prove live RingCentral
  Video layout behavior, current coordinate reliability, or fullscreen state.
- Reconcile the concurrent security/lock Q&A edits before committing. Do not
  overwrite them and do not mechanically reset Q&A counts back to the clean
  baseline if those edits remain.

## Verification Commands

After implementation, use cache/coverage-light focused checks:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py::test_ringcentral_full_screen_prompts_route_to_view_layout
```

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_diagnostics.py::test_diagnostics_reports_question_aliases_ok_for_ringcentral_package tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_questions_ok_for_ringcentral_package tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_alias_overlap_ok_for_ringcentral_package tests\unit\test_cli.py::test_doctor_loads_profile_package_and_flow
```

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\ai-presenter.exe doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo
```

```powershell
git diff --check -- packages\ringcentral-video.yaml tests\unit\test_questions.py tests\unit\test_diagnostics.py tests\unit\test_cli.py docs\agent-handoffs\cycle-168-technical-scan.md
```
