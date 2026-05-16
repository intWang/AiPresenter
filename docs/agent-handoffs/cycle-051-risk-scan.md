# Cycle 051 Risk Scan

## Risk Reduced

Q&A additions can shadow package-owned aliases because runtime checks Q&A before alias fallback. Before this cycle, doctor checked duplicate aliases and duplicate Q&A prompts separately, but not the cross-source overlap.

## Red Tests

- A package with entrypoint alias `chat` and answer-only Q&A prompt `chat` should produce `[WARN] qa alias overlap`.
- A Q&A prompt `chat` related to `demo.chat` should remain OK.
- The real RingCentral package should remain OK.
- CLI doctor should print the warning and still exit successfully when only this warning is present.

## Existing Behavior To Preserve

- Runtime matching order remains Q&A first, then entrypoint alias fallback.
- Duplicate alias and duplicate Q&A diagnostics remain unchanged.
- RingCentral doctor keeps its healthy package baseline.
- `.coverage` remains a local test artifact and is not committed.

## Review Checklist

- Use runtime indexes instead of scanning YAML directly.
- Warn only on exact normalized cross-source overlap.
- Preserve same-entrypoint overlap.
- Keep the new diagnostic warning-only.
