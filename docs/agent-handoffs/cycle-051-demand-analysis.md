# Cycle 051 Demand Analysis

## Recommended Slice

Add a doctor-only guard for exact overlaps between Q&A prompts and package-owned entrypoint aliases.

## User Value

AiPresenter is gaining more RingCentral Video Q&A coverage. Operators need doctor to catch cases where a newly authored Q&A prompt silently shadows an existing package-owned alias. Without that guard, doctor can report both Q&A prompts and aliases as individually healthy while runtime still answers through Q&A first.

## Acceptance Criteria

- Doctor emits a `qa alias overlap` diagnostic whenever a Q&A prompt exactly matches an entrypoint alias and the Q&A does not reference that entrypoint.
- The diagnostic is `WARN`, not `FAIL`.
- The warning names the normalized prompt, Q&A languages, alias languages, Q&A item label, shadowed entrypoint IDs, and that the first match is Q&A.
- Q&A prompts that reference the same entrypoint as the alias remain OK.
- The RingCentral Video package remains OK; the intentional `recording` safety overlap stays allowed because the Q&A references the recording entrypoint.
- Runtime Q&A/alias matching behavior remains unchanged.

## Out Of Scope

- No matcher ordering change.
- No YAML package content change.
- No new entrypoints, locators, or RingCentral automation.
- No substring or fuzzy overlap diagnostics.

## Suggested Files And Tests

- `src/ai_presenter/runtime/diagnostics.py`
- `tests/unit/test_diagnostics.py`
- `tests/unit/test_cli.py`

Focused tests should cover answer-only shadowing, same-entrypoint allowed overlap, RingCentral healthy baseline, and CLI doctor output.
