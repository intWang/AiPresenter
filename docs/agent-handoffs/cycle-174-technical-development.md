# Cycle 174 Technical Development Handoff: Presenter Meta-Request Guard

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`
Role: Cycle174 technical-development handoff

## Scope and Boundary

This handoff documents the current Cycle174 implementation diff. Per assignment, this pass writes only:

- `docs/agent-handoffs/cycle-174-technical-development.md`

No source, test, YAML, coverage, staging, or commit changes were made by this handoff pass. The working tree already contained edits in `.coverage`, `src/ai_presenter/runtime/questions.py`, `tests/unit/test_questions.py`, and untracked Cycle174 handoff docs before this file was added.

## Problem

Presenter meta-requests are requests about how AiPresenter should answer, not requests to operate the RingCentral Video UI. Examples from the current slice include:

- `Be more concise`
- `Switch to careful tone`
- `Answer in Chinese`
- `I am new to RingCentral Video`

Before this guard, these prompts could fall through into RingCentral Video entrypoint alias or token matching. That made style, language, pacing, or user-familiarity requests look like app-control requests such as More, Views, or Video settings. The unsafe outcome to avoid is any `entrypoint_id`, `can_operate=True`, or generated interrupt for a prompt that should remain answer-only.

## Implementation Summary

The current diff adds a conservative Presenter meta-request guard in `src/ai_presenter/runtime/questions.py`.

Key pieces:

- `_PRESENTER_META_REQUEST_ANSWER` defines the generic answer explaining that language, tone, pacing, and guidance depth belong to AiPresenter voice settings and are separate from RingCentral Video controls.
- `_PRESENTER_META_REQUEST_FRAGMENTS` lists high-confidence English fragments for language, tone, pacing, and beginner-guidance requests.
- `_is_presenter_meta_request(normalized_question)` returns `True` when any configured fragment is a substring of the normalized prompt.
- `_answer_question(...)` keeps existing Q&A safety routing first, then treats pure Presenter meta requests as answer-only.
- `_match_explicit_entrypoint(...)` lets a mixed prompt keep an explicit RingCentralVideo intent when it contains a package alias, meeting-info location lookup, or entrypoint title.
- When a pure meta request has no explicit RingCentralVideo intent, it returns `QuestionResponse(answer_text=_render_text(_PRESENTER_META_REQUEST_ANSWER, voice))`.

Because `QuestionResponse` defaults are `entrypoint_id=None` and `can_operate=False`, the short-circuited response is answer-only and cannot create a RingCentral Video interrupt through `create_question_interrupt_step(...)`.

The current diff also adds parametrized unit tests in `tests/unit/test_questions.py` covering representative pure meta prompts and mixed prompts that combine style modifiers with meeting-info privacy, encryption status, host controls, and full-screen routing.

## Files Touched

Observed implementation diff:

- `src/ai_presenter/runtime/questions.py`
  - Added Presenter meta answer text.
  - Added high-confidence fragment matcher.
  - Added Q&A-first pure-meta short-circuit in `_answer_question(...)`.
  - Added explicit-entrypoint matching for mixed meta plus RingCentralVideo requests.
  - Added `_is_presenter_meta_request(...)`.
- `tests/unit/test_questions.py`
  - Added `test_presenter_meta_requests_do_not_route_to_ringcentral_controls`.
  - The test asserts `entrypoint_id is None`, `can_operate is False`, no interrupt step, answer prefix `Presenter settings:`, and no no-match wording.
  - Added `test_presenter_meta_modifiers_do_not_steal_ringcentral_intents`.
  - The mixed-intent test asserts privacy/security/host-control Q&A and full-screen routing still win when a prompt also contains tone or brevity modifiers.

This handoff pass touched only:

- `docs/agent-handoffs/cycle-174-technical-development.md`

Pre-existing dirty/untracked files observed:

- `.coverage`
- `docs/agent-handoffs/cycle-174-demand-analysis.md`
- `docs/agent-handoffs/cycle-174-risk-scan.md`
- `docs/agent-handoffs/cycle-174-technical-scan.md`

## Exact Matcher Behavior

Normalization is inherited from `normalize_question_prompt(...)` in `src/ai_presenter/packages/models.py`: the prompt is stripped, case-folded, and Latin diacritics are removed. Punctuation is not removed by this normalizer.

The matcher behavior is exact substring matching over the normalized prompt:

```python
any(fragment in normalized_question for fragment in _PRESENTER_META_REQUEST_FRAGMENTS)
```

There is no regex, token-boundary check, fuzzy matching, NLP classifier, YAML participation, package lookup, or voice-state mutation.

Current fragments:

```text
answer in chinese
answer in english
answer in japanese
answer in spanish
be brief
be concise
beginner guidance
can you speak chinese
can you speak english
can you speak japanese
can you speak spanish
careful tone
change language
coach tone
conversational tone
explain more slowly
formal tone
friendly tone
guidance depth
language to
make the presenter friendlier
more concise
more slowly
new to ringcentral
new to ringcentral video
please be brief
presenter friendlier
privacy tone
speak chinese
speak english
speak japanese
speak spanish
support tone
```

Examples of current positive matches:

- `Be more concise` matches `more concise`.
- `Switch to careful tone` matches `careful tone`.
- `Use coach tone` matches `coach tone`.
- `Answer in Chinese` matches `answer in chinese`.
- `Can you speak Spanish?` matches `can you speak spanish` despite the trailing question mark.
- `Change language to Japanese` matches both `change language` and `language to`.
- `I am new to RingCentral Video` matches `new to ringcentral` and `new to ringcentral video`.
- `I need beginner guidance` matches `beginner guidance`.
- `Make the presenter friendlier` matches `make the presenter friendlier`.

For pure meta prompts, the returned response does not set `entrypoint_id` or `can_operate`, so the dataclass defaults keep the route non-operable. For mixed prompts, existing Q&A safety routes win first; if there is no Q&A hit, only explicit package aliases, meeting-info location lookups, or entrypoint title mentions can route to RingCentralVideo while the meta matcher is active. Broad token fallback is intentionally skipped for meta prompts.

## Insertion Point

The guard is evaluated after `_match_qa(...)` and before broad entrypoint token fallback.

This final insertion point protects existing RingCentralVideo safety knowledge. Meeting-info privacy, encryption/security, host controls, recording, notes/transcript, and other authored Q&A can still answer first. After that, pure Presenter style/language/familiarity prompts do not enter broad RingCentralVideo token matching, so `more`, `switch`, or `RingCentral Video` cannot accidentally produce More actions, Views, or Video settings.

The placement is conservative because the fragment list is narrow and because mixed prompts only bypass the meta answer when they carry an explicit RingCentralVideo signal. It avoids bare words such as `privacy`, `language`, `tone`, `video`, `more`, `settings`, `chat`, `participants`, `recording`, `host`, `security`, `share`, or `copy`. The guarded strings are phrased as Presenter answer-style requests, not general RingCentral Video controls.

There is still a tradeoff: meta prompts skip broad token fallback unless they also contain an explicit package alias, meeting-info location lookup, or entrypoint title. That is intentional for this patch, but future expansions should add overlap tests before adding broader fragments.

## Known Limits and Future Work

- The matcher is English-only except for whatever English fragments users type around non-English language names.
- It does not cover several plausible meta-requests from earlier analysis, such as `Use Chinese`, `Respond in English`, `Make this more executive`, `Skip the basics`, or `I know RingCentral Video well, be concise`.
- It uses substring matching without token boundaries. This is simple and stable for the current fragments, but future broader fragments could create false positives.
- It does not persist or mutate `PresenterVoiceSettings`; it only answers safely. The answer must not be interpreted as a real language or tone state change.
- The answer text is generic for all matched dimensions. Future work could tailor responses by language/tone/detail/familiarity category.
- There are no added controller/session tests in this diff. The unit test verifies no interrupt through `create_question_interrupt_step(...)`, but controller-level text-only behavior could be covered later.
- If the fragment list expands, keep Q&A-first ordering and add explicit exclusions or tests for meeting-info privacy, host controls, recording, notes/transcript, full-screen, and encryption/security prompts.
- Future tests should add boundary examples with embedded control words, such as `answer chat more concisely`, `be more detailed when explaining participants`, and plain control lookups like `where is chat` to prove ordinary controls still route normally.

## Commands and Results

Inspection commands run:

```powershell
git status --short
```

Result summary: working tree had pre-existing modifications in `.coverage`, `src/ai_presenter/runtime/questions.py`, and `tests/unit/test_questions.py`, plus untracked Cycle174 handoff docs.

```powershell
git diff -- src/ai_presenter/runtime/questions.py tests/unit/test_questions.py
```

Result summary: showed the Presenter meta-request constants/helper/short-circuit in `questions.py` and the new parametrized unit test in `test_questions.py`.

```powershell
Get-ChildItem -Path 'docs\agent-handoffs' -Filter 'cycle-174-*' | Select-Object -ExpandProperty FullName
```

Result summary: found existing `cycle-174-demand-analysis.md`, `cycle-174-risk-scan.md`, and `cycle-174-technical-scan.md`.

Focused verification run:

```powershell
.\.venv\Scripts\python.exe -B -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests\unit\test_questions.py::test_presenter_meta_requests_do_not_route_to_ringcentral_controls tests\unit\test_questions.py::test_ringcentral_full_screen_questions_route_to_view_layout
```

Result:

```text
18 passed in 4.31s
```

Main-session follow-up verification after addressing the mixed-intent P2:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\unit\test_questions.py::test_presenter_meta_modifiers_do_not_steal_ringcentral_intents -q --no-cov
```

