# Cycle 153 Technical Development

## Objective

Add the smallest post-`empathetic -> support` guard proving RingCentral question routing remains tone-invariant when the `empathetic` alias is supplied.

## Final Implementation

The retained implementation is test-only in `tests/unit/test_questions.py`.

Exact diff behavior:

```python
for tone in ("friendly", "coach", "support", "empathetic", "privacy"):
```

This adds `empathetic` to the existing tone-invariant loop in `test_ringcentral_sensitive_prompt_routing_is_tone_invariant`. The existing assertions continue to compare each non-baseline tone against the `professional` baseline for:

- `entrypoint_id`
- `can_operate`
- interrupt-step presence from `create_question_interrupt_step(...)`

No source, package, profile, README, or existing handoff document changes are part of the final implementation.

## Evidence

Red evidence:

- Temporary removal of `"empathetic": "support"` from the tone alias table caused the focused RingCentral routing test to fail across all 9 routing parameters.
- Failure mode: `Unsupported presenter tone: empathetic`.
- The alias entry was restored; no source mutation remains.

Green evidence:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py::test_ringcentral_sensitive_prompt_routing_is_tone_invariant tests\unit\test_voice.py::test_voice_settings_normalize_expanded_tones
```

Observed result:

```text
10 passed
```

## Risk Boundaries

- This does not introduce a new canonical `empathetic` tone.
- This does not change RingCentral routing, `questionPolicy`, `openSteps`, package YAML, answer text, or interrupt behavior.
- This does not claim `empathetic` makes routing safer, more private, more compliant, or more capable.
- This does not touch `.coverage`; the repository already had a modified `.coverage` file.
- Pytest commands for this slice should keep `--override-ini addopts=` to avoid coverage writes.

## Recommended Follow-Up

Before merge, keep the retained diff limited to `tests/unit/test_questions.py` plus this handoff. If future work adds more tone aliases, include them in this same invariant routing surface only after their alias normalization is already covered in `tests/unit/test_voice.py`.
