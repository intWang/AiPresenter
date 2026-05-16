# Cycle 108 Risk Scan: Chinese Notes/Transcript Safety Routing

## Verdict

Go for targeted Chinese Notes/Transcript action and content prompt hardening in the next implementation cycle.

No-go for YAML alias expansion, demo route changes, or making Notes operable from questions. The current runtime remains safe because `ringcentral.video.more.notes` has `questionPolicy: answerOnly`; Chinese action/content prompts that associate with Notes still return `can_operate=False` and create no question interrupt step. The risk is over-association and misleading answer text, not an observed unsafe click.

## Context

Cycle 107 committed `64d7f31 fix: harden notes transcript safety routing`.

That cycle moved English and Japanese Notes/Transcript action/content prompts to the existing captions/live transcription/translation safety Q&A. It preserved location lookups such as `Show me where Notes and Transcript is` and Japanese Notes location aliases.

The remaining gap is Chinese. `src/ai_presenter/runtime/questions.py` now has `_NOTES_TRANSCRIPT_TERMS` and `_NOTES_TRANSCRIPT_ACTION_OR_CONTENT_TERMS` for English and Japanese terms, but not Chinese action/content terms. Meanwhile `packages/ringcentral-video.yaml` has Chinese Notes aliases:

- `笔记`
- `转录`
- `会议笔记`

Those aliases are valid for location discovery, but they also catch Chinese action/content requests such as reading, summarizing, copying, saving, or starting notes.

## Risks By Severity

| Severity | Risk | Failure mode | Impact | Guardrail |
| --- | --- | --- | --- | --- |
| P0 | Start meeting regression | Chinese or mixed prompts such as `点击 Start meeting` or existing English/Japanese `Start meeting` prompts are swallowed by the Notes/Transcript safety matcher because `start` is treated as unsafe whenever CJK click wording appears nearby. | Users lose the legitimate meeting-start route; a safety fix appears to break core routing. | Add positive sentinels for `start meeting`, `点击 Start meeting`, and `Start meeting をクリックして` that still route to `ringcentral.develop.video.start` and remain non-operable. |
| P0 | Unsafe action under-match | Prompts such as `开始笔记`, `启动会议笔记`, `开启转录`, or `点击 Start notes` keep matching `ringcentral.video.more.notes` through aliases/title tokens. | AiPresenter gives a location-style answer to a state-changing request, which can sound like it is ready to start notes/transcription/recording. | Pair Chinese Notes/Transcript subject terms with narrow action terms before entrypoint matching; expect safety Q&A or no-match with `entrypoint_id is None`. |
| P0 | Private content under-match | Prompts such as `读一下转录内容`, `总结转录`, `朗读会议笔记`, `复制转录内容`, or `保存会议笔记` remain Notes entrypoint answers. | Privacy boundary is muddied; the user may believe AiPresenter can read, summarize, copy, or save meeting content from route metadata. | Add content verbs only when paired with Notes/Transcript subjects; assert no content claim, no operation, and no interrupt step. |
| P1 | Location overmatch | Legitimate location prompts such as `笔记和转录在哪里`, `会议笔记在哪里`, `转录入口在哪里`, or `Notes and Transcript 在哪里` are redirected to the safety Q&A. | Safe discovery becomes less useful and Chinese location aliases appear broken. | Check location intent before safety routing with Chinese location terms including `哪里`, `在哪`, `位置`, and `入口`; keep `ringcentral.video.more.notes` acceptable for location. |
| P1 | Q&A shadowing | Broad Chinese terms for `转录`, `记录`, or `摘要` steal existing captions/live transcription, post-meeting artifact, or recording safety Q&A prompts. | More specific safety answers are replaced by a generic Notes/Transcript answer. | Keep Q&A-first ordering; add regression prompts for `实时转录在哪里`, `会后转录在哪里`, `怎么录制会议`, and `记录会议`. |
| P1 | Mixed-language gap | `Start notes 请帮我点击`, `点击 Start notes`, or `帮我点 Also record this meeting` are not covered because the subject is English and the action is Chinese. | The exact prompts likely to happen in localized UI remain noisy or fall to no-match. | Test Chinese action terms paired with English UI labels `Start notes`, `Notes and Transcript`, `Transcript`, and `Also record this meeting`. |
| P2 | Bare-term ambiguity | Bare `笔记`, `转录`, `会议笔记`, or `会议纪要` are interpreted as content intent or operation intent. | The system may become overly cautious or imply capabilities it does not have. | Treat bare terms as location-only answer or clarification; never make them operable. |
| P2 | Encoding false confidence | Terminal probes display CJK fixtures as mojibake, hiding whether tests contain the intended Chinese strings. | Reviewers may approve the wrong literals or miss a broken fixture. | Use UTF-8 source files and `\u` escapes in diagnostics where helpful; do not judge CJK correctness from PowerShell rendering alone. |

