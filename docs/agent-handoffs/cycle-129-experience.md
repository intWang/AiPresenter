# Cycle 129 Experience Handoff: Spanish OpenAI Proof Lessons

Date: 2026-05-16
Cycle: 129
Scope: experience handoff only. This file is the only intended edit for this
handoff. Do not modify source, tests, durable docs, package YAML, profiles,
generated artifacts, staging, commits, or live acceptance evidence from this
slice.

## Summary

Cycle129 worked best when it treated Spanish as a proof problem, not a language
expansion problem. The useful pattern was to prove the OpenAI path with focused
unit and dry-run evidence, preserve the local-provider rejection boundary, and
avoid words that imply live RingCentral or real OpenAI acceptance.

The current in-flight diff already reflects that posture:

- Controller readiness validates profile/language compatibility before local
  asset readiness.
- Runtime-factory tests prove Spanish material demos use `localizedText.es` and
  route speech through `openai`.
- A stricter injected-registry test proves the Spanish OpenAI path can run
  without constructing `OpenAISpeechProvider`.
- Controller and view-model tests now keep Start and Submit aligned for local
  Spanish rejection and OpenAI Spanish readiness.
- The questions runtime gained a Spanish no-match fallback, with tests proving
  Spanish does not fall back to English.

`.coverage` is dirty in the worktree and should remain treated as generated
output unless the cycle owner explicitly asks otherwise.

## Lessons For Future Cycles

### Proof-First Spanish OpenAI Path

The strongest Cycle129 lesson is that "Spanish exists" is not enough. Future
cycles should keep proving the complete product path: voice normalization,
profile compatibility, provider routing, package-localized narration, controller
readiness, dry-run behavior, and operator-facing messages.

For Spanish, the safe claim is still narrow:

- Spanish is runtime-selectable with OpenAI-backed speech profiles.
- Spanish package localization is complete for RingCentral Video.
- Spanish local SAPI/Piper support is not implemented.
- Live RingCentral Spanish acceptance remains unproven until a dated acceptance
  run records provider, profile, flow, audio, and RingCentral evidence.

Do not upgrade unit tests, dry runs, or localization reports into live
acceptance language.

### Compatibility Before Asset Readiness

Cycle129 exposed an important ordering rule: profile/language compatibility must
be validated before local asset checks. Spanish on a local profile is not a
missing-asset problem; it is an incompatible-provider problem.

Future local-provider work should preserve this order:

1. Validate that the selected profile can use the selected runtime language.
2. Only then check local voice assets when the provider route actually needs
   them.
3. Report OpenAI-only languages with compatibility wording, not SAPI/Piper asset
   wording.

This keeps operators from chasing local voice installs for a language that is
intentionally OpenAI-only.

### Package Fallback Strings Matter

When promoting a runtime language, remember the small strings around the core
path. Spanish needed a no-match Q&A fallback so an unsupported question did not
drop back to English.

Future runtime-language additions should audit at least:

- no-match Q&A fallback strings,
- package localized narration,
- localized Q&A answers,
- question aliases,
- voice labels,
- CLI and diagnostics messages.

ASCII-only fallback copy may be acceptable for consistency with the current
codebase, but call that out as a copy-polish item rather than pretending it is
final localization quality.

### Injected Registries Avoid Provider Construction

The injected-registry runtime-factory test is the strongest no-live-provider
evidence in this cycle. Monkeypatching `OpenAISpeechProvider` proves construction
can be intercepted; injecting a registry and making construction fail proves the
code path does not need to construct the real provider at all.

Future provider-bound tests should prefer:

- fake provider registries,
- fake windows or handles,
- fake timeline runners,
- explicit failure if real provider construction is reached,
- no dependence on `OPENAI_API_KEY` for dry-run/unit evidence.

This gives much clearer proof than relying on environment absence alone.

### Controller Readiness Parity

Start and Submit need the same voice-readiness truth. Cycle129 reinforced that a
language/profile combination blocked for Start must also be blocked before
Submit can launch or queue a question demo.

Future controller changes should test both operator paths:

- local incompatible voice disables Start and Submit with the same provider
  compatibility reason,
- OpenAI Spanish remains startable with `assets: Not required`,
- question demos forward `PresenterVoiceSettings(language="es")`,
- running-state Submit behavior stays tied to valid target and voice state.

### No Live Acceptance Claims

Cycle129 handoffs were careful not to say Spanish was "accepted" or
"production-ready" for RingCentral. Keep that discipline. A passing unit test,
dry run, or `doctor` command can prove code-path wiring; it cannot prove live
audio quality, real OpenAI synthesis, or RingCentral UI behavior.

Acceptance claims need dated evidence with the actual provider, profile, flow,
audio path, RingCentral state, and observed outcome.

## Next-Cycle Recommendations

1. Run and record the full Spanish OpenAI verification bundle before staging:
   focused unit tests, `voices`, `localization-report`, `doctor`,
   `demo --dry-run`, `controller --dry-run`, the negative local-profile command,
   `git diff --check`, and `git status --short`.

2. Add a concise Cycle129 test-evidence or merge-readiness handoff after the
   full command bundle runs. Separate "observed command output" from inference,
   especially for doctor environment readiness.

3. Preserve the injected-registry pattern for any future OpenAI or network-bound
   runtime tests. Make real provider construction fail loudly unless the test is
   explicitly scoped as an integration run.

4. Keep package-only language boundary coverage alive with an unsupported
   fixture language such as `de`. Spanish is no longer the right sentinel for
   "localized package exists but runtime language is unsupported."

5. Review the Spanish no-match fallback copy later, ideally in a copy/localization
   cycle rather than this runtime-proof cycle. The current `No encontre` string
   is useful coverage, but not a reason to broaden this change.

6. Do not stage `.coverage` with Cycle129 unless explicitly requested. It is a
   generated artifact and appears unrelated to the intended implementation
   surface.

7. If live Spanish acceptance becomes the next target, make it its own cycle
   with explicit prerequisites: OpenAI credentials, selected OpenAI voice/model,
   RingCentral environment, flow, recording or transcript expectations, and a
   dated acceptance artifact. Do not combine that with local SAPI/Piper work.
