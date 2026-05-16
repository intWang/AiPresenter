# Cycle 022 Demand Analysis: RingCentral Chinese Q&A Content Expansion

Date: 2026-05-16
Role: demand-analysis worker
Write scope: this file only

## Read Scope

Reviewed local repository context only:

- `packages/ringcentral-video.yaml`
- `src/ai_presenter/runtime/questions.py`
- `src/ai_presenter/runtime/voice.py`
- `src/ai_presenter/packages/models.py`
- `tests/unit/test_questions.py`
- `tests/unit/test_voice.py`
- `tests/unit/test_material_packages.py`
- `README.md`
- `docs/runbooks/ringcentral-manual-acceptance.md`
- `docs/superpowers/specs/2026-05-14-ringcentral-video-material-package-design.md`
- `docs/superpowers/specs/2026-05-16-localized-qa-aliases-design.md`
- `docs/knowledge/ringcentral-video/validation-checklist-index.md`
- `docs/knowledge/ringcentral-video/evidence-index.md`
- `docs/knowledge/ringcentral-video/privacy-matrix.md`
- Cycle handoffs for 009, 011, 012, 016, 020, and 021

No production code, package YAML, tests, runbook, or knowledge docs were edited.

## Content Gaps

The runtime is ready for a package-authored content slice, but the RingCentral package only uses a
small part of it today.

- `packages/ringcentral-video.yaml` has only three `qa` entries. Only `How do I protect my real
  background?` has `localizedQuestions.zh` and `localizedAnswers.zh`.
- Existing English Q&A covers background privacy, shared-screen content, and inviting people. It
  does not yet cover audio/camera readiness, chat/participant privacy, network quality, notes and
  transcript safety, recording safety, or the first-one-here Add coworkers path.
- Package-owned `questionAliases.zh` currently exist only for Background settings, Share, Invite,
  Chat, and Leave. Key observed routes such as Participants, microphone/camera, audio/video menus,
  network quality, meeting information, Notes, and Recording still depend on the legacy Python alias
  fallback or English token matching.
- `runtime.questions` matches package Q&A first, then entrypoint aliases, then token scoring. It
  does not consult `explainers`, so live controller Q&A usefulness must primarily come from `qa`
  and `questionAliases` unless runtime logic changes later.
- `Explainer` content is complete enough for coverage diagnostics, but it is English-only and has
  no localized or tone-specific schema. Refining explainer wording is useful as package knowledge,
  but it will not make `answer_question()` produce richer answers by itself.
- Chinese localized Q&A answers bypass `render_presenter_text()`, so selected tone does not add the
  existing friendly/coach/formal Chinese prefixes. Tone-sensitive Chinese usefulness must be handled
  by writing answers that are naturally usable across tones, or by adding separate Q&A entries for
  explicit user intents such as quick answer versus step-by-step guidance.

## Recommended Scope

Recommended Cycle 022 implementation slice: edit package content and focused content tests only.
Do not change runtime matching, package schema, controller behavior, CLI behavior, or safety policy.

In scope:

- Enrich the two existing unlocalized Q&A entries with `localizedQuestions.zh` and
  `localizedAnswers.zh`.
- Add four or five new Q&A entries for the highest-value RingCentral routes:
  audio/video readiness, chat/participant privacy, network quality troubleshooting, notes/transcript
  versus recording, and first-one-here Add coworkers/invite behavior.
- Add package-owned `questionAliases.zh` for a small set of P0/P1 and runbook routes that users are
  likely to ask about in Chinese.
- Keep answers grounded in existing entrypoints, presenter notes, privacy matrix, and validation
  evidence. The package should explain where controls live and what is safe, not claim live
  acceptance or read private content.
- Add focused assertions in a later implementation cycle proving package loading, localized Q&A
  matching, alias matching, and unchanged `can_operate` behavior.

Preferred small file set for future implementation:

- `packages/ringcentral-video.yaml`
- `tests/unit/test_questions.py`
- `tests/unit/test_material_packages.py`
- implementation handoff only, if that cycle records one

## Target Entrypoints And Questions

Prioritize content that helps the controller answer real operator questions while staying inside
known route and privacy boundaries.

