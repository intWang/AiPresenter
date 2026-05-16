# Cycle 105 Demand Analysis: Japanese Sensitive More-Menu Questions

## Recommendation

Introduce and document an answer-only policy for executable but sensitive More-menu informational entrypoints before adding Japanese Notes or Transcript aliases.

Japanese users should be able to ask location, status, and how-to questions about Notes, Transcript, and recording-related controls. Those questions are useful in a demo and likely in real meetings, but they should not trigger UI operations. Treat the question-response path as informational unless the user explicitly enters an operation flow with confirmed intent and the visible UI state supports it.

Recommended next implementation slice:

- Add a runtime answer-only policy for sensitive informational question routes, starting with `ringcentral.video.more.notes` and keeping `ringcentral.video.more.recording` covered.
- Keep Japanese Notes/Transcript `questionAliases.ja` out of package YAML until that policy is tested.
- Prefer localized Q&A and runtime guards for natural Japanese phrasing before expanding package-owned aliases.
- Keep answer text useful for demos: name the likely surface, explain privacy/state boundaries, and say what AiPresenter will not do automatically.

This is a stronger product move than alias expansion alone because it lets Japanese users ask natural questions without accidentally opening a panel that can expose meeting notes, transcript text, or controls that start notes or recording.

## Analysis Inputs

Cycle 104 established the current boundary:

- Recording location aliases were added only because `ringcentral.video.more.recording` has no `openSteps` and remains non-operable.
- Notes and Transcript were deferred because `ringcentral.video.more.notes` can execute open steps and open the Notes and Transcript side panel.
- Japanese recording action, consent, status, and artifact prompts now route to a safety answer instead of becoming operable.

Subagent-style lenses used for this demand analysis:

| Lens | Focus | Demand read |
| --- | --- | --- |
| Product demand | What Japanese users are likely to ask during a RingCentral Video demo or meeting | Users need discovery help for where controls live, what they do, and whether artifacts/status exist. |
| Privacy and consent | What could reveal private content or change meeting state | Notes, Transcript, captions, summaries, recordings, and recording status should not be opened, read, summarized, or asserted from a question alone. |
| Demo usefulness | What helps a presenter answer naturally without derailing the demo | Answer-only responses are useful because they explain the control map while keeping the meeting stable and avoiding consent surprises. |

No callable parallel subagent primitive was available in this session, so these lenses were consolidated into this single handoff.

## Candidate Prompt Classes

### Safe To Answer, Not Operate

These are the highest-demand prompts. They should return localized answer-only responses with `can_operate=False`.

| Class | Example Japanese prompts | Desired behavior |
| --- | --- | --- |
| Location lookup: Notes | `ノートはどこにありますか`; `Notes and Transcript の場所はどこですか` | Explain that Notes opens the Notes and Transcript panel. Do not open the panel from the question path. |
| Location lookup: Transcript | `文字起こしはどこにありますか`; `Transcript はどこですか` | Explain the known discovery surface. Do not read or expose transcript content. |
| Location lookup: recording | `録画ボタンの場所はどこですか`; `Start recording の場所はどこですか` | Explain where Start recording is found. Do not start recording. |
| How-to: safe recording | `会議を録画するにはどうすればいいですか`; `録画を安全に扱うにはどうすればいいですか` | Answer with consent, role, policy, and confirmation requirements. Do not click anything. |
| How-to: notes/transcript | `ノートを使うにはどうすればいいですか`; `文字起こしを確認するにはどうすればいいですか` | Explain the surface and safety boundary. Do not start notes or inspect content. |
| Status/availability | `録画中ですか`; `文字起こしは有効ですか`; `ノートは開始されていますか` | Say AiPresenter cannot assert status unless it is verified in visible context. Do not open panels or infer state. |
| Post-meeting artifacts | `会議後の録画はどこですか`; `要約やインサイトはありますか` | Explain that artifacts depend on generation, enablement, and permissions. Do not claim existence or summarize content. |

### Sensitive But Potentially Useful Later

These have demand, but should remain gated until the product has a clearer explicit-operation model:

- `ノートを開始して`
- `録画を開始して`
- `文字起こしをオンにして`
- `録画を止めて`
- `Transcript を読んで`
- `会議内容を要約して`

These are not pure informational prompts. They can change meeting state or expose private content. A future implementation should require explicit confirmation, role/permission awareness where possible, and verified visible context.

### Low-Value Or Risky Alias Candidates

Avoid using these as Japanese entrypoint aliases:

- Bare nouns: `ノート`, `文字起こし`, `Transcript`, `録画`
- Action fragments: `録画して`, `ノート開始`, `文字起こしオン`
- Content requests: `読んで`, `要約して`, `共有して`
- Indirect More-menu routes that do not answer the specific question: `More`, `その他`, `もっと`

