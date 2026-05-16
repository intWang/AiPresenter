# Cycle 153 Technical Scan

## Scan Scope

Inspected the current RingCentral question tests and runtime question path:

- `tests/unit/test_questions.py`
- `tests/unit/test_voice.py`
- `src/ai_presenter/runtime/voice.py`
- `src/ai_presenter/runtime/questions.py`
- `src/ai_presenter/runtime/session.py`
- `packages/ringcentral-video.yaml`

The repository already has a modified `.coverage` file. Leave it untouched.
This handoff is documentation only and does not edit source, tests, README,
packages, profiles, or existing docs.

## Current State

`src/ai_presenter/runtime/voice.py` already normalizes `empathetic` to the
canonical `support` tone through `_TONE_ALIASES`. `PresenterVoiceSettings`
normalizes tone input during construction, so downstream question APIs receive
`voice.tone == "support"` for `PresenterVoiceSettings(tone="empathetic")`.

`tests/unit/test_voice.py::test_voice_settings_normalize_expanded_tones`
already asserts:

```python
assert PresenterVoiceSettings(tone="empathetic").tone == "support"
```

The question runtime keeps tone out of route authorization:

- `answer_question(...)` calls `_answer_question(...)` and logs `voice.tone`.
- `_answer_question(...)` matches Q&A first, then entrypoints, and computes
  `QuestionResponse.can_operate` through `_can_operate(...)`.
- `_can_operate(...)` depends on the matched entrypoint, `questionPolicy`,
  `openSteps`, and risky entrypoint words, not tone.
- `create_question_interrupt_step(...)` returns `None` unless
  `response.entrypoint_id` is set and `response.can_operate` is true.

`tests/unit/test_questions.py::test_ringcentral_sensitive_prompt_routing_is_tone_invariant`
is already the right RingCentral safety regression surface. It compares a
`professional` baseline against `friendly`, `coach`, `support`, and `privacy`
for route, `can_operate`, and interrupt-step behavior across sensitive and
operable prompts. It currently does not include the `empathetic` alias.

Focused scan command run without coverage or cache writes:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py::test_ringcentral_sensitive_prompt_routing_is_tone_invariant tests\unit\test_voice.py::test_voice_settings_normalize_expanded_tones
```

Observed result: `10 passed`.

## Smallest Test-First Slice

Add `empathetic` to the existing RingCentral question tone-parity loop.

Exact test location:

- `tests/unit/test_questions.py::test_ringcentral_sensitive_prompt_routing_is_tone_invariant`

Minimal test edit:

```python
for tone in ("friendly", "coach", "support", "empathetic", "privacy"):
    response = answer_question(
        package=package,
        question=question,
        voice=PresenterVoiceSettings(tone=tone),
    )

    assert response.entrypoint_id == baseline.entrypoint_id
    assert response.can_operate is baseline.can_operate
    assert (create_question_interrupt_step(package, response) is not None) is (
        baseline_interrupt
    )
```

Helper/API surface being proved:

- `PresenterVoiceSettings(tone="empathetic")`
- `answer_question(package=package, question=question, voice=...)`
- `create_question_interrupt_step(package, response)`

This is smaller than adding a new test because the existing parameterized cases
already cover answer-only prompts, non-operable entrypoint routes, and operable
entrypoint routes:

- recording safety
- notes/transcript safety
- meeting information
- chat/participant privacy
- invite
- share
- participants
- leave
- network quality

## Red Method

Because current behavior already passes through voice normalization, use a
temporary mutation to prove the test catches the alias dependency before keeping
the green state.

1. Add `empathetic` to the tone loop in
   `tests/unit/test_questions.py::test_ringcentral_sensitive_prompt_routing_is_tone_invariant`.
2. Temporarily remove or comment out the existing
   `"empathetic": "support"` entry in `src/ai_presenter/runtime/voice.py`.
3. Run the focused test:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py::test_ringcentral_sensitive_prompt_routing_is_tone_invariant
```

Expected red result:

- the test fails when constructing `PresenterVoiceSettings(tone="empathetic")`;
- failure includes `Unsupported presenter tone: empathetic`.

Then restore `"empathetic": "support"` exactly as it was. The retained change
should be test-only: the added loop member in `tests/unit/test_questions.py`.

## Verification Commands

Focused question-route proof:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py::test_ringcentral_sensitive_prompt_routing_is_tone_invariant
```

Alias normalization guard:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_voice.py::test_voice_settings_normalize_expanded_tones
```

Broader impacted unit surface:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py tests\unit\test_voice.py
```

Diff hygiene:

```powershell
rg -n "[ \t]+$" tests\unit\test_questions.py
git diff --check -- tests\unit\test_questions.py
```

Do not run coverage-producing commands for this slice. `.coverage` is already
modified by other work and should remain untouched.

## No-Go Scope

Do not include any of the following in this smallest slice:

- source changes, unless the temporary red mutation is immediately restored;
- changes to package YAML, profiles, README, existing docs, or `.coverage`;
- new canonical tones, labels, descriptions, CLI choices, or provider routes;
- changes to RingCentral `questionPolicy`, `openSteps`, aliases, or Q&A copy;
- answer text assertions for `empathetic`;
- broad refactors of `answer_question(...)`, `_can_operate(...)`, or
  `create_question_interrupt_step(...)`;
- live RingCentral acceptance claims.

The slice is complete when `empathetic` is exercised through the RingCentral
question API and produces the same `entrypoint_id`, `can_operate`, and
interrupt-step presence as the canonical `professional` baseline in the
existing sensitive prompt matrix.