## Negative Prompt Matrix

| Prompt class | Example prompts | Current observed route | Expected next-cycle route | Required safety result |
| --- | --- | --- | --- | --- |
| Chinese Notes location lookup | `笔记和转录在哪里`; `会议笔记在哪里` | Notes Q&A / `ringcentral.video.more.notes` | Preserve current route | `can_operate=False`; no interrupt step |
| Chinese captions/live transcription location | `实时转录在哪里`; `字幕在哪里` | Captions/live transcription Q&A, `entrypoint_id=None` | Preserve Q&A-first route | `can_operate=False`; no interrupt step |
| Chinese post-meeting artifacts | `会后转录在哪里`; `会议摘要和洞察在哪里` | Post-meeting artifacts Q&A, `entrypoint_id=None` | Preserve Q&A-first route | `can_operate=False`; no interrupt step |
| Chinese recording safety | `记录会议`; `怎么录制会议` | Recording safety Q&A / recording entrypoint, non-operable | Preserve recording safety route | `can_operate=False`; no interrupt step |
| Chinese start Notes action | `开始会议笔记`; `点击开始笔记` | `ringcentral.video.more.notes` entrypoint answer | Safety Q&A, `entrypoint_id=None` | `can_operate=False`; no interrupt step; do not start notes |
| Chinese transcript content read | `读取转录内容`; `读会议笔记内容` | `ringcentral.video.more.notes` entrypoint answer | Safety Q&A, `entrypoint_id=None` | `can_operate=False`; no interrupt step; do not read content |
| Chinese transcript/notes summary | `总结转录内容`; `总结会议笔记` | `ringcentral.video.more.notes` entrypoint answer | Safety Q&A, `entrypoint_id=None` | `can_operate=False`; no interrupt step; do not summarize content |
| Chinese copy/save/export | `复制转录`; `保存会议笔记`; `导出转录` | Likely Notes entrypoint by alias when alias term appears | Safety Q&A, `entrypoint_id=None` | `can_operate=False`; no interrupt step; do not expose private artifacts |
| Safe unrelated control sentinel | `网络质量` | `ringcentral.video.top.network-quality`, operable | Preserve operable route | `can_operate=True`; interrupt step allowed |

## Positive Prompt Matrix

