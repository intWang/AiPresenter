# Cycle 174 Experience Handoff: Presenter Meta Requests

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`
Scope: write only `docs/agent-handoffs/cycle-174-experience.md`

## Sources Read

- `docs/agent-handoffs/cycle-174-demand-analysis.md`
- `docs/agent-handoffs/cycle-174-risk-scan.md`
- `docs/agent-handoffs/cycle-174-technical-scan.md`
- `docs/knowledge/ringcentral-video/runtime-safety-routing.md`
- `docs/knowledge/ai-presenter-maintenance.md`
- Current working diff for `src/ai_presenter/runtime/questions.py` and `tests/unit/test_questions.py`

The current workspace already has unrelated dirty files: `.coverage`, `src/ai_presenter/runtime/questions.py`, and `tests/unit/test_questions.py`. Treat those as existing work from other agents unless explicitly assigned otherwise.

## What User Need Was Discovered

The real user need is not another RingCentral Video control route. Users are asking AiPresenter to change how it explains:

- Language: `Answer in Chinese`, `Answer in English`, `Can you speak Spanish?`
- Tone: `Switch to careful tone`, `Use privacy tone`, `Make the presenter friendlier`
- Detail and pacing: `Be more concise`, `Explain more slowly`, `I need beginner guidance`
- Familiarity level: `I am new to RingCentral Video`

Those prompts are about Presenter behavior, not app UI operation. Before Cycle174, these words could fall through into RingCentral Video alias/token routing and accidentally hit Views, More, Video settings, Chat, Participants, or other controls. The expected experience is answer-only, non-operable, and no interrupt. The answer may acknowledge the Presenter preference, but it must not claim a persistent language/tone state change unless controller or voice state was actually updated and tested.

## Durable Routing Pattern

Keep Presenter meta requests at the runtime routing layer, not in `packages/ringcentral-video.yaml`. They are AiPresenter expression requests, not RingCentralVideo package facts.

The durable pattern is:

1. Normalize the prompt with the same question normalizer used by existing routing.
2. Let existing Q&A safety routing win first.
3. Detect only high-confidence Presenter meta requests before broad entrypoint token fallback.
4. For pure meta requests, return `QuestionResponse(answer_text=..., entrypoint_id=None, can_operate=False)`.
5. For mixed prompts, allow only explicit RingCentralVideo package aliases, meeting-info location lookups, or entrypoint title mentions to route.
6. Let `create_question_interrupt_step(...)` naturally return `None` for pure meta requests because there is no entrypoint and no permission.
7. Render through `PresenterVoiceSettings`, but do not let language or tone alter route choice.
8. Avoid YAML count drift, localization diagnostic drift, and package-owned alias expansion.

Important caveat from the risk scan and follow-up review: a meta matcher must never steal existing safety Q&A for meeting information, host controls, encryption/security, recording, notes, transcript, or full screen. Cycle174 now covers this with mixed-intent tests and Q&A-first ordering.

Current diff observation: the working tree adds `_PRESENTER_META_REQUEST_FRAGMENTS`, `_is_presenter_meta_request(...)`, `_match_explicit_entrypoint(...)`, and a `Presenter settings:` answer in `questions.py`, plus pure-meta and mixed-intent parametrized tests in `test_questions.py`.

## Test Strategy

For the current slice, keep tests focused in `tests/unit/test_questions.py`:

- Positive meta prompts should assert `response.entrypoint_id is None`, `response.can_operate is False`, and `create_question_interrupt_step(package, response) is None`.
- The answer should identify a Presenter setting/request and must not use RingCentral control prefixes such as `View layout menu:`, `More actions:`, `More video settings:`, `Meeting information:`, `Network quality:`, or `Reactions:`.
- Plain control lookups such as `chat`, `where is chat`, `participants`, and `network quality` should still route as before.
- Full screen prompts should still route to `ringcentral.video.top.views`.
- Meeting information privacy, host controls, encryption/security status, notes/transcript, and recording safety prompts should remain Q&A-first or answer-only as already designed.
- Tone and language variants must not change `entrypoint_id`, `can_operate`, or interrupt creation.

Suggested focused command for implementation agents:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -B -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests\unit\test_questions.py tests\unit\test_controller_session.py tests\unit\test_controller.py::test_presenter_controller_queues_safe_question_without_stopping_running_demo tests\unit\test_controller.py::test_presenter_controller_answers_risky_question_without_demo
```