| Intent | Entrypoints | Recommended Q&A shape |
| --- | --- | --- |
| Bring people in from an empty room or toolbar | `ringcentral.video.main.add-coworkers`, `ringcentral.video.toolbar.invite` | Localize the existing invite Q&A and add Chinese phrasings like `怎么邀请同事入会`, `我是第一个人怎么拉人`, and `怎么复制会议邀请`. Answer should mention Add coworkers for empty-room state and Invite for the toolbar, while not reading links or suggestions. |
| Chat and participant privacy | `ringcentral.video.toolbar.chat`, `ringcentral.video.toolbar.participants` | Add `Can the presenter read chat or participant names?` with Chinese variants like `你能读聊天内容吗` and `能说出参会人名字吗`. Answer: explain panels and counts, but do not read messages, names, roles, or private tabs unless explicitly asked and verified. |
| Audio and camera readiness | `ringcentral.video.toolbar.audio`, `ringcentral.video.toolbar.audio-menu`, `ringcentral.video.toolbar.video`, `ringcentral.video.toolbar.video-menu` | Add `How do I make sure my audio and camera are ready?` with Chinese variants like `怎么检查麦克风和摄像头` and `开会前怎么确认声音视频`. Answer: check mute/camera state first, then use menus for device recovery; do not toggle real meeting media without intent. |
| Connection troubleshooting | `ringcentral.video.top.network-quality`, optionally `ringcentral.video.top.report-issue` | Add `How do I troubleshoot choppy audio or video?` with Chinese variants like `声音或视频卡顿怎么办` and `怎么看网络质量`. Answer: use Network quality for packet loss/jitter/latency context and Report issue for escalation; avoid overdiagnosing without observed values. |
| Notes, transcript, and recording | `ringcentral.video.more.notes`, `ringcentral.video.more.recording` | Add `Where are notes, transcripts, and recording controls?` with Chinese variants like `笔记和转录在哪里` and `怎么录制会议`. Answer: Notes opens the notes/transcript panel; recording changes meeting state and requires confirmation/consent. Do not start notes or recording by default. |
| Shared-screen boundary | `ringcentral.video.toolbar.share` | Localize the existing shared-screen Q&A with Chinese variants like `你能说明共享屏幕内容吗` and `能读共享的文档吗`. Answer: only describe shared content after approved observation and user permission; the Share picker itself can be explained safely. |

Recommended alias additions:

- `ringcentral.video.main.add-coworkers`: `加同事`, `邀请同事`, `拉人入会`, `我是第一个人怎么邀请`
- `ringcentral.video.toolbar.participants`: `参会者`, `参会人列表`, `成员`, `谁在会议里`
- `ringcentral.video.toolbar.audio`: `麦克风`, `静音`, `取消静音`, `声音`
- `ringcentral.video.toolbar.audio-menu`: `音频设置`, `换麦克风`, `换扬声器`, `电话音频`
- `ringcentral.video.toolbar.video`: `摄像头`, `开视频`, `关视频`, `视频开关`
- `ringcentral.video.toolbar.video-menu`: `视频设置`, `换摄像头`, `摄像头菜单`
- `ringcentral.video.top.network-quality`: `网络质量`, `连接质量`, `卡顿`, `延迟`
- `ringcentral.video.top.meeting-info`: `会议信息`, `会议号`, `会议链接`
- `ringcentral.video.more.notes`: `笔记`, `转录`, `会议笔记`, `字幕记录`
- `ringcentral.video.more.recording`: `录制`, `录像`, `记录会议`

Do not remove the legacy alias table in this slice. Treat these as package-owned migration for
high-value routes only.

## Tone And Language Principles

- Keep canonical language support to English and Chinese. Regional aliases such as `zh-CN` already
  normalize to `zh`; this content slice should not add new language families.
- Use real authored Chinese, not word-for-word English replacement. Prefer short spoken sentences
  that sound natural in a live demo.
- Do not add new YAML fields for tone-specific answers. Current schema supports localized answers,
  not per-tone answer variants.
- For English answers, existing tone rendering can add friendly, coach, formal, conversational, or
  concise wrappers. Keep the base answer factual so those wrappers do not distort meaning.
