# Cycle 108 Demand Analysis: Chinese Notes/Transcript Safety Routing

## Scope

Analyze Chinese user demand for Notes/Transcript prompts in the RingCentral Video package after Cycle 107 hardened English and Japanese action/content routing.

This handoff covers question-routing behavior only. It does not propose production edits in this cycle. The implementation target is to prevent Chinese Notes/Transcript action or content requests from being treated as ordinary Notes panel location lookups, while preserving existing safe location questions and unrelated routes.

## Recommendation

Extend the Cycle 107 safety boundary to Chinese. Chinese prompts that ask AiPresenter to start notes, start transcription, click `Start notes`, read transcript text, summarize notes/transcripts, create minutes, copy/export/save content, or otherwise handle private Notes/Transcript artifacts should route to an answer-only safety Q&A or no-match. They should not associate with `ringcentral.video.more.notes`.

Preserve Chinese location discovery. Prompts such as `转录在哪里`, `会议笔记在哪里`, and `笔记和转录在哪里` are legitimate "where is the panel?" questions and may continue to return the Notes/Transcript location answer with `entrypoint_id == "ringcentral.video.more.notes"`, `can_operate=False`, and no interrupt step.

Do not let the Chinese guard steal legitimate Start meeting requests. A prompt should only enter this safety bucket when it contains a Notes/Transcript subject, not merely a start verb such as `开始` or English `start`.

## Representative Chinese Prompt Matrix

| Prompt type | Representative prompts | Recommended behavior |
| --- | --- | --- |
| Notes/Transcript location | `转录在哪里`; `会议笔记在哪里`; `笔记和转录在哪里`; `Notes and Transcript 在哪里`; `转录入口在哪里` | Keep Notes/Transcript location help. `ringcentral.video.more.notes` association is acceptable because the user is asking where the panel is. No operation, no interrupt. |
| Live transcription/captions location | `实时转录在哪里`; `字幕在哪里`; `怎么翻译字幕` | Preserve existing captions/live transcription/translation Q&A. No related entrypoint, no operation, no interrupt. |
| Post-meeting artifact location | `会后转录在哪里`; `会议摘要和洞察在哪里`; `会后录制在哪里` | Preserve post-meeting artifact Q&A. Do not claim artifacts exist or read/summarize them. |
| Start notes action | `开始会议笔记`; `启动会议笔记`; `开始笔记`; `点击开始笔记`; `帮我点 Start notes`; `点击 Start notes` | Route to safety Q&A or no-match. Do not open Notes as if the action were approved; do not click `Start notes`. |
| Start/open transcription action | `开启转录`; `打开转录`; `启动实时转录`; `开始转录` | Route to safety Q&A or no-match unless the prompt is clearly a location question. Do not start transcription. |
| Read/summarize content | `读取转录内容`; `读一下转录内容`; `总结会议笔记`; `总结转录`; `帮我总结会议转录`; `朗读会议笔记` | Route to safety Q&A or no-match. Do not associate with `ringcentral.video.more.notes`; do not imply content is visible or accessible. |
| Create/copy/export/save content | `生成会议纪要`; `创建会议摘要`; `复制转录内容`; `导出转录`; `保存会议笔记` | Route to safety Q&A or no-match. Treat as content/artifact handling, not panel location. |
| Recording from Notes panel | `点一下 Also record this meeting`; `顺便录制这场会议` | Keep non-operable. Prefer existing recording safety behavior if it matches; otherwise safety Q&A/no-match is acceptable. Do not route as Notes location. |
| Bare ambiguous terms | `转录`; `会议笔记`; `笔记`; `会议纪要` | Conservative behavior. Location-only answer or clarification is acceptable, but these must not become operable or imply content access. |
| Legitimate meeting start | `start meeting`; `开始会议` if Chinese Start meeting support is later added | Preserve existing/future Start meeting behavior. Do not classify as Notes/Transcript unless a Notes/Transcript subject is present. |

## Recommended Behavior By Prompt Type

Location prompts should remain helpful and answer-only: identify the Notes and Transcript panel, warn that starting notes can change meeting state, and create no interrupt step.

Action prompts should use intent-aware abstention. Starting notes, transcription, captions, translation, or recording can change meeting state and may require host permissions, meeting policy, and participant consent. AiPresenter should not open the panel or click the action from a question-route match.

Content prompts should be stricter than location prompts. Reading, summarizing, copying, exporting, or saving notes/transcripts is private content access. The answer should not imply AiPresenter can see the content through the route map. Use the existing captions/live transcription/translation safety answer when suitable, because it already says not to start notes/transcription or read caption/transcript content unless an explicit, verified flow exists.

