# Cycle 103 Implementation Handoff

## Scope

Cycle 103 adds a narrow Japanese location-discovery slice for RingCentral Video visible-signal controls:

- `ringcentral.video.toolbar.react`
- `ringcentral.video.toolbar.raise-hand`

The implementation follows the risk scan's smaller `+4` recommendation rather than the wider `+6` demand/technical option. The added aliases help users ask where the controls are, without treating questions as requests to send a reaction, raise a hand, lower a hand, identify participants, or perform host/moderator actions.

## Alias Set

`ringcentral.video.toolbar.react` now owns:

- `React ボタンの場所`
- `リアクション欄の場所`

`ringcentral.video.toolbar.raise-hand` now owns:

- `挙手ボタンの場所`
- `挙手の場所`

Expected post-cycle counts:

- `questionAliases.ja present on 11/27 entrypoints (30 aliases)`
- `83 package-owned aliases have no cross-entrypoint duplicates`

## Safety Boundary

Runtime behavior remains text-only for these routes:

- Reactions stays non-operable because `_can_operate()` catches risky words in the entrypoint title/purpose such as `send` and `reaction`.
- Raise hand stays non-operable because `_can_operate()` catches risky words such as `raise hand` and `lower hand`.
- The mixed English/Japanese prompt `Raise hand の場所はどこですか` intentionally remains captured by the existing reaction/raise-hand safety Q&A rather than becoming a package alias.

Tests now protect:

- The four new Japanese location prompts route to the intended entrypoints with `can_operate is False`.
- Japanese send-reaction prompts, hand-toggle prompts, participant-identity prompts, and host-control prompts remain non-operable and do not route to unsafe entrypoints.
- The existing Japanese reaction/raise-hand safety Q&A remains answer-only.

## Verification Evidence

Red test before YAML changes:

- `.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py tests\unit\test_questions.py tests\unit\test_cli.py tests\unit\test_diagnostics.py`
- Result: `22 failed, 262 passed`. Failures matched the expected missing aliases, stale `9/27` and `26` Japanese alias counts, stale `79` doctor count, and no route for new Japanese location prompts.

Green test after YAML changes:

- Same focused command.
- Result: `284 passed`.

Additional checks:

- `.\.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language ja`
  - Result: `questionAliases.ja present on 11/27 entrypoints (30 aliases)`.
- `.\.venv\Scripts\ai-presenter doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo`
  - Result: `83 package-owned aliases have no cross-entrypoint duplicates`; doctor completed with `11 ok, 1 info, 0 warnings, 0 failed`.