Result:

```text
5 passed in 1.34s
```

```powershell
.\.venv\Scripts\python.exe -m pytest tests\unit\test_questions.py::test_presenter_meta_requests_do_not_route_to_ringcentral_controls tests\unit\test_questions.py::test_presenter_meta_modifiers_do_not_steal_ringcentral_intents tests\unit\test_questions.py::test_ringcentral_full_screen_questions_route_to_view_layout tests\unit\test_questions.py::test_ringcentral_host_controls_question_returns_participants_guidance tests\unit\test_questions.py::test_ringcentral_careful_tone_preserves_privacy_question_route tests\unit\test_questions.py::test_ringcentral_english_meeting_info_privacy_questions_stay_qa_first tests\unit\test_questions.py::test_ringcentral_encryption_status_questions_stay_meeting_info_answer_only tests\unit\test_questions.py::test_spanish_meeting_info_location_requests_use_entrypoint_answer -q --no-cov
```

Result:

```text
97 passed in 20.64s
```

## Status

Cycle174 technical-development handoff is complete. The implementation protects covered pure Presenter meta-request prompts as answer-only, non-operable, and no-interrupt, while preserving mixed RingCentralVideo privacy, security, host-control, and full-screen routing.

Changed file path:

- `docs/agent-handoffs/cycle-174-technical-development.md`
