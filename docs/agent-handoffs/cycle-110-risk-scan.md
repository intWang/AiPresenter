# Cycle 110 Risk Scan: Cross-Tone Route Parity

Date: 2026-05-16
Scope: risk/review matrix only. Do not edit production code or tests as part of this handoff.

## Verdict

Go for a narrow cross-tone route parity regression matrix, with guardrails.

The tests should prove that tone is style-only: `professional`, `conversational`, `concise`, `friendly`, `coach`, `formal`, `support`, and `careful` must produce the same RingCentral route eligibility for the same prompt. Route parity means the same `entrypoint_id`, same `can_operate`, same `questionPolicy` effect, and same interrupt-step outcome. It does not mean identical `answer_text`, because some tones legitimately add prefixes or shorten generated English text.

No-go for a broad golden-answer suite, package YAML rewrites, new route aliases, or assertions that make `Safety note.` and other tone prefixes part of route behavior. Cycle 110 should close the Cycle 109 gap without turning tone rendering tests into brittle route tests.

## Severity Risks

| Severity | Risk | Failure mode | Impact | Guardrail |
| --- | --- | --- | --- | --- |
| P0 | Tone changes operation eligibility | A tone-specific branch changes `can_operate`, weakens `questionPolicy: answerOnly`, or allows `create_question_interrupt_step(...)` for a previously blocked RingCentral prompt. | A user could select a tone and make a privacy-sensitive or destructive route operable. | Compare route tuples across all canonical tones: `entrypoint_id`, `can_operate`, and `interrupt_created`. Include Meeting information and Notes because they rely on package policy, not only risky words. |
| P0 | Prefix overfit hides route regression | Tests assert `careful.answer_text.startswith("Safety note.")` and miss that the route or interrupt changed. | The suite appears to cover careful tone while the actual safety gate drifts. | Keep prefix checks in voice/rendering tests. In route parity tests, treat answer text as secondary sentinels only and fail primarily on route invariants. |
| P0 | Localized authored answer mutation | Cross-tone parameterization expects localized Q&A answers to vary, or applies English careful prefixes to Chinese/Japanese authored answers. | Localized privacy boundaries can become awkward, duplicated, or less direct; exact authored safety copy loses protection. | For localized Q&A rows, assert authored-answer preservation separately: no English prefix, no dropped consent/verified-context clause, and route invariants unchanged. |
| P1 | Prompt choice creates false parity failure | A prompt is chosen where `answer_text` is intentionally tone-dependent, such as dynamic English entrypoint answers under `friendly`, `support`, or `careful`. | Tests fail for legitimate style differences and encourage weakening tone rendering. | For dynamic English answers, compare route tuple only. Use minimal sentinel words tied to safety facts, not full text or prefix order. |
| P1 | Broad parameterization slows the unit suite | Every sensitive prompt is multiplied by every tone, language, and alias. | The route suite becomes noisy and expensive, discouraging future safety coverage. | Use a small high-signal matrix: all canonical tones for 6-8 representative prompts, plus targeted localized rows for authored-answer invariants. Keep aliases to one or two smoke rows. |
| P1 | Alias drift mistaken for tone drift | `privacy`, `safety`, `safe`, `guarded`, or `compliance` are tested as separate canonical tones everywhere. | Test count balloons and failures obscure whether alias normalization or route parity broke. | Full matrix should use canonical tones only. Add a tiny alias smoke test proving `privacy` normalizes to `careful` before route evaluation. |
| P1 | QuestionPolicy coverage is indirect only | Tests cover risky-word non-operability but omit `answerOnly` entrypoints. | Removing `questionPolicy` from Meeting information or Notes could be missed if risky words still block some prompts. | Include Meeting information and Notes location prompts; assert no interrupt even if risky-word list is monkeypatched elsewhere in existing tests. |
| P2 | Golden text churn | The matrix snapshots full answers in multiple tones and languages. | Minor copy improvements create review noise unrelated to route safety. | Avoid full-answer snapshots. Use exact text only for localized authored-answer preservation when the answer is expected to bypass tone rendering. |
| P2 | Mixing route parity with package expansion | Cycle 110 adds new aliases or prompts while adding route parity tests. | Failures become hard to classify: matching changed, policy changed, or tone changed. | Keep Cycle 110 test-only unless separately approved; do not edit package YAML or production route code for this matrix. |

## Candidate Prompt Matrix

Use this as a review target, not a demand to multiply every cell by every language. The all-tone rows should cover canonical tones only: `professional`, `conversational`, `concise`, `friendly`, `coach`, `formal`, `support`, and `careful`.

