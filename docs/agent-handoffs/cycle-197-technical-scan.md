# Cycle 197 Technical Scan: Presenter Tone Behavior Matrix

Date: 2026-05-17

## Read-Only Findings

The existing runtime tone contract lives in `src/ai_presenter/runtime/voice.py`.
Current canonical tones are exposed through `PRESENTER_TONE_CHOICES`, public
aliases through `presenter_tone_aliases(...)`, and public descriptions through
`presenter_tone_description(...)`.

`docs/knowledge/ringcentral-video/runtime-safety-routing.md` already documents
the RingCentral route-safety invariant. The new tone matrix should link to it
instead of duplicating package safety policy.

## Recommended Durable Doc

Use `docs/knowledge/presenter-tone-behavior-matrix.md`.

The doc is repo-wide runtime knowledge, not RingCentral-only evidence. The
`presenter-` prefix was kept to avoid confusing this with unrelated tone or
copywriting guidance.

## Test Targets

- Add a matrix contract test near the existing voice tests in
  `tests/unit/test_voice.py`.
- Iterate over `PRESENTER_TONE_CHOICES` and require the durable doc to include
  every tone, label, alias list, and public description from runtime source.
- Guard core phrases for style-only routing boundaries, localized behavior,
  English deterministic prefixes, and Chinese SAPI rate.
- Keep existing route invariant coverage in `tests/unit/test_questions.py`;
  no new routing behavior is needed for this docs slice.

## Phrases To Preserve

- `Tone is style-only.`
- `entrypoint_id`
- `can_operate`
- `questionPolicy`
- Q&A-first matching
- `create_question_interrupt_step(...)`
- `Sure.`
- `Happy to help.`
- `Let's walk through it.`
- `Certainly.`
- `Executive brief.`
- `Let's troubleshoot this.`
- `Safety note.`
- Chinese SAPI rate
- Japanese and Spanish localized text does not add English prefixes

## Drift Risks

- The matrix can go stale when `voice.py` gains a new tone, alias, or public
  description.
- Wording might overclaim `privacy`, `safety`, or `compliance` as policy
  controls instead of aliases for `careful`.
- Wording might imply repo tests or provider compatibility are live RingCentral
  acceptance evidence.
- RingCentral-specific route policy should stay in
  `docs/knowledge/ringcentral-video/runtime-safety-routing.md`.

## Verification Commands

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests/unit/test_voice.py
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests/unit/test_questions.py::test_ringcentral_sensitive_prompt_routing_is_tone_invariant
git diff --check
git status --short
```
