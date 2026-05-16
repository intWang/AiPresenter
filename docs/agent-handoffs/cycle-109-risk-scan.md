# Cycle 109 Risk Scan: Presenter Tone Expansion

## Verdict

Go for a narrow tone expansion only if the implementation keeps tone as a rendering hint, not a policy bypass.

No-go for any change that softens privacy/safety answers, changes operation eligibility, broadens RingCentral action routing, or rewrites localized package copy as part of the tone work. RingCentral Video safety should continue to come from package/runtime gates such as `questionPolicy: answerOnly`, `_can_operate(...)`, Q&A-first matching, and `create_question_interrupt_step(...)`, with tone only affecting phrasing around already-safe text.

## Current Context

- The committed baseline defines canonical tones: `professional`, `conversational`, `concise`, `friendly`, `coach`, `formal`, and `support`.
- Tone aliases already normalize inputs such as `warm` -> `friendly`, `mentor` -> `coach`, and `calm`/`steady`/`reassuring` -> `support`.
- English tone rendering can prepend helper phrases. Chinese rendering has tone-specific prefixes for some tones. Japanese and localized narration mostly preserve authored localized text except `concise`, which truncates to the first sentence.
- Q&A localized answers bypass tone transformation when a localized answer exists. This is a useful safety property because RingCentral privacy answers keep their authored boundaries.
- Concurrent working-tree edits now include an in-progress `careful` tone in `src/ai_presenter/runtime/voice.py`, matching test expectations for aliases such as `safety`, `privacy`, `guarded`, `safe`, and `compliance`. Do not overwrite those edits; review this scan against that active implementation before merging.

## Risks By Severity

| Severity | Risk | Failure mode | Impact | Guardrail |
| --- | --- | --- | --- | --- |
| P0 | Safety answer softening | Friendly, support, coach, or new careful/privacy tone prepends reassuring language before a hard privacy boundary, e.g. "Happy to help" before "I cannot read chat unless..." | Users may hear permission or willingness before the safety limit, especially in live RingCentral Video. | For privacy/safety Q&A, keep authored localized answers unchanged or prepend only explicit boundary language such as "Safety note."; never lead with casual reassurance. |
| P0 | Tone changes operation eligibility | A new tone branches into question handling or controller flow and changes `can_operate`, interrupt-step creation, `questionPolicy`, or risky-word behavior. | Tone selection could make a blocked control appear operable. | Keep `PresenterVoiceSettings.tone` out of route authorization. Tests should assert the same entrypoint, `can_operate`, and interrupt result across all tones for risky prompts. |
| P0 | Localized safety regression | New English prefixes are applied to Chinese/Japanese localized Q&A or narration, or concise truncates away the second sentence containing consent/privacy conditions. | Localized RingCentral demos may become awkward, unsafe, or incomplete. | Localized Q&A answers should remain exact authored copy. For localized narration, allow only known safe transforms; add negative tests where the first sentence alone is insufficient. |
| P1 | CLI/controller compatibility drift | `PRESENTER_TONE_CHOICES`, `PresenterTone`, labels, descriptions, aliases, controller labels, `voices`, `doctor`, `demo`, and `controller` accept different tone sets. | Users see a tone in one surface and get "Unsupported presenter tone" elsewhere. | Add tone candidates in one central pass and test normalization, labels, `voices` catalog, dry-run voice labels, controller labels, and unknown-tone rejection. |
| P1 | Alias ambiguity | Aliases such as `safe`, `calm`, `supportive`, `privacy`, or `compliance` could imply regulatory guarantees or collide semantically with support/troubleshooting. | Users may over-trust the tone label or misunderstand its scope. | Label any safety-oriented tone as wording style only. Prefer `careful` as canonical; treat `privacy`/`safety` as aliases, not claims that the app has verified compliance. |
| P1 | Verbosity creep | Coach/support/careful tones add prefaces to already-long RingCentral safety answers. | Live demos become slow and less clear; important boundaries are buried. | Cap safety answer expansion to one short boundary prefix or no prefix. Preserve concise default behavior and test answer length/first sentence for key privacy prompts. |
| P1 | SAPI speech-rate mismatch | New Chinese tones inherit default SAPI rate accidentally or are grouped with slow/reassuring tones without review. | Chinese narration can sound either too rushed for safety content or too slow for live control tours. | Update `sapi_rate_for_voice(...)` deliberately for every new canonical tone and add a rate assertion. |
| P2 | Public catalog noise | `ai-presenter voices` lists too many aliases or non-ASCII content in a legacy Windows console. | CLI output becomes hard to scan or fails ASCII-safe expectations. | Keep alias lists short, ASCII-safe in CLI rendering, and sorted by canonical groups. |
| P2 | Scope creep into package YAML | Tone expansion pulls in Q&A rewrites, new RingCentral aliases, or demo flow copy changes. | Review becomes harder and safety/localization counts shift unexpectedly. | Keep Cycle 109 runtime/tests/docs only unless a separate package-copy task is approved. |
| P2 | Test-only mismatch persists | Tests expecting `careful` land without runtime changes, or runtime changes land without matching CLI/controller tests. | The suite fails or, worse, a tone is partially available. | Treat test/runtime parity as a release gate; run the focused voice/CLI/controller suite before go-live. |

