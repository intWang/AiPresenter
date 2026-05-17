# Cycle 158 Technical Scan: Reactions and Raise Hand Exact Prompts

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`

## Recommendation

Treat these six English prompts as exact Q&A prompts on the existing visible-signal safety Q&A item, not as `questionAliases` on the Reactions or Raise hand entrypoints:

- `Raise my hand`
- `Lower my hand`
- `Send a thumbs up`
- `Send a reaction`
- `React with thumbs up`
- `Can you raise my hand?`

These are action-shaped live meeting signal requests. They should return the existing safety answer for `Can AiPresenter send a reaction or raise my hand safely?`, remain `can_operate is False`, and create no question interrupt step. Do not add English entrypoint aliases for these prompts; entrypoint aliases are for locating or explaining controls and can return thin text such as `Reactions: Send meeting reactions without interrupting speech.` instead of the explicit visible-signal boundary.

## Current Routing

`src/ai_presenter/runtime/questions.py` already has the right routing shape:

- `answer_question()` normalizes the user prompt.
- `_match_qa()` checks `package.qa_questions_by_normalized` before entrypoint aliases or scored entrypoint matching.
- Exact Q&A matches return the Q&A answer and only then evaluate operability.
- `_can_operate()` blocks risky entrypoints using `questionPolicy`, missing `openSteps`, and risky words such as `send`, `reaction`, `raise hand`, and `lower hand`.
- `create_question_interrupt_step()` returns `None` when `response.can_operate` is false.

Observed current-tree routing for all six target prompts:

```text
'Raise my hand' -> entrypoint=None, can_operate=False, answer_start='Reactions and Raise hand are visible meeting signals...'
'Lower my hand' -> entrypoint=None, can_operate=False, answer_start='Reactions and Raise hand are visible meeting signals...'
'Send a thumbs up' -> entrypoint=None, can_operate=False, answer_start='Reactions and Raise hand are visible meeting signals...'
'Send a reaction' -> entrypoint=None, can_operate=False, answer_start='Reactions and Raise hand are visible meeting signals...'
'React with thumbs up' -> entrypoint=None, can_operate=False, answer_start='Reactions and Raise hand are visible meeting signals...'
'Can you raise my hand?' -> entrypoint=None, can_operate=False, answer_start='Reactions and Raise hand are visible meeting signals...'
```

Location-style questions still route to entrypoints, which is desirable:

- `Where is Raise hand?` -> `ringcentral.video.toolbar.raise-hand`, `can_operate is False`, entrypoint text.
- `Where are Reactions?` -> `ringcentral.video.toolbar.react`, `can_operate is False`, entrypoint text.

## Current Tree Note

The working tree is not limited to `.coverage` right now. I did not create or edit these source/test changes, and did not revert them:

- `packages/ringcentral-video.yaml` has the six exact English prompts added under the existing reaction/raise-hand safety Q&A item.
- `tests/unit/test_questions.py` has those six prompts added to `test_ringcentral_reaction_and_raise_hand_safety_questions_are_answer_only`.
- `tests/unit/test_cli.py` has doctor Q&A prompt count expectations updated from `103` to `109`.
- `tests/unit/test_diagnostics.py` has Q&A diagnostic count expectations updated from `103` to `109`.
- `docs/agent-handoffs/cycle-158-demand-analysis.md` is untracked and already present.
- `.coverage` is dirty.

This scan only writes `docs/agent-handoffs/cycle-158-technical-scan.md`.

## Files and Counts

Already aligned in the current tree:

- `packages/ringcentral-video.yaml`
  - The existing Q&A item now has 10 English localized prompts for this item: the previous 4 plus the 6 exact prompts.
- `tests/unit/test_questions.py`
  - The focused safety test now covers 11 English prompts total: the previous 5 plus the 6 exact prompts.
- `tests/unit/test_cli.py`
  - Doctor output count assertions now expect `109 Q&A question prompts...`.
- `tests/unit/test_diagnostics.py`
  - Q&A count assertions already expect `109`.

No runtime source changes appear necessary. No entrypoint alias counts should change, because these prompts belong in Q&A, not `questionAliases`.

## Test Evidence

Passing:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py::test_ringcentral_reaction_and_raise_hand_safety_questions_are_answer_only
```

Observed:

```text
11 passed
```

Passing:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_questions_ok_for_ringcentral_package tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_alias_overlap_ok_for_ringcentral_package
```

Observed:

```text
2 passed
```

Passing:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_cli.py::test_doctor_loads_profile_package_and_flow
```

Observed:

```text
1 passed
```

Doctor output confirms the current package inventory:

```powershell
.\.venv\Scripts\ai-presenter doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo
```

Key observed lines:

```text
[OK] question aliases: 157 package-owned aliases have no cross-entrypoint duplicates
[OK] qa questions: 109 Q&A question prompts have no cross-item duplicates
[OK] qa alias overlap: 109 Q&A question prompts have no unsafe package-owned alias overlaps
[INFO] qa alias substring risk: 11 Q&A question prompts contain package-owned alias substrings outside related entrypoints
Doctor completed: 11 ok, 1 info, 0 warnings, 0 failed.
```

## Focused Commands

Use `--override-ini addopts= -p no:cacheprovider` to avoid the repo's default coverage/cache behavior while preserving the current `.coverage` situation as much as possible:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py::test_ringcentral_reaction_and_raise_hand_safety_questions_are_answer_only
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_questions_ok_for_ringcentral_package tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_alias_overlap_ok_for_ringcentral_package
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_cli.py::test_doctor_loads_profile_package_and_flow
.\.venv\Scripts\ai-presenter doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo
git diff --check -- packages\ringcentral-video.yaml tests\unit\test_questions.py tests\unit\test_diagnostics.py tests\unit\test_cli.py docs\agent-handoffs\cycle-158-technical-scan.md
```

## No-Go Scope

- Do not stage, commit, reset, or revert other workers' edits.
- Do not add English `questionAliases` to `ringcentral.video.toolbar.react` or `ringcentral.video.toolbar.raise-hand` for these action-shaped prompts.
- Do not make Reactions or Raise hand operable from Q&A.
- Do not add or change `openSteps`.
- Do not click or queue `React`, `Raise hand`, thumbs up, any reaction item, or remove raise hand from these question prompts.
- Do not claim a reaction was sent, a hand was raised, a hand was lowered, or visible signal state was verified.
- Do not combine this with recording, Notes, Transcript, captions, leave/end, participants, host controls, chat, share, microphone, background, settings, runtime matcher changes, or acceptance work.
