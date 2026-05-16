# Cycle 109 Demand Analysis: Presenter Tone Expansion

## Scope

Identify a small tone expansion for AiPresenter responses that helps RingCentral Video presenters in live demo, training, and Q&A contexts without changing package content, route safety, localization counts, or demo flow behavior.

Current committed runtime voice behavior supports `professional`, `conversational`, `concise`, `friendly`, `coach`, `formal`, and `support`. These tones mostly change deterministic response prefixes, voice instruction text, and Chinese SAPI pacing. Package YAML already carries the safety and localization burden for RingCentral Video, so the next tone slice should stay in shared voice metadata/rendering only.

## Target Users And Use Cases

- Demo operators running a live RingCentral Video walkthrough who need AiPresenter to answer questions without sounding casual around recording, notes, transcript, invite links, participant names, chat content, or shared-screen content.
- Support and enablement teams using AiPresenter as a meeting coach for new hosts who need clear step-by-step guidance without overexplaining every control.
- Multilingual presenters switching EN/ZH/JA output where tone selection should affect style only, not facts, privacy boundaries, or whether an operation is allowed.

## Recommendation

### P0: Add `careful` as a privacy/safety-aware tone

Add one canonical tone: `careful`.

Recommended aliases:

- `careful`
- `safety`
- `safe`
- `privacy`
- `guarded`
- `compliance`

This tone fills a real gap between `support` and `formal`. `support` is recovery-focused for troubleshooting. `formal` is polished and restrained. `careful` should be boundary-focused: calm, explicit about consent, privacy, visible state, and meeting side effects, but still useful as presenter speech.

Best-fit RingCentral surfaces:

- Recording and leave/end meeting.
- Notes, transcript, captions, summaries, and post-meeting artifacts.
- Meeting info, meeting ID, invite links, and participant names.
- Chat content and shared-screen content.
- Host/security controls and any role- or policy-dependent action.

### P1: Add alias-only coaching terms to `coach`

Do not add another canonical tone unless user demand proves it. Add alias-only mappings to the existing `coach` tone:

- `guided`
- `guide`
- `trainer`
- `training`
- `walkthrough`

These match how live operators are likely to ask for a teaching mode. They should normalize to `coach`, reuse the existing controller label `Coach`, and keep the existing step-by-step behavior.

If only one change lands, choose `careful`.

## Example Behavior

| Tone | EN | ZH | JA |
| --- | --- | --- | --- |
| `careful` / `privacy` | `Safety note. Recording affects everyone in the meeting. I can show where Recording is, but I will not start or stop it without explicit confirmation and verified context.` | `我会谨慎说明。Recording 会影响会议中的所有人。我可以说明入口位置，但不会在没有明确确认和可见上下文验证时开始或停止录制。` | `Recording は会議全体に影響します。場所は説明できますが、明確な確認と表示状況の確認なしに開始や停止はしません。` |
| `guided` aliasing to `coach` | `Let's walk through it. First check Microphone, then Camera, then Share.` | `我们一步步来看。先确认 Microphone，再看 Camera，最后看 Share。` | `順番に見ていきます。まず Microphone、次に Camera、最後に Share を確認します。` |

JA deterministic localized text should not receive an English prefix. For JA, the main value is the rendered voice instruction passed to model-backed narration and the controller/CLI label. Existing authored Japanese package text should remain untouched.

## Acceptance Criteria

A future implementation satisfies this demand analysis when:

- `PresenterVoiceSettings(tone="careful").tone == "careful"`.
- `safety`, `safe`, `privacy`, `guarded`, and `compliance` normalize to `careful`.
- `guided`, `guide`, `trainer`, `training`, and `walkthrough` normalize to `coach`.
- `PRESENTER_TONE_CHOICES` exposes `Careful` as a selectable tone, while the new coaching terms remain aliases unless product explicitly wants more UI choices.
- `presenter_tone_description("careful")` describes the tone as privacy-aware, boundary-focused, calm, and consent-aware.
- `render_voice_instruction(PresenterVoiceSettings(language="en", tone="privacy"))` includes English and the careful tone description.
- `render_voice_instruction(...)` also works for `zh` and `ja` without changing provider validation rules.
- English deterministic careful responses use a short prefix such as `Safety note.` and do not rewrite the factual payload.
- Chinese deterministic careful responses use a Chinese prefix such as `我会谨慎说明。` and do not introduce English prefix text.
- Japanese deterministic localized text remains unprefixed by English; `concise` remains the only tone that trims localized text.
- `sapi_rate_for_voice(...)` remains conservative: `careful` can use neutral rate `0`; do not speed up safety-sensitive Chinese narration.
- Existing tones keep their current labels, aliases, descriptions, prefixes, and SAPI rate behavior.
- No changes are made to `packages/ringcentral-video.yaml`, Q&A counts, alias counts, demo flow shape, locator metadata, or localization coverage.

## Non-Goals

- Do not make tone selection change safety decisions, route matching, `can_operate`, cleanup behavior, or whether a question creates an interrupt step.
- Do not add per-tone package narration variants.
- Do not rewrite RingCentral Video localized scripts to sound more careful.
- Do not add playful, salesy, legalistic, urgent, humorous, or emotional-support tones.
- Do not treat `careful` as legal/compliance advice. It is operational meeting caution, not policy judgment.
- Do not add new language support, speech providers, or package content in this tone slice.

## Handoff Notes For Implementation

- Keep the implementation in shared voice metadata and focused tests, likely `src/ai_presenter/runtime/voice.py`, existing controller/CLI voice label paths, and unit tests around voice normalization/rendering.
- The CLI `voices` command should list `Careful aliases:` and remain ASCII-safe by escaping non-ASCII aliases where applicable.
- Controller labels should render `English / Careful`, `Chinese / Careful`, and `Japanese / Careful` through the existing `tone_label(...)` path.
- Use `privacy` as the most important user-facing alias, because recent RingCentral Video cycles repeatedly protected private meeting content and consent-sensitive artifacts.
- Prefer a small deterministic prefix over full text rewriting. The package owns facts and safety content; the tone layer should only frame the response.
- Add regression coverage that `professional`, `conversational`, `concise`, `friendly`, `coach`, `formal`, and `support` still normalize and render exactly as before.
- Add a package-stability check or focused assertion that this slice changes no RingCentral package YAML, localization counts, Q&A counts, or alias counts.
- Workspace note from this analysis: `.coverage` and `tests/unit/test_voice.py` were already modified before this doc-only work began. Coordinate with that in-progress test work before implementing `careful`.
