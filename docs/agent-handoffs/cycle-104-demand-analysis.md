# Cycle 104 Demand Analysis: Japanese Notes / Transcript And Recording Discovery

## Findings

Cycle 103 left Japanese `questionAliases.ja` at `11/27` entrypoints and `30` aliases, with `83` total package-owned aliases. The baseline is healthy: Japanese demo and Q&A localization are complete, doctor reports no alias duplicates, and `qa alias substring risk` remains the existing INFO-level `11` prompt summary.

User value is real for both candidate areas, but they are not equally safe:

| Candidate | User value | Current safety posture | Demand verdict |
| --- | --- | --- | --- |
| Notes / Transcript | High. Japanese users may naturally ask where meeting notes, transcript, or the Notes and Transcript panel lives. | Risky. The panel contains `Start notes` and `Also record this meeting`; transcript text is private. A read-only probe shows the current Notes Q&A route can return `entrypoint_id=ringcentral.video.more.notes` with `can_operate=True`, and `Transcript はどこですか` can route to the Notes entrypoint with `can_operate=True`. | Do not add Notes/Transcript `questionAliases.ja` until the Notes entrypoint is made explain-only for question responses. |
| Recording | Medium-high. Users commonly ask `録画はどこですか` or how to handle recording safely. | Safer than Notes. `ringcentral.video.more.recording` has `openSteps: []` and its title/purpose contain `Start recording` / `recording`, so question responses stay `can_operate=False`. Existing Japanese Q&A covers `会議を録画するにはどうすればいいですか`, but plain location phrasing is currently a no-match unless the user says mixed English like `Start recording の場所`. | Good candidate for answer-only Q&A expansion; package aliases are possible but should be secondary. |
| Other candidates | Lower near-term value for this user story. | Share, Leave, Invite/Add coworkers, host controls, broad Settings, Report issue, and More all touch state changes, private values, or ambiguous menus. More is mechanically safer than Recording, but it is a less direct answer to the Japanese user question and exposes the same risky menu shelf. | Defer in favor of sensitive-surface hardening and narrow Q&A coverage. |

Important nuance: the existing Notes Q&A answer is safer than opening the panel, but because it is related to `ringcentral.video.more.notes`, the runtime's `can_operate` result can still be `True`. That is a demand blocker for any "answer-only / read-only" Notes discovery slice.

## Recommended Scope

Recommend Cycle 104 as a safety-first answer-only slice, not a `questionAliases.ja` expansion.

Minimum safe scope:

- Make `ringcentral.video.more.notes` explain-only for question responses, using the same spirit as the existing meeting-info privacy gate. The goal is that Notes/Transcript Q&A and title/entrypoint lookup may identify the relevant surface, but must return `can_operate=False`.
- Strengthen the Notes / Transcript Japanese Q&A answer so it explicitly says AiPresenter may explain the panel location, but must not start notes, read or summarize transcript content, trigger recording, or promise post-meeting artifacts unless the user explicitly asks and visible context is verified.
- Add Japanese localized Q&A question variants, not package-owned entrypoint aliases, for the user phrasing that currently misses:
  - `ノートはどこにありますか`
  - `文字起こしはどこにありますか`
  - `Notes and Transcript の場所はどこですか`
  - `録画はどこにありますか`
  - `録画ボタンの場所はどこですか`
  - `Start recording の場所はどこですか`
  - `録画を安全に扱うにはどうすればいいですか`
- Keep `questionAliases.ja` unchanged at `11/27` entrypoints and `30` aliases; keep total package-owned aliases unchanged at `83`.

Expected answer boundaries:

- Notes / Transcript prompts should return the Notes safety answer or an equivalent answer-only response, with `can_operate=False`.
- Recording prompts should return the recording safety answer, with `can_operate=False`.
- Responses may name the relevant surface, but must not present a click path as something AiPresenter can perform unattended.
- No response should claim notes, transcripts, summaries, insights, or recordings exist unless verified in visible context.

If the main session decides that Cycle 104 must add package `questionAliases.ja`, limit that alias-only fallback to Recording:

| Entrypoint | Strict fallback aliases | Expected boundary |
| --- | --- | --- |
| `ringcentral.video.more.recording` | `録画ボタンの場所`<br>`Start recording の場所` | Location wording only. Expected counts would become `questionAliases.ja present on 12/27 entrypoints (32 aliases)` and `85 package-owned aliases`. `can_operate` must remain `False`; answer text must not imply recording was or will be started. |

