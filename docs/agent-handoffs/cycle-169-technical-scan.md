# Cycle 169 Technical Scan: RingCentral Video View and Encryption Routing

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`
Head inspected: `62929a1`

## Guardrails

This was a scan-only pass. I did not edit source, package YAML, tests, staging,
commits, or `.coverage`. The only write from this subagent is this handoff file.

Initial `git status --short` showed `.coverage` modified. During the scan,
another worker added dirty full-screen routing edits in:

- `packages/ringcentral-video.yaml`
- `tests/unit/test_questions.py`
- `tests/unit/test_diagnostics.py`
- `tests/unit/test_cli.py`

I left those changes untouched. Current recommendations below assume those
dirty full-screen edits remain in place; if starting from clean `62929a1`,
reconcile them first.

## Current Probe Results

Read-only probe path: load `packages/ringcentral-video.yaml`, call
`answer_question(...)`, then check `create_question_interrupt_step(...)`.

### Full-Screen and Views Prompts

With the current dirty full-screen changes, the probed View layout prompts route
correctly:

| Prompt | Current route | `can_operate` | Interrupt | Notes |
| --- | --- | --- | --- | --- |
| `Show full screen` | `ringcentral.video.top.views` | `True` | yes | Dirty alias routes to Views. |
| `Full screen view` | `ringcentral.video.top.views` | `True` | yes | Dirty alias routes to Views. |
| `Switch to gallery view` | `ringcentral.video.top.views` | `True` | yes | Existing route remains good. |
| `Switch to full screen` | `ringcentral.video.top.views` | `True` | yes | Dirty alias routes to Views. |
| `Where is full screen?` | `ringcentral.video.top.views` | `True` | yes | Dirty alias routes to Views. |
| `Can you open views?` | `ringcentral.video.top.views` | `True` | yes | Existing title/purpose match remains good. |
| `Change meeting layout` | `ringcentral.video.top.views` | `True` | yes | Existing purpose match remains good. |

`git diff` shows those full-screen aliases and tests are uncommitted relative to
`62929a1`; do not overwrite them.

### Encryption-Status Prompts

Encryption prompts are still mixed:

| Prompt | Current route | `can_operate` | Interrupt | Issue |
| --- | --- | --- | --- | --- |
| `Is this meeting encrypted?` | `None` | `False` | no | No match. |
| `Is end-to-end encryption on?` | `ringcentral.video.top.meeting-info` | `False` | no | Safe but generic Meeting information text. |
| `Can you verify encryption?` | `ringcentral.video.top.meeting-info` | `False` | no | Safe but generic Meeting information text. |
| `Can you verify end-to-end encryption?` | `ringcentral.video.toolbar.leave` | `False` | no | Wrong safety answer; `end` falls toward Leave. |
| `Where is encryption?` | `ringcentral.video.top.meeting-info` | `False` | no | Safe location route. |
| `Show meeting encryption status` | `ringcentral.video.top.meeting-info` | `False` | no | Safe but generic Meeting information text. |
| `Open encryption settings` | `ringcentral.video.settings.background` | `True` | yes | Wrong and operable; `settings` falls to Background settings. |
| `Where is end-to-end encryption?` | `ringcentral.video.top.meeting-info` | `False` | no | Safe location route. |

## Recommended Safe Target

Extend the existing Meeting information privacy Q&A to cover English
encryption-status prompts. This is safer than adding an entrypoint alias because
it keeps the response answer-only, avoids clicking UI, and prevents the two bad
routes above from falling to Leave or Background settings.

Use the existing Q&A item:

```yaml
- question: How should AiPresenter handle meeting IDs and links safely?
```

Do not create a new Q&A item for this slice unless you also update localization
count expectations. Extending the existing item keeps localized Q&A item totals
stable.

## Exact Package Edit

In `packages/ringcentral-video.yaml`, add these English localized questions to
that existing Meeting information privacy Q&A:

```yaml
    - Is this meeting encrypted?
    - Is end-to-end encryption on?
    - Can you verify encryption?
    - Can you verify end-to-end encryption?
    - Open encryption settings
    - Show meeting encryption status