Before staging in a future implementation cycle, also run:

```powershell
git diff --check
git status --short
git diff --cached --name-status
```

Do not let `.coverage` become part of the change. Use `--no-cov`, `-p no:cacheprovider`, `-B`, and `PYTHONDONTWRITEBYTECODE` for focused verification when possible.

## RingCentralVideo Knowledge Gained

- `entrypoint_id` is identification, not permission. Permission is decided by `questionPolicy`, `openSteps`, and risky wording.
- `questionPolicy: answerOnly` lets a route identify a useful surface without queuing UI operation.
- `create_question_interrupt_step(...)` is the final interrupt gate: no entrypoint or `can_operate=False` means no demo interrupt.
- Meeting information is especially sensitive because it can include meeting ID, link, dial-in, host identity, account details, encryption, and E2EE options.
- Full screen belongs to the Views/layout explanation path, not Leave meeting, Share, or OS full-screen behavior.
- Language and tone belong to rendering and voice settings. They must not change route, Q&A precedence, `can_operate`, or interrupt behavior.
- Package YAML is the wrong place for Presenter meta requests. Adding them there would blur app knowledge with Presenter behavior and disturb package diagnostics.
- RingCentralVideo optimization should preserve package counts unless the cycle explicitly owns package content.

## Reusable Prompts For Next Agents

Implementation prompt:

```text
Continue Cycle174 Presenter meta request routing. Read the cycle-174 handoffs and current diff first. Keep changes limited to runtime question routing and focused tests unless the user assigns more. Ensure high-confidence language, tone, detail, and familiarity prompts return answer-only with no RingCentralVideo entrypoint or interrupt. Do not change package YAML or persistent voice state.
```

Reviewer prompt:

```text
Review the Presenter meta request guard for false positives. Check whether it can steal meeting-info privacy Q&A, host controls, encryption/security answer-only routes, notes/transcript safety, recording safety, or full screen Views routing. Prioritize missing tests and route regressions over style comments.
```

Test-expansion prompt:

```text
Add overlap tests for Presenter meta prompts containing control words. Separate pure style requests from mixed RingCentralVideo intents: pure style requests should be answer-only with no interrupt; mixed requests with explicit package aliases, meeting-info location, or entrypoint titles should preserve the RingCentral route and safety policy. Include Chinese equivalents after English behavior is pinned.
```

Knowledge-update prompt:

```text
If the Presenter meta guard survives implementation and review, update repo-local knowledge only. Add a short note to the RingCentral runtime safety guidance explaining that Presenter expression requests are runtime answer-only guards, not RingCentralVideo YAML Q&A or aliases. Do not claim live RingCentral acceptance without dated evidence.
```

## Next-Cycle Candidate Backlog

- Add negative-control tests around plain app control lookups so the meta guard cannot swallow real RingCentralVideo requests.
- Add more overlap tests for meeting-info privacy, host controls, encryption/security, notes/transcript, recording, and full screen before expanding meta phrases.
- Consider replacing a flat fragment list with a conservative two-part matcher: Presenter expression verb plus language/tone/detail/familiarity dimension.
- Add Chinese high-confidence meta prompts after English coverage is stable, especially `请用中文回答`, `请讲简单一点`, and `用更谨慎的语气回答`.
- Add controller/session sentinel tests proving Presenter meta requests remain text-only and never enqueue `question-answer-demo`.
- Decide whether natural-language language/tone requests should ever update persistent `PresenterVoiceSettings`. If yes, make that a separate controller/voice state slice with copy that accurately reflects persistence.
- Document the stable pattern in `docs/knowledge/ringcentral-video/runtime-safety-routing.md` only after implementation tests and review pass.
- Keep Spanish and Japanese meta requests as a later localization wedge unless there is a concrete user prompt and provider/runtime boundary to test.

## Status

This handoff captures the Cycle174 experience lesson: separate Presenter expression requests from RingCentralVideo app-control routing, and keep the guard narrow, answer-only, and no-interrupt. No source, tests, YAML, staging, or commits were performed as part of this handoff.
