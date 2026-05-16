# Cycle 059 Technical Scan: Q&A Prompt Alias Substring Diagnostics

## Scope

Add a diagnostics warning for the risk where a package-owned question alias appears as a substring inside a privacy or safety Q&A prompt. This scan is handoff-only: no code, test, YAML, or git changes were made.

Example risk from cycle 058: the Japanese chat alias `\u30c1\u30e3\u30c3\u30c8` appears inside the localized Q&A prompt `\u30c1\u30e3\u30c3\u30c8\u5185\u5bb9\u3084\u53c2\u52a0\u8005\u540d\u3092\u8aad\u307f\u4e0a\u3052\u3089\u308c\u307e\u3059\u304b`.

## Existing Logic

`diagnose_configuration()` calls `_diagnose_material_package()` when a material package is present. Package checks currently include:

- `question aliases`: `_diagnose_question_aliases()` groups `material_package.entrypoint_question_aliases` by `normalized_alias` and warns only when the same normalized alias maps to more than one entrypoint.
- `qa questions`: `_diagnose_qa_questions()` groups `material_package.qa_question_candidates` by `normalized_question` and warns only when the same normalized Q&A prompt belongs to more than one Q&A item.
- `qa alias overlap`: `_diagnose_qa_alias_overlaps()` groups aliases by exact `normalized_alias`, groups Q&A candidates by exact `normalized_question`, and warns only when a normalized Q&A prompt exactly equals a package-owned alias whose entrypoint is not in the Q&A item's `related_entrypoint_ids`.

Runtime matching in `questions.py` explains why substring collisions matter:

- `_answer_question()` tries `_match_qa()` before `_match_entrypoint()`.
- `_match_qa()` can match by exact prompt, prompt substring, reverse substring, then token overlap.
- `_match_entrypoint_alias()` later uses package-owned aliases with substring matching: `_match_package_entrypoint_alias()` returns the first alias where `alias.normalized_alias in normalized_question`.
- `MaterialPackage.entrypoint_question_aliases_by_match_order` sorts aliases by match priority for runtime routing, so short localized aliases can match inside longer user questions.

The current `qa alias overlap` diagnostic is exact-only, so it catches `question: chat` versus alias `chat`, but not alias `chat` inside `can you read chat messages?`, or Japanese `\u30c1\u30e3\u30c3\u30c8` inside a longer privacy prompt.

## Suggested Implementation Location

Implement this inside `src/ai_presenter/runtime/diagnostics.py`, next to `_diagnose_qa_alias_overlaps()`.

Recommended shape:

- Add a new check in `_diagnose_material_package()` immediately after `_diagnose_qa_alias_overlaps(material_package)`.
- Name it something distinct from exact overlap, for example `qa alias substring`.
- Iterate `material_package.qa_question_candidates` and `material_package.entrypoint_question_aliases`.
- Flag when:
  - `alias.normalized_alias` is non-empty.
  - `alias.normalized_alias != candidate.normalized_question`.
  - `alias.normalized_alias in candidate.normalized_question`.
  - `alias.entrypoint_id` is not in `candidate.item.related_entrypoint_ids`.
- Group conflicts by `(candidate.normalized_question, id(candidate.item))`, similar to `_diagnose_qa_alias_overlaps()`, so localized variants of one Q&A item report as one prompt conflict.
- Reuse existing helpers where possible:
  - `_format_qa_item_label()`
  - `_qa_question_language()`
  - `_unique_alias_entrypoint_ids()`
  - `_ordered_unique()`

Consider a formatter like `_format_qa_alias_substring_conflict(material_package, normalized_question, candidates, aliases)`. It can mirror `_format_qa_alias_overlap_conflict()` but say `contains aliases for ...` instead of `shadows ...`.

Keep severity as `WARN`. This is a routing/privacy risk, but it is not necessarily a broken package because related entrypoint IDs can make some overlaps intentional and safe.

## Test Design

Add focused unit tests to `tests/unit/test_diagnostics.py` using the existing `_alias_qa_package()` helper.

Recommended cases:

- Warn when an unrelated package alias is a substring of a Q&A prompt:
  - Alias: `demo.chat` -> `{"en": ["chat"]}`
  - Q&A: `question: "Can you read chat messages?"`, no related entrypoints.
  - Expect `qa alias substring` status `WARN`.
  - Expect detail includes normalized prompt, alias language, `demo.chat`, and first Q&A label.

