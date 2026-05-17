# Cycle 183 Risk Scan: zh/ja Privacy Parity

Date: 2026-05-17

## Findings

- The main UX risk was misleading operator wording: privacy Q&A matched but summary said `no matching safe control`.
- Voice readiness remains deliberately profile-constrained. Chinese needs `openai` or `windows-sapi-zh`; Japanese needs `openai`. This cycle does not change that.
- Chinese and Japanese participant privacy depend on runtime term matrices plus localized Q&A. New phrasing should still be added with tests before docs promise it.
- `.coverage` remains a local generated artifact and must stay unstaged.

## Mitigations

- Added `answer_source` metadata from `answer_question()` through `QuestionSubmitResult`.
- Updated operator summary wording for Q&A-only results.
- Added durable Chinese and Japanese examples to the privacy matrix.
- Added Japanese controller text-only regressions without triggering unsupported voice execution.

## Residual Risks

- Session-level Japanese tests still require an OpenAI profile because `ControllerSession.set_voice()` validates voice readiness.
- Future localized phrase expansion can still miss runtime guards if docs and tests are not updated together.
