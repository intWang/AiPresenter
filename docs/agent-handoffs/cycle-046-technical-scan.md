# Cycle 046 Technical Scan

## Current State

The package has a Participants entrypoint, explainer notes, privacy matrix coverage, and demo narration that mention participant controls. Q&A currently covers reading chat/participant names, but not the positive "how do I manage participants as host" scenario.

## Proposed Implementation

- Add one Q&A item to `packages/ringcentral-video.yaml`.
- Provide English question/answer plus `localizedQuestions.zh` and `localizedAnswers.zh`.
- Omit `relatedEntrypointIds` so the host-management answer stays non-operable.
- Update localization count tests from 8/8 to 9/9.
- Tighten Q&A substring matching so a one-word generic query such as `participants` does not get shadowed by the new host-management Q&A.

## TDD Plan

1. Add English and Chinese question tests before changing YAML.
2. Update localization/doctor/CLI expectations for the new Q&A total.
3. Run the focused new tests and observe failure.
4. Add the YAML Q&A item.
5. Re-run question, material package, CLI localization, and diagnostics tests.

## Risk Notes

The answer must not imply Ai Presenter can perform high-impact host actions automatically. Keep the wording centered on explaining where the Participants panel lives and require explicit request plus visible verification for names, roles, muting, removing, locking, or other state-changing host controls. The matcher guard preserves existing generic entrypoint questions while still allowing exact localized Q&A questions and specific fragments such as "host controls".