- Allow substring when the Q&A item is related to the same entrypoint:
  - Same alias and prompt.
  - Q&A includes `relatedEntrypointIds: ["demo.chat"]`.
  - Expect `qa alias substring` status `OK`.

- Warn for localized Japanese substring:
  - Alias: `demo.chat` -> `{"ja": ["\u30c1\u30e3\u30c3\u30c8"]}`
  - Q&A localized question: `{"ja": ["\u30c1\u30e3\u30c3\u30c8\u5185\u5bb9\u3084\u53c2\u52a0\u8005\u540d\u3092\u8aad\u307f\u4e0a\u3052\u3089\u308c\u307e\u3059\u304b"]}`
  - No related entrypoint, or related entrypoint only to another route.
  - Expect `WARN`.

- Do not double-count exact overlaps:
  - Alias and Q&A prompt both normalize to `chat`.
  - Existing `qa alias overlap` should warn.
  - New substring check should stay `OK` if `alias.normalized_alias == candidate.normalized_question` is excluded.

Update CLI coverage in `tests/unit/test_cli.py` with a temp package doctor case parallel to `test_doctor_warns_when_qa_question_shadows_entrypoint_alias()`. Assert:

- `[WARN] qa alias substring:` appears.
- Detail includes the longer prompt and the shadowed entrypoint.
- Doctor exits `0` with warnings, not failures.

`tests/unit/test_material_packages.py` probably does not need direct changes unless the implementation adds new package-level indexes. If the real `packages/ringcentral-video.yaml` remains with the current Japanese substring risk, update the package expectation tests only if the new diagnostic changes doctor output assertions.

## Expected Diagnostic Copy

Suggested OK detail:

```text
71 Q&A question prompts have no unsafe package-owned alias substrings
```

Suggested WARN detail:

```text
1 Q&A question prompt contains unsafe package-owned alias substrings: 'can you read chat messages?' (Q&A languages: en; alias languages: en) appears in #1 Can you read chat messages? and contains aliases for demo.chat; first match is Q&A #1 Can you read chat messages?
```

For multiple conflicts:

```text
2 Q&A question prompts contain unsafe package-owned alias substrings: ...; and 1 more
```

The wording should preserve the existing diagnostics style:

- Start with count.
- Use singular/plural `prompt` or `prompts`.
- Include normalized prompt with `!r`.
- Include Q&A languages and alias languages.
- Include Q&A item label and affected entrypoint IDs.
- Include `first match is Q&A ...` because Q&A matching runs before alias routing.

## RingCentral Package Expectation

The current package likely produces at least one warning after this check because:

- `ringcentral.video.toolbar.chat` owns Japanese aliases including `\u30c1\u30e3\u30c3\u30c8`.
- A privacy Q&A localized Japanese prompt asks whether chat contents or participant names can be read aloud.
- That Q&A is a privacy/safety answer, not an instruction to open Chat, and it does not appear to be related to `ringcentral.video.toolbar.chat`.

That is the intended signal from cycle 058. Decide in implementation whether to:

- Keep the warning and make doctor surface it, documenting the known risk.
- Or resolve the package by adding the relevant `relatedEntrypointIds` if the answer intentionally explains Chat and Participants locations, but only if that would not weaken the privacy boundary.

## Verification Commands

Run targeted tests first:

```powershell
pytest tests/unit/test_diagnostics.py -q
pytest tests/unit/test_cli.py -q
```

Then run package-focused tests:

```powershell
pytest tests/unit/test_material_packages.py -q
```

Finally run a real doctor command to inspect copy:

```powershell
ai-presenter doctor --profile ringcentral-video-bind-speaker --package ringcentral-video
```

If `ai-presenter` is not on PATH in the local shell, use the repo's normal test runner or module entrypoint instead.

## Risks

- False positives: short aliases such as `chat`, `notes`, `record`, or CJK two-to-four-character aliases can naturally occur in explanatory privacy prompts. Keeping related-entrypoint exemptions reduces noise.
- False negatives: substring checks still depend on `normalize_question_prompt()` output. If normalization later strips punctuation or whitespace differently, tests should cover CJK and Latin examples.
- Diagnostic churn: `test_doctor_loads_profile_package_and_flow()` currently expects all three package diagnostics to be OK for RingCentral. Adding this check may require updating the doctor output assertions and warning counts.
- Runtime semantics: the new diagnostic should describe risk only. Do not change `_match_qa()` or `_match_package_entrypoint_alias()` as part of this diagnostic work.
- Copy length: doctor output is single-line per check, so only show the first conflict plus `; and N more`, matching existing diagnostics.