Bare or broad terms are easy to ask, but they blur the difference between finding a control, starting a feature, and inspecting private content.

## Privacy Expectations

Japanese users are likely to expect AiPresenter to distinguish between explaining a control and using it. That distinction matters more for Notes, Transcript, and recording than for ordinary navigation because these features can affect everyone in the meeting or reveal meeting content.

Expected boundaries:

- Do not start, stop, or enable recording from an informational prompt.
- Do not start notes, captions, live transcription, or translation from an informational prompt.
- Do not open the Notes and Transcript panel merely to answer where/status/how-to questions.
- Do not read, quote, summarize, or promise transcript, notes, recording, summary, or insight content without an explicit content request and verified visible context.
- Do not assert current recording, notes, transcript, caption, or artifact status unless the status is visible and verified.
- Do not imply that participant consent, host permission, organization policy, or artifact availability is known.

These expectations should apply regardless of language, but Japanese coverage is the immediate product gap.

## Demo Usefulness

Answer-only handling improves demos in three ways:

- It lets presenters accept natural Japanese questions without pausing to warn that the assistant may click into sensitive UI.
- It keeps demo state stable: no accidental panel opening, recording start, notes start, or visible transcript exposure.
- It gives better narration than no-match fallback: the assistant can explain where to look and why it will not operate automatically.

The ideal answer is not just a refusal. It should be useful: identify the surface, describe the control's purpose, and state the safety boundary in one concise Japanese response.

## Out Of Scope

Do not include these in the next implementation slice:

- Adding Japanese Notes or Transcript `questionAliases.ja` before answer-only runtime tests pass.
- Adding broad Japanese aliases for Notes, Transcript, captions, summaries, insights, or recording.
- Changing package YAML counts as part of the policy-only slice.
- Implementing actual recording, notes, transcript, caption, translation, or post-meeting artifact operations.
- Reading, summarizing, exporting, downloading, or opening post-meeting artifacts.
- Detecting true recording or transcript status from UI state unless a separate visible-state verifier is designed.
- Expanding the policy to all RingCentral Video settings or host controls beyond the sensitive informational surfaces named here.

## Success Criteria For Implementation

Policy behavior:

- Japanese Notes, Transcript, recording, caption/transcription, and post-meeting artifact informational prompts return answer-only responses.
- Responses for sensitive informational prompts have `can_operate=False`.
- `ringcentral.video.more.notes` is non-operable when reached through question answering, even though its scripted tour step may still open the panel.
- `ringcentral.video.more.recording` remains non-operable for all question responses.
- No interrupt step is created from informational Notes, Transcript, or recording prompts.

Routing tests:

- `ノートはどこにありますか` returns a Notes/Transcript answer with `can_operate=False`.
- `文字起こしはどこにありますか` returns a Notes/Transcript answer with `can_operate=False`.
- `Notes and Transcript の場所はどこですか` returns an answer-only Notes/Transcript response.
- `Transcript はどこですか` does not produce an operable Notes route.
- `録画ボタンの場所はどこですか` returns an answer-only recording response.
- `録画中ですか` returns an answer-only response that does not assert status without visible verification.
- `会議後の録画や文字起こしはどこにありますか` remains answer-only and does not claim artifacts exist.

Negative tests:

- `ノートを開始して`, `文字起こしを読んで`, `Transcript を要約して`, `録画を開始して`, and `同意なしで録画して` remain non-operable from question handling.
- Notes/Transcript prompts must not become package-owned Japanese entrypoint aliases in the same slice.
- Existing Japanese recording aliases remain the only Japanese alias expansion from Cycle 104.

Diagnostics and documentation:

- Japanese demo and Q&A localization remain complete.
- Doctor reports no alias duplicates and no new unsafe overlap warning.
- Package YAML counts do not change for the policy-only slice.
- The implementation handoff explicitly records that the runtime policy, not alias expansion, is what makes Japanese sensitive informational questions safe.

## Handoff Notes

Read-only commands used:

- `Get-Content docs/agent-handoffs/cycle-104-summary.md`
- `Get-Content docs/agent-handoffs/cycle-104-demand-analysis.md`
- `rg -n -C 8 "ringcentral\\.video\\.more\\.(notes|recording)|Notes and transcript|Start recording|会議を録画|文字起こし|録画" packages\\ringcentral-video.yaml`
- `rg -n -C 5 "recording|notes|transcript|answer-only|can_operate|question" src\\ai_presenter\\runtime\\questions.py tests\\unit\\test_questions.py`
- `git status --short`

Observed workspace note:

- `.coverage` was already modified before this doc was written. It was not touched.