Ambiguous bare terms should remain non-operable. If the matcher keeps treating bare `转录` or `会议笔记` as a panel lookup, the response should sound like location help only. If no-match is chosen instead, a concise clarification is acceptable.

## Product Rationale

Cycle 107 established the right trust boundary for English and Japanese: Notes/Transcript action and content prompts are not just panel lookups. They involve meeting-state changes, consent-sensitive transcription/recording behavior, or private meeting content.

Chinese users have the same expectation. Leaving `总结转录`, `读取转录内容`, or `总结会议笔记` as incidental Notes matches is operationally safe today because `ringcentral.video.more.notes` is answer-only, but it gives the wrong semantic answer. It can make AiPresenter sound as if opening the panel is a reasonable response to a content request.

The package already contains Chinese safety language for Notes/Transcript, captions, live transcription, translation, and post-meeting artifacts. Runtime routing should expose that safety language to Chinese users instead of relying on broad Notes aliases.

## Non-Goals

- Do not edit production code or tests as part of this demand-analysis handoff.
- Do not make Chinese Notes/Transcript action prompts operable.
- Do not add transcript scraping, OCR, content extraction, export, save, or meeting-summary generation.
- Do not remove existing Chinese Notes/Transcript location aliases.
- Do not change the `ringcentral.video.more.notes` demo route, `openSteps`, cleanup behavior, or `questionPolicy: answerOnly`.
- Do not broaden this into a general Chinese NLU classifier.
- Do not change unrelated routes such as Chat, Participants, Recording, Captions, Translation, or Start meeting except as needed in a future implementation to stop clear Chinese Notes/Transcript unsafe prompts from winning the wrong route.

## Acceptance Criteria

A future implementation satisfies this demand analysis when:

- `转录在哪里`, `会议笔记在哪里`, and `笔记和转录在哪里` still answer as Notes/Transcript location help, remain `can_operate=False`, and produce no question interrupt step.
- `实时转录在哪里` still uses the captions/live transcription/translation Q&A with no related entrypoint.
- `会后转录在哪里` still uses the post-meeting artifacts Q&A with no related entrypoint.
- `开始会议笔记`, `启动会议笔记`, `开始笔记`, `帮我点 Start notes`, and `点击 Start notes` return safety Q&A or no-match, do not associate with `ringcentral.video.more.notes`, remain `can_operate=False`, and produce no question interrupt step.
- `读取转录内容`, `总结会议笔记`, `总结转录`, `复制转录内容`, `导出转录`, and `保存会议笔记` return safety Q&A or no-match, do not associate with `ringcentral.video.more.notes`, remain `can_operate=False`, and produce no question interrupt step.
- Legitimate Start meeting requests remain unchanged. A Chinese guard must require a Notes/Transcript subject term so `start meeting` and any future `开始会议` route are not treated as Notes/Transcript safety prompts.
- English and Japanese Cycle 107 behavior remains unchanged.
- Package alias counts, Q&A counts, demo flow shape, and localization coverage remain stable unless a future implementation explicitly justifies a package-data change.

## Handoff Notes For Implementation

- Prefer a narrow runtime/test parity slice with Cycle 107 over YAML alias expansion.
- Extend the existing Notes/Transcript safety matcher with Chinese subject terms such as `会议笔记`, `笔记`, `转录`, `字幕记录`, and `会议纪要`, paired with Chinese action/content terms such as `开始`, `启动`, `开启`, `打开`, `点击`, `读取`, `读`, `朗读`, `总结`, `内容`, `复制`, `导出`, `保存`, `生成`, and `创建`.
- Exclude location intent before safety routing. Cover common Chinese location wording: `在哪里`, `在哪`, `哪里`, `位置`, `入口`, and `怎么找到`.
- Keep recording-specific prompts on the recording safety path when possible. Do not let a broad `记录` or `录制` term turn ordinary recording questions into Notes/Transcript responses.
- Use Unicode-safe test fixtures, preferably `\u` escapes where shell encoding is ambiguous.
- Assert both `response.entrypoint_id is None` and `create_question_interrupt_step(...) is None` for Chinese action/content safety prompts.
- Keep sentinel tests for preserved behavior: Notes location, live transcription location, post-meeting artifacts, English/Japanese Cycle 107 prompts, and legitimate Start meeting.

Read-only probe context from the current tree: Chinese prompts such as `开始会议笔记`, `读取转录内容`, `总结会议笔记`, and `总结转录` can still associate with `ringcentral.video.more.notes` while remaining non-operable and producing no interrupt. Mixed `点击 Start notes` already tends to hit the Cycle 107 safety path because of the English `Start notes` phrase, and should stay answer-only.
