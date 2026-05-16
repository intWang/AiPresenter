# Cycle 063 Risk Scan: `explain-invite` JA Narration

Date: 2026-05-16

## Scope

Assess risks for adding Japanese `localizedText.ja` narration to `packages/ringcentral-video.yaml` -> `meeting-controls-tour` -> `explain-invite`.

Only this handoff document was edited. The scan read targeted local context:

- `packages/ringcentral-video.yaml`
- `docs/knowledge/ringcentral-video/privacy-matrix.md`
- `docs/agent-handoffs/cycle-062-risk-scan.md`
- targeted test/spec references for active-meeting invite adaptation

## Risk List

1. **Active-meeting privacy surface**
   - Toolbar `Invite` opens the same Invite others dialog as empty-room `Add coworkers`.
   - The dialog can expose names, email addresses, contact suggestions, meeting links, and meeting details while other participants may already be present.
   - Japanese narration must not read, summarize, copy, or imply verification of any private values unless the user explicitly asks and the content is verified from an approved source.

2. **Invite link and meeting detail leakage**
   - The toolbar entrypoint purpose includes inviting coworkers or copying meeting details.
   - "Copy meeting details" is a sensitive action in an active meeting because links, meeting IDs, dial-in data, host identity, or room metadata can be exposed outside the call.
   - The narration can say the control is where those options live, but must not say the presenter will copy or read exact details during the tour.

3. **Accidental invitation risk**
   - The dialog has search/suggestion selection and an `Invite` action.
   - A localized tour line must not sound like it will type a name, select a suggestion, press Invite, or invite someone without confirmation.
   - This is higher risk than purely informational toolbar controls because it can affect people outside the current automation session.

4. **Active participant impact**
   - Unlike the empty-room `Add coworkers` callout, toolbar `Invite` is the active-meeting entrypoint and can run while attendees are already in the room.
   - Narration should not announce participant names, infer who is missing, or claim the meeting needs more people.
   - It should avoid disrupting the meeting by lingering in a blocking modal before subsequent controls.

5. **State confusion with empty-room `Add coworkers`**
   - `Add coworkers` is the empty-room canvas callout; `Invite` is the regular toolbar entrypoint for active meetings.
   - Reusing the previous Japanese line would create stale empty-room UX in an active meeting.
   - The Japanese text should preserve the visible label `Invite`, mention toolbar/active-meeting context, and avoid framing it as the empty-room first-person callout.

6. **Adaptive localized narration regression**
   - Prior adaptive logic had a known class of risk: rewritten active-meeting steps can update English `text` while stale localized text remains preferred by narration rendering.
   - Adding Japanese to `explain-invite` creates another localized value that must align with active-meeting adaptation, especially when participant count is two or more.
   - If runtime adaptation rewrites either Add coworkers or Invite to active-meeting wording, Japanese output must also be active-meeting wording.

7. **Blocking modal cleanup**
   - `ringcentral.video.toolbar.invite` has `cleanup: modal`, and presenter notes say to close with dialog X or Cancel before continuing.
   - If the Invite others dialog remains open, later toolbar controls may be hidden or blocked.
   - Cleanup must not rely on reading private dialog contents, pressing the final Invite button, or copying meeting details.

8. **Over-promising product behavior**
   - The exact tenant policy for external guests, directory suggestions, and meeting-link copy behavior may vary.
   - Avoid wording that promises external invitations, specific recipient types, or exact copy behavior beyond the visible toolbar purpose.
   - Keep the line descriptive: this is the active-meeting place to add participants or access meeting details.

## Mitigations

- Keep implementation narration-only: add only `narration.localizedText.ja` for `meeting-controls-tour` -> `explain-invite` unless the implementation task explicitly owns tests or docs.
- Preserve the visible product label `Invite` and mention the toolbar/active-meeting context.
- Distinguish this step from `Add coworkers`: do not use "empty meeting", "first one here", or other empty-room phrasing.
- Phrase invite and copy behavior as available options, not actions the presenter will perform.
- Include a privacy boundary covering names, emails, suggestions, invite links, and meeting details.
- Keep the line short enough for `placement: during` and `actionOffsetMs: 350`, then rely on existing modal cleanup.
- Do not add Japanese aliases or broaden operation permission for Invite as part of the narration slice.
- Treat live validation as privacy-safe observation: confirm the dialog opens and closes without recording private values.

## Must Verify

- YAML shape:
  - `localizedText.ja` is added under `meeting-controls-tour` -> `explain-invite` -> `narration`.
  - Existing English text, Chinese `localizedText.zh`, `placement: during`, and `actionOffsetMs: 350` remain unchanged unless a separate owner explicitly changes them.
  - No entrypoint, locator, `openSteps`, cleanup, aliases, Q&A, runtime, test, or unrelated flow changes are bundled into this risk slice.

- Text safety:
  - Includes `Invite`.
  - Mentions toolbar and active/ongoing meeting context.
  - Mentions adding participants or accessing/copying meeting details only as workflow options.
  - Does not say the presenter reads, copies, enters, selects, sends, or invites.
  - Does not read or expose names, email addresses, suggestions, invite links, meeting IDs, dial-in details, or participant names by default.
  - Does not use empty-room `Add coworkers` wording.

- Active-meeting behavior:
  - In two-plus-participant state, localized narration remains active-meeting wording.
  - No stale empty-room Japanese text is spoken after adaptive rewriting.
  - The step does not imply current participants are absent, incomplete, or safe to identify.

- Modal cleanup:
  - The Invite others dialog closes by X or Cancel before the next toolbar step.
  - A lingering modal, blocked toolbar, or cleanup path that presses `Invite` or copies details is a failure.
  - Manual validation uses a disposable meeting and does not enter real names, emails, or external addresses.

- Suggested focused checks after implementation:

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ja
pytest tests\unit\test_material_packages.py -k "japanese_invite or japanese_demo"
pytest tests\unit\test_adaptive_demo.py
```

If existing tests are adjusted by another owner, they should assert the active-meeting/privacy wording rather than only checking that Japanese text exists.

## Recommendation

Proceed as a narrow narration-only slice if the Japanese line clearly separates toolbar `Invite` from empty-room `Add coworkers`, treats invite links and meeting details as private, and leaves sending/copying/reading actions behind explicit user confirmation. This is acceptable risk for localization, but it should not be expanded into locator, alias, or live invite behavior changes in the same pass.

## Changed Files

- `docs/agent-handoffs/cycle-063-risk-scan.md`
