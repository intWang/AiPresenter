# Cycle 062 Risk Scan: `explain-add-coworkers` JA Narration

Date: 2026-05-16

## Scope

Assess risks for adding Japanese `localizedText.ja` narration to `packages/ringcentral-video.yaml` -> `meeting-controls-tour` -> `explain-add-coworkers`.

Only this handoff document was edited. The scan read targeted local context:

- `packages/ringcentral-video.yaml`
- `docs/knowledge/ringcentral-video/privacy-matrix.md`
- `docs/knowledge/ringcentral-video/observation-log.md`
- `docs/knowledge/ringcentral-video/locator-matrix.md`
- recent Cycle 060/061 handoffs where relevant

## Risk List

1. **Contacts and directory suggestion exposure**
   - The `Add coworkers` entrypoint opens the Invite others dialog, which includes a name/email field and suggestions.
   - Japanese narration must not read, summarize, or imply verification of visible contact names, email addresses, directory suggestions, or account/profile details.
   - Directory suggestions can contain coworkers who are not in the meeting and may be sensitive even when visible.

2. **Invite link and meeting detail leakage**
   - The dialog includes `Copy meeting link`.
   - The privacy matrix treats invite links, meeting IDs, dial-in details, names, and emails as private by default.
   - Narration that says "copy the link" too operationally can sound like the presenter will copy or disclose a private meeting link.

3. **Accidental invitation risk**
   - The dialog has an `Invite` action after search/suggestion selection.
   - The Japanese text must describe the workflow without selecting a person, entering text, pressing Invite, or implying that an invite will be sent during the tour.
   - This risk is higher than purely explanatory controls because a click or typed query could affect external people.

4. **External participant boundary risk**
   - The UI supports name/email entry, so the workflow may invite people outside the current meeting and possibly outside the organization depending on tenant settings.
   - Avoid wording that says "anyone" or "external guests" can be added unless the product state, tenant policy, and user intent are verified.
   - Keep the line to "coworker search / invite dialog" rather than promising cross-organization invitation behavior.

5. **Focus-stealing modal/popover risk**
   - `Add coworkers` opens a modal dialog and presenter notes say it blocks the toolbar until closed.
   - If narration is too long, or if cleanup is missed, the next tour step can operate against a covered toolbar and fail.
   - The modal should be closed via dialog X or Cancel before touching other meeting controls.

6. **Empty-room state and adaptive invite boundary**
   - `Add coworkers` is an empty-room callout and should be skipped when participant tiles or participant counts show others are already present.
   - The nearby `explain-invite` step opens the same invite flow from the toolbar and is the regular active-meeting entrypoint.
   - Japanese wording for `explain-add-coworkers` must not make stale empty-room claims when runtime adaptation rewrites active-meeting behavior to toolbar Invite.

7. **Duplication/confusion with `explain-invite`**
   - `explain-add-coworkers` and `explain-invite` share the same Invite others dialog but have different teaching roles.
   - `explain-add-coworkers` should be framed as the empty-meeting callout.
   - `explain-invite` should remain the toolbar/active-meeting entrypoint. Do not collapse the two narrations into identical Japanese text unless tests and adaptive behavior explicitly account for that.

8. **Localized UI mismatch risk**
   - Existing entrypoints match English UI labels such as `Add coworkers` and `Invite`; live localized RingCentral UI labels are not established here.
   - Adding Japanese narration does not localize the app UI or locator matching.
   - Manual validation should not assume Japanese UI labels are available or that locator evidence transfers across locale, DPI, or window variants.

## Mitigations

- Keep the implementation narration-only: add only `narration.localizedText.ja` under `explain-add-coworkers`; do not edit entrypoints, open steps, cleanup behavior, action timing, aliases, Q&A, tests, or runtime adaptation unless a later implementation task explicitly asks.
- Preserve the product label `Add coworkers` in the Japanese narration so the spoken script maps to the visible control.
- Phrase the dialog as a place where the user can search for coworkers or access invite options. Avoid saying the presenter will copy, send, read, select, enter, or invite.
- Include a privacy boundary: do not read invite links, emails, contact names, or suggestion lists unless the user explicitly asks and the content has been verified.
- Keep the external participant story neutral. Avoid promising that external guests can be invited; say "coworkers" or "people invited by the user" only if needed.
- Keep the narration short enough for `placement: during` and `actionOffsetMs: 400`; the dialog should be visible briefly and then closed.
- Treat `explain-add-coworkers` as the empty-room entrypoint and leave `explain-invite` as the active-meeting toolbar entrypoint.
- If runtime adaptation rewrites Add coworkers to Invite in active meetings, ensure localized Japanese text is also adapted or suppressed so it does not still say "empty meeting" while clicking toolbar Invite.

## Must Verify

- YAML shape:
  - `localizedText.ja` is added under `meeting-controls-tour` -> `explain-add-coworkers` -> `narration`.
  - Existing English text, Chinese `localizedText.zh`, `placement: during`, and `actionOffsetMs: 400` remain unchanged.
  - No `localizedText.ja` is accidentally added to `explain-invite` in this slice unless separately requested.

- Text safety:
  - Includes `Add coworkers`.
  - Identifies the dialog as the empty-meeting invite entrypoint.
  - Avoids reading or exposing invite links, emails, names, and suggestion lists.
  - Does not say the presenter copies a link, sends an invite, selects a suggestion, types into search, or adds an external participant.
  - Does not imply directory suggestions are verified coworkers or safe to announce.
  - Does not duplicate active-meeting toolbar wording reserved for `explain-invite`.

- Focus and cleanup:
  - The dialog is closed before the next tour step.
  - A blocked toolbar or lingering Invite others dialog is treated as a failure.
  - Manual validation uses a disposable meeting and does not enter real names, email addresses, or external addresses.

- Boundary with `explain-invite`:
  - `explain-add-coworkers` remains empty-room specific.
  - `explain-invite` remains the regular active-meeting toolbar path.
  - If active-meeting adaptive behavior rewrites the step, Japanese narration must follow the rewritten active-meeting meaning and must not speak stale empty-room text.

- Suggested focused checks after implementation:

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ja
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ja --require-complete
```

If tests are added or already exist for this slice, they should assert privacy wording rather than only checking that Japanese text exists.

## Recommendation

Proceed only as a narrow narration-only slice. This step is higher privacy risk than the previous report/top-bar localization work because it opens a live invite surface with contacts, suggestions, invite links, and an action that can affect other people. The risk is manageable if the Japanese narration stays descriptive, keeps `Add coworkers` tied to the empty-room callout, does not read or act on private invite content, and leaves the active-meeting toolbar story to `explain-invite`.

## Changed Files

- `docs/agent-handoffs/cycle-062-risk-scan.md`
