# Cycle 104 Implementation Handoff

## Scope

Cycle 104 implements the risk scan's Recording-only alias slice and adds a small runtime safety guard for Japanese recording action/status prompts.

Notes/Transcript aliases remain deferred because `ringcentral.video.more.notes` currently has executable `openSteps`; adding Japanese aliases there would make more ordinary Japanese prompts capable of opening the Notes and Transcript side panel.

## Alias Set

`ringcentral.video.more.recording` now owns:

- `Start recording の場所`
- `録画ボタンの場所`

Expected post-cycle counts:

- `questionAliases.ja present on 12/27 entrypoints (32 aliases)`
- `85 package-owned aliases have no cross-entrypoint duplicates`

## Runtime Safety

Red tests exposed an additional route-safety issue before the YAML implementation: `参加者に知らせず録画して` could be captured by the Japanese Participants alias and become operable. The implementation adds a small Q&A-first recording safety matcher in `src/ai_presenter/runtime/questions.py` for Japanese recording action, consent, status, and artifact requests.

This keeps prompts such as the following non-operable and returns the existing Recording safety Q&A instead of routing to Participants or any executable control:

- `参加者に知らせず録画して`
- `同意なしで録画して`
- `録画を開始して`
- `録画を止めて`
- `録画状態を確認して`
- `録画の内容を要約して`

Location prompts still route to `ringcentral.video.more.recording` and remain non-operable because Recording has `openSteps: []`.

## Verification Evidence

Red test before implementation:

- `.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py tests\unit\test_questions.py tests\unit\test_cli.py tests\unit\test_diagnostics.py`
- Result: `24 failed, 280 passed`. Expected failures covered stale alias totals and missing Recording aliases. One failure revealed the Participants-route safety issue for `参加者に知らせず録画して`.

Green test after implementation:

- Same focused command.
- Result: `304 passed`.

Additional checks:

- `.\.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language ja`
  - Result: `questionAliases.ja present on 12/27 entrypoints (32 aliases)`.
- `.\.venv\Scripts\ai-presenter doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo`
  - Result: `85 package-owned aliases have no cross-entrypoint duplicates`; `qa questions` remains `71`; `qa alias overlap` remains OK; substring risk remains INFO at `11`; doctor completed with `11 ok, 1 info, 0 warnings, 0 failed`.

## Next Risk Item

The next cycle should consider the demand-analysis recommendation: make Notes/Transcript question responses answer-only before adding any Japanese Notes/Transcript aliases. That requires a runtime policy decision, not just YAML alias expansion.