## Tone Candidate Evaluation

| Candidate | Recommendation | Value | Main risk | Required behavior |
| --- | --- | --- | --- | --- |
| `careful` | Go, best next canonical tone | Names boundary-aware delivery without promising compliance. Fits privacy, recording, transcript, meeting-info, invite, and chat answers. | Can become verbose or overly legalistic. | English prefix should be short, e.g. "Safety note."; Chinese prefix must be localized; Japanese/localized Q&A should avoid English prefixes. |
| `privacy` | Alias only | User-friendly way to ask for privacy-aware wording. | Sounds like a policy mode or data-protection guarantee. | Normalize to `careful`; catalog description must clarify phrasing style only. |
| `safety` / `safe` | Alias only, with caution | Natural operator term for demos with risky controls. | "safe" can imply the operation itself is safe. | Normalize to `careful`; do not alter `can_operate` or safety gates. |
| `guarded` | Alias only | Good internal/user shorthand for restrained boundary-first output. | Could sound defensive or unnatural if surfaced as label. | Normalize to `careful`; do not list as the primary UI label. |
| `compliance` | Defer or alias only after wording review | Useful for enterprise demos where policy language matters. | Implies legal/regulatory compliance AiPresenter has not verified. | If kept, normalize to `careful` and describe as "policy-aware wording", not compliance validation. |
| `empathetic` | Defer | Could improve support-style recovery answers. | Too soft for consent/privacy boundaries; overlaps `friendly` and `support`. | Revisit only with concrete UX examples and safety prompt tests. |
| `executive` | Defer | Could make demos crisper for stakeholder briefings. | Mostly presentation style, not RingCentral safety-specific. | Prefer future style work; do not mix with safety tone expansion. |
| `technical` | Defer | Helpful for admin/troubleshooting demos. | Could encourage extra detail and over-explain sensitive states. | Treat as separate diagnostics/training tone later. |

## Negative Test Matrix

| Area | Prompt or command | Tone(s) | Expected result |
| --- | --- | --- | --- |
| Unknown tone rejection | `ai-presenter demo ... --tone shouty --dry-run` | `shouty` | Nonzero / `BadParameter`; runtime is not called. |
| Default behavior | `PresenterVoiceSettings()` | default | Still `language == "en"` and `tone == "professional"`. |
| Alias normalization | `PresenterVoiceSettings(tone="privacy")` | `privacy` | Normalizes to `careful`; label renders `Careful`; aliases are public and complete. |
| CLI catalog | `ai-presenter voices` | all tones | Lists `Careful aliases:` and remains ASCII-safe. |
| Controller label | `render_voice_label(PresenterVoiceSettings(tone="safety"))` | `safety` | Renders `English / Careful`; no controller-only label drift. |
| Profile validation | `doctor --profile ringcentral-video --language zh-CN --tone privacy` | `privacy` | Fails for incompatible fake speech provider before runtime, same as `friendly`; no special bypass. |
| Demo dry run | `demo --profile ringcentral-video-bind-speaker ... --tone privacy --dry-run` | `privacy` | Loads `English / Careful` or selected localized label and validates profile compatibility. |
| Safety Q&A route parity | "Can the presenter read meeting messages or participant names?" | professional, friendly, support, careful | Same `entrypoint_id`, same `can_operate=False`, no interrupt step; answer keeps explicit privacy boundary. |
| Recording route parity | "recording"; "How do I handle meeting recording safely?" | professional, support, careful | Same non-operable recording route/safety Q&A; no language that implies AiPresenter can start recording. |
| Notes/transcript privacy | "Read the transcript"; Chinese/Japanese equivalents from Cycle 108 coverage | professional, careful | Safety answer or answer-only route; `entrypoint_id is None` where current safety Q&A expects it; no interrupt step. |
| Meeting information privacy | "meeting information"; "meeting link"; localized equivalents | friendly, careful | Still answer-only for meeting info; no fabricated IDs, links, host names, URLs, or phone numbers. |
| Localized Q&A exactness | Chinese/Japanese privacy Q&A prompts | careful/privacy aliases | Localized answer is not prefixed with English text and does not drop required consent/verified-context clauses. |
| Concise safety guard | A multi-sentence safety narration where first sentence names the control and second sentence carries consent/privacy caveat | concise, careful | Do not use `concise` on authored safety copy if it removes the only boundary; add a sentinel or exempt safety-class text. |
| SAPI rate mapping | `sapi_rate_for_voice(PresenterVoiceSettings(language="zh", tone="privacy"))` | privacy/careful | Expected rate is explicit, not accidental. Prefer `0` or `-1` only after listening/review. |
| Logging privacy | Answer private prompt under new tone | careful | Logs canonical `tone=careful` but not raw question text or answer text. |