Do not use bare `録画`, `録画して`, `録画開始`, `録画を開始`, or `会議を録画` as aliases. Keep those in Q&A safety routing, where the answer can state consent and role requirements.

## Deferred Scope

Defer Notes / Transcript `questionAliases.ja` until the Notes entrypoint is proven explain-only for questions. If aliases are later needed, they should be a separate risk-scanned slice after the hardening above, and should use only long location nouns such as:

- `ノートと文字起こしパネルの場所`
- `Notes and Transcript の場所`

Still avoid broad aliases such as `ノート`, `文字起こし`, `Transcript`, `議事録`, `ノートを開始`, `文字起こしを読んで`, or `要約して`. Broad terms can accidentally capture requests to start notes, read transcript content, or summarize meeting artifacts.

Also defer:

- Post-meeting artifact aliases. They risk implying recordings, transcripts, summaries, or insights exist.
- Recording operation aliases. They risk sounding like permission to start or stop recording.
- More menu aliases as an indirect recording route. They add little user value and may expose risky menu items without answering the user's exact question.
- Share, Leave, Invite/Add coworkers, host/security, participant identity, report contents, and broad Settings aliases.

## Acceptance Signals

For the recommended answer-only scope:

- `answer_question(..., "ノートはどこにありますか", language="ja")` returns a Notes/Transcript safety answer with `can_operate is False`.
- `answer_question(..., "文字起こしはどこにありますか", language="ja")` returns a Notes/Transcript safety answer with `can_operate is False`.
- `answer_question(..., "Notes and Transcript の場所はどこですか", language="ja")` does not return an operable Notes route.
- `answer_question(..., "Transcript はどこですか", language="ja")` no longer produces an operable Notes response.
- `answer_question(..., "録画はどこにありますか", language="ja")` returns the recording safety answer with `can_operate is False`.
- `answer_question(..., "録画ボタンの場所はどこですか", language="ja")` returns the recording safety answer with `can_operate is False`.
- Negative prompts remain non-operable and do not become entrypoint aliases: `ノートを開始して`, `文字起こしを読んで`, `Transcript を要約して`, `録画を開始して`, `会議を録画して`, `会議後の要約を作って`.
- Japanese localization report remains `51/51` demo steps, `12/12` Q&A questions, `12/12` Q&A answers, and `questionAliases.ja present on 11/27 entrypoints (30 aliases)`.
- Doctor keeps `83 package-owned aliases have no cross-entrypoint duplicates` for the recommended no-alias scope. Q&A prompt totals may increase by the number of added localized question prompts, but duplicate and unsafe-overlap checks should stay OK.

For the fallback Recording alias-only scope:

- Add aliases only under `ringcentral.video.more.recording`.
- Assert exact Japanese alias counts move to `12/27` entrypoints and `32` aliases.
- Assert total package-owned aliases move to `85`.
- Assert `録画ボタンの場所はどこですか` and `Start recording の場所はどこですか` route to `ringcentral.video.more.recording` with `can_operate is False`.
- Assert action phrases such as `録画を開始して` and `会議を録画して` remain safety-gated and never produce an operable response.

## Handoff Notes

Read-only commands used:

- `.\.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language ja --require-complete`
- `.\.venv\Scripts\ai-presenter doctor --profile profiles\ringcentral-video.yaml --package packages\ringcentral-video.yaml --flow meeting-control-map-demo`
- Runtime read-only probes through `answer_question()` for Japanese Notes/Transcript and Recording phrasing.

Observed baseline:

- Localization report: `51/51` demo steps, `12/12` localized Q&A questions, `12/12` localized Q&A answers, `questionAliases.ja present on 11/27 entrypoints (30 aliases)`.
- Doctor: `11 ok, 1 info, 0 warnings, 0 failed`; `83 package-owned aliases have no cross-entrypoint duplicates`; `qa alias overlap` OK; substring risk remains INFO at `11`.
- Current route concern: `ノートと文字起こしはどこにありますか` returns the Notes Q&A but can still report `can_operate=True`; `Transcript はどこですか` can route to the Notes entrypoint with `can_operate=True`. Treat this as the reason to harden before adding Notes aliases.

Demand recommendation: use Cycle 104 to make sensitive Japanese discovery genuinely answer-only. Recording aliases are feasible, but the stronger user-value move is to cover both Notes/Transcript and Recording through localized Q&A while fixing the Notes `can_operate` boundary first.
