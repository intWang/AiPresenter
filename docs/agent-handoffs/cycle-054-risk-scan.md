# Cycle 054 Risk Scan

## Risks

- Localized prompts are routing inputs, so Japanese strings can shadow entrypoint aliases or redirect privacy questions.
- Japanese voice support must not imply every speech provider can synthesize Japanese.
- Privacy-sensitive Q&A must preserve explicit-user-request and verified-context language.
- `.coverage` remains a tracked modified artifact after tests and must stay out of commits.

## Controls Applied

- Japanese voice output is accepted only for OpenAI speech profiles.
- Japanese local text rendering avoids English tone prefixes.
- Japanese no-match text prevents runtime `KeyError` or unsupported-language crashes after voice normalization.
- Chat/participant privacy Q&A was made answer-only by removing its related entrypoints; direct `chat` entrypoint routing remains available through entrypoint aliases and token matching.

## Review Checklist

- Confirm `qa questions` and `qa alias overlap` stay OK at `63` prompts.
- Confirm Japanese Q&A has no executable new route.
- Confirm Chinese and English behavior still passes existing tests.
- Confirm `.coverage` is not staged.