| Prompt class | Example prompts | Expected route | Why it must remain positive |
| --- | --- | --- | --- |
| Chinese Notes location lookup | `笔记和转录在哪里`; `会议笔记在哪里`; `转录在哪里`; `笔记入口在哪里` | Notes location Q&A or `ringcentral.video.more.notes`; `can_operate=False`; no interrupt step | Finding the panel is safe and is the intended purpose of the existing Chinese aliases. |
| Mixed Chinese/English Notes location | `Notes and Transcript 在哪里`; `Start notes 在哪里` | Location-style Notes answer; no operation | Users may ask about English UI labels while speaking Chinese; location wording should not be mistaken for a click request. |
| Captions/live transcription discovery | `实时转录在哪里`; `字幕在哪里`; `翻译在哪里` | Existing captions/live transcription/translation Q&A, preferably `entrypoint_id=None` | This Q&A has more specific safety copy than the Notes entrypoint answer. |
| Post-meeting artifact discovery | `会后转录在哪里`; `会议摘要和洞察在哪里` | Existing post-meeting artifacts Q&A, preferably `entrypoint_id=None` | Post-meeting artifacts have availability and permission caveats that should not be flattened into Notes panel routing. |
| Recording guidance | `怎么录制会议`; `录制会议在哪里`; `记录会议` | Existing recording safety Q&A or recording entrypoint answer with `can_operate=False`; no interrupt step | Recording is adjacent to Notes but has its own consent-sensitive route. |
| Start meeting sentinel | `start meeting`; `点击 Start meeting`; `Start meeting をクリックして` | `ringcentral.develop.video.start`; `can_operate=False` in question mode | Chinese Notes hardening must not break the known Start meeting route or revive the Cycle 107 `Start notes`/Start meeting confusion. |
| Safe unrelated control | `网络质量`; `Network quality 在哪里`; `摄像头菜单在哪里` | Their existing control routes; operable only when the entrypoint is safe | The matcher must stay scoped to Notes/Transcript and avoid a broad CJK-action clampdown. |

## Overmatching Risks

- A Chinese hardening matcher that treats all `转录` prompts as unsafe would break legitimate location Q&A such as `实时转录在哪里` and `笔记和转录在哪里`.
- A matcher that treats all `笔记` prompts as unsafe would make the existing Chinese Notes aliases ineffective for location discovery.
- Adding Chinese action terms too broadly could steal recording prompts from the recording safety Q&A. `记录会议` must keep the recording safety behavior, not become a Notes/Transcript response.
- Adding Chinese location terms to the exclusion list must account for common phrasing such as `在哪里`, `在哪`, `哪里`, `位置`, and `入口`; otherwise location prompts can be routed to the safety Q&A by accident.
- The current safety Q&A target is the captions/live transcription/translation answer. That is acceptable for transcript content and start-control caution, but it should not be used for post-meeting artifact prompts that already have a more specific Q&A.
- `entrypoint_id` association is the main residual semantic risk. It is safe operationally today, but downstream analytics or UI labels may interpret `ringcentral.video.more.notes` as intent to open Notes even when the user asked to read or summarize private content.
- Console and shell probes need Unicode-safe fixtures. Use escaped literals or UTF-8-safe test files; mojibake probes can produce false no-matches.

- A mixed-language matcher that keys on `点击` plus any English `start` token could suppress `点击 Start meeting`; require the Notes/Transcript subject term as well.

## Count Expectations

The recommended Cycle 108 hardening should be runtime/tests only. Expected counts should remain:

- Japanese localization report: `questionAliases.ja present on 13/27 entrypoints (34 aliases)`
- Chinese localization report: `questionAliases.zh present on 15/27 entrypoints (49 aliases)`
- Localization coverage: `51/51` demo steps, `12/12` Q&A questions, `12/12` Q&A answers for both `ja` and `zh`
- Doctor question aliases: `87 package-owned aliases have no cross-entrypoint duplicates`
- Q&A prompt count: `71 Q&A question prompts`
- Q&A alias overlap: `71 Q&A question prompts have no unsafe package-owned alias overlaps`
- Q&A alias substring risk: INFO at `11` prompts
- Doctor summary: `11 ok, 1 info, 0 warnings, 0 failed`

Any change to alias counts, Q&A counts, localized coverage, substring INFO count, warning/failure totals, demo flow shape, or Notes `openSteps` is out of scope for this hardening slice unless explicitly justified.

## Guardrails