| Area | Candidate prompt | Languages / tones | Expected route invariant | Answer-text guard |
| --- | --- | --- | --- | --- |
| Operable baseline | `open chat` | English, all canonical tones | `entrypoint_id == ringcentral.video.toolbar.chat`; `can_operate is True`; interrupt step is created. | Do not compare full text; dynamic prefixes may differ by tone. |
| Answer-only package policy | `meeting information` | English, all canonical tones | `entrypoint_id == ringcentral.video.top.meeting-info`; `can_operate is False`; no interrupt. | Must not fabricate meeting ID, URL, host, phone number, or `ringcentral.com`. |
| Notes answer-only policy | `Where are Notes and transcript` | English, all canonical tones | `entrypoint_id == ringcentral.video.more.notes`; `can_operate is False`; no interrupt. | Should still describe the panel/location, not imply notes are started. |
| Recording safety | `recording` | English, all canonical tones | `entrypoint_id == ringcentral.video.more.recording`; `can_operate is False`; no interrupt. | Must keep consent/state-change terms; must not include `Start recording:` as an instruction prefix. |
| Participants privacy Q&A | `where are host controls for participants` | English, all canonical tones | `entrypoint_id is None`; `can_operate is False`; no interrupt. | Safety facts such as explicit user request and verified context must remain present; prefix may differ. |
| Invite sensitive route | `invite people` | English, all canonical tones | `entrypoint_id == ringcentral.video.toolbar.invite`; `can_operate is False`; no interrupt. | Must not imply an invite was sent or details were copied. |
| Screen sharing | `share screen` | English, all canonical tones | `entrypoint_id == ringcentral.video.toolbar.share`; `can_operate is False`; no interrupt. | Must not imply final sharing was confirmed. |
| Destructive control | `leave meeting` | English, all canonical tones | `entrypoint_id == ringcentral.video.toolbar.leave`; `can_operate is False`; no interrupt. | Must not imply leaving/end meeting was executed. |
| Legitimately operable diagnostic | `network quality` | English, selected tones: `professional`, `support`, `careful` | `entrypoint_id == ringcentral.video.top.network-quality`; `can_operate is True`; interrupt step is created. | Do not force identical answer text; this row protects against over-disabling all routes. |
| Localized authored Q&A | Existing Chinese captions/transcription prompt from tests | Chinese, selected tones: `professional`, `careful` plus alias `privacy` | Same Q&A route as professional; `can_operate is False`; no interrupt. | Authored localized answer should not receive English `Safety note.` or Chinese dynamic careful prefix. |
| Localized privacy Q&A | Existing Japanese chat/participant privacy prompt from tests | Japanese, selected tones: `professional`, `careful` | `entrypoint_id is None`; `can_operate is False`; no interrupt. | Preserve authored privacy boundary; do not require English prefix or exact English wording. |
| Alias smoke | Any one high-risk prompt, preferably `meeting information` | `careful` and alias `privacy` | Same route tuple and no interrupt. | Alias normalization belongs in voice tests; one route smoke row is enough. |

## Invariant Recommendations

- Define a small helper that returns a route tuple such as `(entrypoint_id, can_operate, interrupt_created)` for a prompt and tone.
- Compare each non-baseline tone to the `professional` result for the same prompt.
- Include `questionPolicy` effect indirectly by choosing Meeting information and Notes rows where `answerOnly` must force `can_operate=False` and no interrupt.
- Keep answer-text assertions sparse: presence of safety facts is useful; exact full text and prefix order are not route invariants.
- For localized authored Q&A, invert the usual answer-text rule: exact or near-exact authored-answer preservation is the safety property, because localized answers bypass tone rendering.
- Keep the full matrix canonical-tone only. Exercise `privacy` as an alias smoke row, not as a ninth tone in every test.
- Add one operable positive row, such as Chat or Network quality, so a broken implementation that disables every route cannot pass.
- Keep prompts stable and already covered by existing package/test fixtures. Do not choose new prompts that require new aliases or package Q&A entries.

## Test Anti-Patterns To Avoid

- Do not assert `answer_text.startswith("Safety note.")` in route parity tests. That belongs in voice rendering coverage.
- Do not snapshot complete answer text across all tones. It couples route safety to copy style.
- Do not parameterize every prompt across every tone, every alias, every language, and every localized variant. Prefer a compact matrix with named rationale.
- Do not use prompts whose answer must legitimately differ by tone if the test expects exact text equality.
- Do not treat `concise` as route-equivalent plus text-equivalent. It may shorten dynamic English text; route parity is still required.
- Do not add package YAML aliases just to make a test prompt route. Pick prompts that already route today.
- Do not infer safety from `can_operate=False` alone. Also assert no interrupt step, because interrupt creation is the user-visible operation path.
- Do not make localized authored-answer tests require English wording, English prefixes, or dynamic careful phrasing.

## Go / No-Go

Go if Cycle 110 adds a compact test matrix that proves route tuple parity across canonical tones for representative RingCentral prompts, with focused localized authored-answer checks and one alias smoke test.

No-go if the proposed tests require production routing changes, package YAML edits, broad alias expansion, or full-answer snapshots.

No-go if the matrix allows any tone to change `questionPolicy`, `can_operate`, or interrupt-step creation. Tone can change phrasing only after route and eligibility have already been decided.

## Review Checklist

- Confirm the implementation diff for this risk scan touches only `docs/agent-handoffs/cycle-110-risk-scan.md`.
- For a later test implementation, confirm production code and package YAML remain unchanged unless a separate approved task exists.
- Confirm all canonical tones are covered in the route parity rows and aliases are limited to smoke coverage.
- Confirm each row asserts `entrypoint_id`, `can_operate`, and interrupt-step creation or absence.
- Confirm Meeting information and Notes are included so `questionPolicy: answerOnly` remains protected.
- Confirm at least one operable route remains operable across tones.
- Confirm answer-text assertions are fact sentinels or authored-localized preservation checks, not full golden strings.
- Confirm localized Chinese/Japanese authored answers do not receive English `Safety note.` or dynamic careful prefixes.
- Confirm `careful`, `privacy`, `safety`, `safe`, `guarded`, and `compliance` remain wording style only and do not imply policy validation.
- Confirm the focused test command is documented after implementation, likely limited to `tests/unit/test_questions.py` plus any voice alias smoke tests.