## Go / No-Go

Go if Cycle 109 is limited to a single canonical safety-oriented tone, preferably `careful`, plus aliases, labels, descriptions, tone rendering, SAPI rate mapping, and focused tests.

No-go if the proposal includes package YAML rewrites, new RingCentral question aliases, changes to Q&A matching, changes to `questionPolicy`, broad prompt rewriting, or any "tone mode" that influences whether an operation can be demonstrated.

No-go if localized safety answers become longer, softer, or less direct than the current authored copy. For RingCentral Video, the safety boundary must remain audible before any helpful elaboration.

## Guardrails

- Keep tone resolution centralized in `runtime.voice`; avoid scattering accepted strings across CLI/controller/runtime.
- Add any canonical tone to `PresenterTone`, `PRESENTER_TONE_CHOICES`, `_TONE_DESCRIPTIONS`, `_TONE_LABELS`, `_TONE_ALIASES`, `render_presenter_text(...)`, `_render_chinese(...)` if needed, and `sapi_rate_for_voice(...)`.
- Keep localized Q&A answers exact. If localized narration needs tone treatment, apply only safe transforms already covered by tests.
- Keep safety boundaries short and front-loaded. Do not prepend "Happy to help", "Sure", or "Let's walk through it" to refusal, consent, transcript, recording, chat, participants, invite, meeting-info, or shared-screen safety answers.
- Preserve all existing RingCentral diagnostic/localization counts unless a separate package change is explicitly approved.
- Do not alter production code or tests while this risk scan is being written; current test edits are owned by another actor.

## Review Checklist

- Confirm the final diff touches only the intended runtime/test/docs files for an implementation cycle; for this scan, only `docs/agent-handoffs/cycle-109-risk-scan.md`.
- Confirm no user or agent edits are overwritten; current dirty files include `src/ai_presenter/runtime/voice.py`, test expectations for `careful`/`privacy`, and a cycle 109 demand-analysis doc.
- Confirm every new canonical tone appears in labels, descriptions, aliases, CLI choices, controller choices, and voice catalog output.
- Confirm unsupported tone validation still fails before runtime for `demo`, `controller`, `voices`, and `doctor`.
- Confirm `ai-presenter voices` remains ASCII-safe for legacy Windows console output.
- Confirm voice profile validation remains language/provider based and does not special-case safety tones.
- Confirm `answer_question(...)` route, `can_operate`, and `create_question_interrupt_step(...)` results are identical across tones for recording, notes/transcript, meeting info, invite, share, chat, and participants prompts.
- Confirm localized Chinese and Japanese privacy/safety answers do not receive English prefixes.
- Confirm concise behavior cannot strip the only sentence containing consent, verified-context, or explain-only boundaries.
- Confirm logs include canonical tone names but do not include raw private prompt text or answer text.
- Confirm focused verification includes `tests/unit/test_voice.py`, `tests/unit/test_cli.py`, `tests/unit/test_controller.py`, and `tests/unit/test_questions.py`.

## Handoff Recommendation

Proceed with the careful-tone slice only if the in-progress runtime/test work stays narrow. The safest next step is to finish one canonical `careful` tone with `privacy`, `safety`, `safe`, `guarded`, and maybe `compliance` aliases; keep route authorization untouched; and prove by tests that RingCentral privacy/safety answers remain exact, direct, and non-operable where they are non-operable today.
