# Cycle 153 Experience: Tone-Invariant Routing Guard

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`

## What This Cycle Learned

- After `empathetic -> support`, the useful next slice was not another tone
  alias or product-copy pass. The sharper risk was that a tone alias could be
  mistaken for a behavior mode and accidentally change RingCentral Video
  question routing.
- A test-only routing guard was enough because the runtime path already
  normalizes `empathetic` to canonical `support` before question routing sees
  the voice settings. The cycle needed regression evidence, not new runtime
  behavior.
- The existing
  `test_ringcentral_sensitive_prompt_routing_is_tone_invariant` matrix was the
  right surface because it already covered answer-only prompts, non-operable
  routes, and operable routes through the same package fixture.
- The guard protects the practical user promise: presenter tone may change
  answer style, but for the covered RingCentral prompts it should preserve the
  selected entrypoint, operation gate, and interrupt-step decision.

## TDD Red Method

- Current behavior already passed, so a normal red-first edit would not expose
  a failure. The cycle used a temporary mutation red instead.
- Red method:
  1. Add `empathetic` to the tone loop in
     `tests/unit/test_questions.py::test_ringcentral_sensitive_prompt_routing_is_tone_invariant`.
  2. Temporarily remove or comment out `"empathetic": "support"` in
     `src/ai_presenter/runtime/voice.py`.
  3. Run the focused routing test and confirm construction of
     `PresenterVoiceSettings(tone="empathetic")` fails with
     `Unsupported presenter tone: empathetic`.
  4. Restore the runtime alias exactly as it was before keeping the test-only
     guard.
- This proved the new assertion depends on the alias normalization path while
  still preserving the final no-source-change scope.

## Final Diff

- Final retained diff is test-only:

```diff
-    for tone in ("friendly", "coach", "support", "privacy"):
+    for tone in ("friendly", "coach", "support", "empathetic", "privacy"):
```

- No source, package, profile, README, existing handoff, or `.coverage` edit is
  part of the retained change.
- The test continues to compare only `entrypoint_id`, `can_operate`, and
  interrupt-step presence. It does not compare answer text, because tone may
  legitimately affect phrasing.

## Safe Wording

- Say "For the covered prompts, RingCentral question routing is
  tone-invariant."
- Say "The guard compares the same `entrypoint_id`, `can_operate`, and
  interrupt-step presence across selected tones."
- Say "The `empathetic` alias reuses canonical `support` tone behavior and
  preserves the same routing outcome."
- Say "This is package question-routing evidence, not live RingCentral Video
  acceptance."
- Avoid "privacy-safe routing", "accepted in live meetings", "provider
  validated", "AI understands sensitive questions", "empathetic privacy
  handling", or "better support quality" unless a separate dated evidence
  source proves that exact surface.

## Next-Cycle Ideas

- RingCentral Video knowledge pack: add another tiny package-owned question
  slice for common operator phrasing around meeting info, participants, invite,
  share, or network quality, while keeping privacy and actionability gates
  explicit.
- RingCentral Video knowledge pack: review whether high-risk areas such as
  recording, transcripts, notes, and chat need more authored answer-only aliases
  without expanding operable actions.
- CLI discoverability: improve how `ai-presenter voices` or a neighboring CLI
  command exposes canonical tones versus aliases, so operators can discover
  words like `empathetic` without reading source.
- CLI discoverability: consider a narrow filter or profile-aware view that
  lists available language/tone combinations separately from provider readiness
  and live RingCentral acceptance.
