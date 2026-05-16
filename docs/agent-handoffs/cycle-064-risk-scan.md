# Cycle 064 Risk Scan: `explain-participants` JA Narration

Date: 2026-05-16

## Scope

Assess risks for adding Japanese `localizedText.ja` narration to `packages/ringcentral-video.yaml` -> `meeting-controls-tour` -> `explain-participants`.

Only this handoff document was edited. The scan read targeted local context:

- `packages/ringcentral-video.yaml`
- `presenter/skills/ringcentral-safety.md`
- `presenter/memory.md`
- `docs/knowledge/ringcentral-video/privacy-matrix.md`
- recent Cycle 062/063 handoffs where relevant
- focused localization test expectations already present for this slice

## Risk List

1. **Roster identity exposure**
   - The Participants panel can expose participant names and possibly roles.
   - The current English says the panel lets the user "confirm who is in the room"; a Japanese line must not turn that into reading names aloud by default.
   - Names and roles should be treated as private unless the user explicitly asks and the visible content is verified.

2. **Attendee count overclaim**
   - The package notes say Participants can answer attendee count questions, and memory notes say the badge can show the live attendee count in a two-person meeting.
   - A verified visible count may be summarized, but the narration must not infer attendance, absence, identity, or quorum from an unverified panel state.
   - Avoid phrasing that implies AiPresenter knows the full roster beyond the visible, current UI.

3. **Role and host/moderator control ambiguity**
   - The panel may expose role-specific controls or labels for host/moderator areas.
   - The Q&A boundary says host controls can be explained, but muting others, removing people, locking the meeting, changing security, or reading names/roles requires explicit user intent and verified context.
   - Japanese narration should describe where controls live, not imply AiPresenter will operate them.

4. **Invite, lock, mute, and more controls as side-effect surfaces**
   - The observed Participants panel has search, Invite, Lock, Mute, raise-hand, and More controls.
   - Invite can expose names, emails, suggestions, and links; lock and mute can affect the live meeting; More may contain participant-specific actions.
   - A tour line can mention these as control categories, but must not press, toggle, select, mute, invite, lock, remove, admit, or open participant-specific More menus.

5. **Participant-specific More menu leakage**
   - "More options" near a roster item can expose person-specific actions or labels.
   - Opening it during a generic tour could reveal a name/role pairing or produce a meeting action affordance such as remove, promote, mute, or ask to unmute.
   - Keep the slice to opening the panel and explaining categories; do not add behavior that expands a participant row or per-person menu.

6. **Boundary with Chat**
   - Participants and Chat share a side-panel area with separate tabs and separate privacy classes.
   - Chat contains public/private messages; Participants contains names, roles, counts, and meeting controls.
   - The Japanese Participants narration must not mention reading Chat messages, private tabs, or chat content, and the next `explain-chat` step should remain its own privacy slice.

7. **Side panel cleanup and toggle risk**
   - The Participants entrypoint uses `cleanup: toggle`, and presenter notes say to toggle Participants or close the side panel before opening Chat.
   - If the panel remains open, the next Chat step can accidentally toggle the wrong side-panel state, stack tabs, or look like the demo is reading roster content while discussing Chat.
   - Cleanup should return to a stable meeting surface or deliberately switch to Chat without exposing roster values.

8. **Alias/Q&A collision risk**
   - Japanese aliases already exist for the Participants entrypoint, while Q&A also covers "can you read chat or participant names?"
   - Adding narration should not expand aliases or routing behavior; short participant-name queries must continue to hit privacy Q&A rather than blindly opening the roster.
   - This risk is especially important for requests like "read participant names" or "who is here?"

9. **Localized UI mismatch**
   - The visible RingCentral UI labels and locators are still modeled with product labels such as `Participants`, `Chat`, `Invite`, and `Mute`.
   - Japanese narration does not prove the live app is localized or that Japanese labels can be matched.
   - Preserve product labels where useful and do not alter locators or entrypoint matching in this slice.

## Mitigations

- Keep implementation narration-only: add only `narration.localizedText.ja` under `meeting-controls-tour` -> `explain-participants`.
- Preserve the visible product label `Participants` so the spoken line maps to the toolbar control.
- Say the panel shows the roster area and meeting people controls, not that AiPresenter will read names.
- Include a privacy boundary for participant names and roles: do not read them unless the user explicitly asks and visible content is verified.
- Mention attendee count only as a verified visible count, not as inferred identity or attendance.
- Phrase Invite, Lock, Mute, and More as available control areas; avoid active verbs that imply clicking or changing meeting state.
- Do not add Japanese aliases, Q&A, open steps, cleanup behavior, runtime behavior, or tests unless a separate implementation owner explicitly owns that scope.
- Keep Participants separate from Chat. Chat content and private conversations should remain governed by `explain-chat` and the existing privacy Q&A.
- Ensure side-panel cleanup/toggle leaves no lingering roster panel before the tour moves to Chat.

## Must Verify

- YAML shape:
  - `localizedText.ja` is added under `meeting-controls-tour` -> `explain-participants` -> `narration`.
  - Existing English text, Chinese `localizedText.zh`, `placement: during`, and `actionOffsetMs: 350` remain unchanged unless a separate owner explicitly changes them.
  - No entrypoint, locator, `openSteps`, cleanup, aliases, Q&A, runtime, or unrelated flow changes are bundled into this narration slice.

- Text safety:
  - Includes `Participants`.
  - Mentions the roster panel or participant list at a high level.
  - Mentions verified attendee count only as a visible count.
  - Includes a default privacy boundary for participant names and roles.
  - Does not say AiPresenter will read names, identify roles, infer who is present or absent, open private tabs, or inspect Chat messages.
  - Does not say AiPresenter will invite people, lock the meeting, mute others, remove people, admit people, change security settings, or open participant-specific More actions by default.

- Roster/control behavior:
  - Opening Participants is acceptable for the scripted tour, but per-person controls remain explain-only.
  - Host/moderator control language stays descriptive and confirmation-gated.
  - Manual validation uses a disposable meeting and records no participant names, roles, chat content, invite links, emails, or screenshots containing private roster data.

- Side-panel and Chat boundary:
  - The Participants panel is toggled closed or safely switched before the `explain-chat` step.
  - A lingering roster panel while Chat narration plays is a failure unless the UI intentionally shows a tab switch with no private content read aloud.
  - Chat privacy remains in the next slice; do not localize or rewrite `explain-chat` as part of this pass.

- Expected localization movement after implementation:
  - Overall Japanese demo narration should move from `14/51` to `15/51`.
  - `meeting-controls-tour` Japanese narration should move from `7/22` to `8/22`.
  - First missing `meeting-controls-tour` step should advance from `explain-participants` to `explain-chat`.
  - Japanese Q&A and alias counts should remain unchanged.

- Suggested focused checks after implementation:

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ja
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ja --require-complete
pytest tests\unit\test_material_packages.py -k "japanese_participants or japanese_demo"
pytest tests\unit\test_cli.py -k "japanese_demo_and_qa_coverage or japanese_demo_gap"
```

If tests are adjusted by another owner, they should assert privacy wording rather than only checking that Japanese text exists.

## Recommendation

Proceed as a narrow narration-only slice if the Japanese line keeps `Participants` mapped to the visible toolbar control, explains roster/count/control purpose without reading names or roles, and explicitly keeps host/moderator actions confirmation-gated. This is acceptable localization risk, but it should not be batched with Chat or with any alias, runtime, cleanup, or live participant-control behavior changes.

## Changed Files

- `docs/agent-handoffs/cycle-064-risk-scan.md`