```

Extend the same Q&A answer with encryption language while preserving the current
opening phrase used by existing tests:

```text
Encryption status and end-to-end encryption options are sensitive meeting details too; explain where to verify them without claiming status, changing settings, or reading exact values unless the user explicitly asks and the visible content is verified.
```

Also update the existing `localizedAnswers` for `es`, `ja`, and `zh` with the
same meaning. No new localized question is required for this English-only route
gap.

## Exact Test Edits

Add a focused test near
`test_ringcentral_english_meeting_info_privacy_questions_stay_qa_first` in
`tests/unit/test_questions.py`:

```python
@pytest.mark.parametrize(
    "question",
    [
        "Is this meeting encrypted?",
        "Is end-to-end encryption on?",
        "Can you verify encryption?",
        "Can you verify end-to-end encryption?",
        "Open encryption settings",
        "Show meeting encryption status",
    ],
)
def test_ringcentral_english_encryption_status_questions_stay_qa_first(
    question: str,
) -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    response = answer_question(
        package=package,
        question=question,
        voice=PresenterVoiceSettings(),
    )

    assert response.entrypoint_id == "ringcentral.video.top.meeting-info"
    assert response.can_operate is False
    assert create_question_interrupt_step(package, response) is None
    assert "Encryption status" in response.answer_text
    assert "end-to-end encryption" in response.answer_text
    assert "Meeting information:" not in response.answer_text
    assert "Background settings:" not in response.answer_text
    assert "Leaving or ending a meeting" not in response.answer_text
```

Update count assertions:

- `tests/unit/test_diagnostics.py::test_diagnostics_reports_qa_questions_ok_for_ringcentral_package`
  from `178 Q&A question prompts...` to `184 Q&A question prompts...`.
- `tests/unit/test_diagnostics.py::test_diagnostics_reports_qa_alias_overlap_ok_for_ringcentral_package`
  from `178 Q&A question prompts...` to `184 Q&A question prompts...`.
- `tests/unit/test_cli.py::test_doctor_loads_profile_package_and_flow`
  for both Q&A prompt count strings, from `178` to `184`.

For this encryption slice, do not change package-owned alias counts. In the
current dirty worktree they are already `161` because of the concurrent
full-screen alias edits. On clean `62929a1`, they would remain at `157` unless
the full-screen slice is also applied.

## Count Impact

Current dirty worktree with the full-screen edits present:

- Package-owned aliases: stays `161`
- Q&A question prompts: `178 -> 184`
- Q&A alias overlap count: `178 -> 184`
- Q&A alias substring risk: stays `11`
- Localized Q&A item coverage: stays `15/15` if the existing Q&A item is
  extended rather than creating a new item

In-memory simulation of the package edit above produced:

```text
question aliases OK 161 package-owned aliases have no cross-entrypoint duplicates
qa questions OK 184 Q&A question prompts have no cross-item duplicates
qa alias overlap OK 184 Q&A question prompts have no unsafe package-owned alias overlaps
qa alias substring risk INFO 11 Q&A question prompts contain package-owned alias substrings outside related entrypoints
```

## Risks

- Do not add broad package-owned aliases such as `encryption`, `security`, or
  `settings`; exact Q&A prompts avoid stealing unrelated Meeting information,
  host security, or settings queries.
- `Can you verify end-to-end encryption?` currently falls toward Leave because
  of the `end` token. Keep this exact prompt in Q&A coverage.
- `Open encryption settings` currently creates a Background settings interrupt.
  Keep it Q&A-first and answer-only; do not turn it into an operable route.
- The answer must not claim encryption is on or off. This scan has no live
  RingCentral UI evidence, only package-routing evidence.
- Preserve the concurrent full-screen dirty edits or coordinate with that worker
  before changing alias-count expectations.

## Verification Commands

Use cache/coverage-light commands so default pytest coverage does not touch
`.coverage`:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py::test_ringcentral_english_encryption_status_questions_stay_qa_first
```

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_questions_ok_for_ringcentral_package tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_alias_overlap_ok_for_ringcentral_package tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_alias_substring_info_for_ringcentral_package tests\unit\test_cli.py::test_doctor_loads_profile_package_and_flow
```

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\ai-presenter.exe doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo
```

```powershell
git diff --check -- packages\ringcentral-video.yaml tests\unit\test_questions.py tests\unit\test_diagnostics.py tests\unit\test_cli.py docs\agent-handoffs\cycle-169-technical-scan.md
```