- For Chinese localized answers, write copy that survives all selected tones because runtime returns
  the localized answer directly. If a question itself asks for coaching, make that Q&A entry
  step-by-step in both languages.
- Keep safety words explicit in every privacy-sensitive answer: explain, summarize, ask, confirm,
  verified, private, consent.
- Avoid claims about exact meeting state, attendee identity, content, plan availability, or live
  validation status unless the current package and evidence support them.

## Out Of Scope

- Runtime matching changes, fuzzy semantic search, explainer lookup, or answer-ranking changes.
- Package schema changes for localized explainers or tone-specific Q&A.
- New canonical languages beyond `en` and `zh`.
- Controller UI copy changes, CLI voice changes, provider routing, voice readiness, or TTS asset work.
- Live RingCentral interaction, acceptance evidence promotion, screenshots, UIA capture, or route
  validation.
- New executable open steps, new routes for whiteboard/captions/host controls, or changes to route
  operability.
- Removing the legacy Python alias table.
- Making risky controls executable. Invite, Share, Recording, Notes start actions, and Leave/End
  must remain governed by existing `can_operate` and package safety boundaries.

## Acceptance Criteria

Future implementation should be accepted only if all of the following are true:

- The package still loads with the current schema; no new YAML fields are introduced.
- The RingCentral package has localized Chinese Q&A for the existing shared-screen and invite
  questions.
- At least four new Q&A entries are added for the recommended route groups, each with:
  English `question` and `answer`;
  `localizedQuestions.zh`;
  `localizedAnswers.zh`;
  accurate `relatedEntrypointIds`.
- Package-owned Chinese aliases are added for the selected P0/P1 routes, and the normalized alias
  index exposes them through existing model behavior.
- Focused tests prove representative Chinese questions resolve to the intended entrypoints and, for
  Q&A matches, return Chinese localized answers.
- Risky or privacy-sensitive routes remain non-operable where they are non-operable today:
  invite/add-coworkers, share, recording, and leave/end should not become automatic clicks.
- Safe routes such as Chat, Participants, Network quality, and audio/video menus keep existing
  behavior; content changes should not force runtime policy changes.
- English tone tests do not require new behavior; selected tone may wrap English Q&A through the
  existing `render_presenter_text()` path.
- Chinese localized answers are tested for content, not tone prefixes, because current runtime does
  not apply tone wrappers to localized Q&A answers.
- Existing tests for mojibake rejection, longest package-owned alias wins, package-owned alias
  precedence, and localized background Q&A continue to pass.
- Recommended focused verification for future implementation:
  `tests/unit/test_material_packages.py`, `tests/unit/test_questions.py`, `ruff` on touched files,
  `mypy` if production code is touched unexpectedly, and `git diff --check`.

## Risks

- Tone mismatch risk: Chinese localized answers bypass tone rendering, so users may expect
  `friendly` or `coach` to reshape every Chinese answer when it currently will not.
- Alias collision risk: short aliases like `卡顿`, `声音`, or `设置` can match broad intent. Prefer
  route-specific longer aliases where ambiguity is likely, and rely on longest-alias behavior.
- Privacy regression risk: richer Q&A can accidentally sound like permission to read chat,
  participant names, shared content, notes, or meeting links. Every sensitive answer needs an
  explicit consent and verification boundary.
- Evidence overclaim risk: package answers should not imply live acceptance. Current evidence says
  no executable RingCentral Video route is fully accepted for unattended live operation.
- Encoding risk: future edits must use real UTF-8 Chinese strings. Do not add terminal mojibake as
  a supported alias or expected answer.
- Scope creep risk: whiteboard, captions, host controls, and AI summaries are valid roadmap
  subjects, but the current package lacks dedicated entrypoints. Adding those routes is a separate
  route/evidence cycle.
- Test brittleness risk: assert representative content and entrypoint ids, not full long localized
  paragraphs unless exact phrasing is the product requirement.

## Key Recommendation

Make Cycle 022 a package-content-only expansion centered on Chinese Q&A and package-owned aliases
for Add coworkers/Invite, Chat/Participants, audio/video readiness, Network quality, Notes/Recording,
and Share privacy. This is the smallest useful slice after the voice and controller readiness work:
it improves real question answers without changing runtime logic, provider behavior, or route safety.