- Keep `ringcentral.video.more.notes.questionPolicy: answerOnly`.
- Keep the existing Notes `openSteps` for curated demos; do not remove or rewrite the panel route in this cycle.
- Preserve Q&A-first matching for captions/live transcription/translation, post-meeting artifacts, recording safety, participant/chat privacy, and host controls.
- Preserve Chinese Notes location discovery; do not remove `笔记`, `转录`, or `会议笔记` aliases as part of this hardening.
- Add Chinese action/content matching narrowly: start/click/open, read, summarize, content, copy, save, export, create, and show-context wording when paired with Notes/Transcript terms.
- Exclude location intent before safety routing, matching the Cycle 107 English/Japanese guard.
- Assert both `response.entrypoint_id is None` and `create_question_interrupt_step(...) is None` for Chinese action/content prompts that should move to safety Q&A.
- Keep a safe-control sentinel such as `网络质量` in tests so the matcher does not over-restrict unrelated operable controls.
- Use exact Unicode fixtures in tests, preferably with `\u` escapes where terminal encoding is ambiguous.
- Do not claim AiPresenter can read, summarize, copy, export, save, or verify Notes/Transcript content without explicit user request and verified visible context.

## Probe Evidence

Read-only probes against the current tree after Cycle 107 showed:

- `笔记和转录在哪里` associated safely with Notes Q&A / Notes and remained non-operable.
- `实时转录在哪里` returned the captions/live transcription/translation safety Q&A with `entrypoint_id=None`.
- `会后转录在哪里` returned the post-meeting artifacts Q&A with `entrypoint_id=None`.
- `记录会议` returned the recording safety answer and remained non-operable.
- `开始会议笔记`, `点击开始笔记`, `读取转录内容`, `读会议笔记内容`, `总结转录内容`, `总结会议笔记`, `复制转录`, and `保存会议笔记` all associated with `ringcentral.video.more.notes`, remained `can_operate=False`, and created no interrupt step.
- `网络质量` remained operable and created an interrupt step.
- English `Read the transcript` and Japanese `Transcript の内容を読んで` returned the safety Q&A with `entrypoint_id=None`, confirming the Cycle 107 behavior for those languages.

## Review Checklist

- Confirm no production route, package YAML alias, demo `openSteps`, or Q&A copy changes are included unless the next cycle explicitly expands scope.
- Confirm `_match_notes_transcript_safety_qa(...)` still runs after exact Q&A and recording safety checks, and before entrypoint title/token matching.
- Confirm Chinese subject terms include Notes/Transcript concepts such as `笔记`, `会议笔记`, `转录`, `字幕`, and mixed English UI labels where needed.
- Confirm Chinese action/content terms are intent words, not standalone blockers: `开始`, `启动`, `开启`, `点击`, `点`, `打开`, `读`, `朗读`, `念`, `总结`, `摘要`, `内容`, `复制`, `保存`, `导出`, `生成`, `创建`.
- Confirm Chinese location terms short-circuit the safety matcher before action/content routing: `哪里`, `在哪`, `位置`, `入口`.
- Confirm negative tests assert `entrypoint_id is None`, `can_operate is False`, and `create_question_interrupt_step(...) is None` for Chinese Notes/Transcript action/content prompts.
- Confirm positive tests preserve `ringcentral.video.more.notes` for Chinese location prompts and preserve existing Q&A routes for captions/live transcription, post-meeting artifacts, and recording guidance.
- Confirm Start meeting sentinels still route to `ringcentral.develop.video.start`, especially `点击 Start meeting`; `点击 Start notes` must not route there.
- Confirm unrelated safe controls such as `网络质量` still create an interrupt step when `can_operate=True`.
- Confirm diagnostics/localization counts remain stable: no new aliases, no new Q&A prompts, no localized coverage regression, no new doctor warnings.
- Confirm CJK fixtures are stored as UTF-8 or escaped literals and have been reviewed outside mojibake-prone terminal output.

## Handoff Recommendation

Harden Chinese prompts this cycle. Treat it as a small runtime/test parity slice with Cycle 107, not a package localization or route-design cycle. The desired behavior is to route Chinese Notes/Transcript action and content prompts to the existing safety Q&A while preserving Chinese location lookups and current diagnostic counts.

Go, with guardrails. The implementation should be limited to adding Chinese subject/action/content/location terms to the existing matcher plus focused tests. No-go if the proposed change broadens package aliases, makes Notes/Transcript operable, changes Start meeting routing, removes Chinese location discovery, or attempts to add transcript reading/summarization capability.
