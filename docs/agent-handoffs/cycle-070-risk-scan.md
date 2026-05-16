# Cycle 070 Risk Scan: explain-share JA Narration

Date: 2026-05-16

## Scope

Risk review for adding Japanese `localizedText.ja` to `meeting-controls-tour` -> `explain-share`.

The owned implementation should remain narration-only and preserve `operation: open`.

## Key Risks

1. **Private shared content**
   - The picker can expose application names, document titles, desktop thumbnails, browser tabs, and private windows.
   - Narration should not read or summarize candidates or shared content by default.

2. **Accidental final Share**
   - Pressing the final Share button changes the meeting state and exposes content to participants.
   - The Japanese narration must make confirmation required before final Share.

3. **System audio**
   - Sharing system audio can expose notifications, media, or private meeting/audio content.
   - Mention it as a capability, not something AiPresenter enables automatically.

4. **Cleanup confidence**
   - The route uses Escape cleanup and is not fully live accepted.
   - This localization pass should not upgrade live confidence or change cleanup.

5. **Boundary with shared-content Q&A**
   - Existing Q&A says shared content can be described only after approved observation and user permission.
   - Demo narration must remain consistent with that privacy boundary.

## Mitigations

- Keep `operation: open` and `actionOffsetMs: 400`.
- Do not change locators, cleanup, aliases, Q&A, runtime routing, or state extraction.
- Explicitly say final Share is not pressed until the user confirms what to show.
- Explicitly say picker candidates and screen content are not read without clear permission.
- Mention system audio only as an option.
- Close the picker after explanation.

## Must-Verify Checks

- `localizedText.ja` is added only to `explain-share`.
- `entrypointId` remains `ringcentral.video.toolbar.share`.
- `operation` remains `open`.
- `placement: during` and `actionOffsetMs: 400` remain unchanged.
- Japanese coverage advances to `21/51`.
- `meeting-controls-tour` advances to `14/22`.
- First missing step advances to `explain-reactions`.
- Q&A and aliases remain unchanged.
- `.coverage` remains unstaged.

## Recommendation

Proceed as a narrow narration slice. Do not bundle reaction localization, live picker acceptance, system-audio toggling, or final Share behavior into this commit.
