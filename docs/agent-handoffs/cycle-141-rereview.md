# Cycle 141 Focused Rereview: Spanish Display Metadata Routing Guard

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`
Scope: rereview of the current Cycle141 diff only:
`tests/unit/test_questions.py` and
`docs/agent-handoffs/cycle-141-*.md`.

## Findings

### [P2] Candidate-token guard omits `title_or_id_tokens`

`tests/unit/test_questions.py:419` builds `candidate_tokens` from
`id_tokens`, `title_tokens`, `area_tokens`, and `purpose_tokens`, then asserts
Spanish-only localized display tokens are disjoint from that union. That is a
real-package candidate assertion and addresses the first review's broad gap,
but it does not cover every score-relevant token field on
`EntrypointMatchCandidate`.

The runtime scorer also reads `candidate.title_or_id_tokens` when deciding
whether a query matched at all and when applying the exact title/id bonus. A
future regression that added localized title/purpose tokens only to
`title_or_id_tokens` could pass the new test while still making localized
display metadata route questions. The guard should assert
`candidate.title_or_id_tokens == candidate.title_tokens | candidate.id_tokens`
and include `title_or_id_tokens` in the localized-token exclusion check.

### [P2] Localized-only probe is not actually a no-match probe for all entries

`tests/unit/test_questions.py:460` now derives each negative query from
localized tokens after subtracting all package entrypoint candidate tokens.
That avoids obvious false positives from canonical product labels such as
`video`, `Background`, `Blur`, `More`, and `Settings`, but the generated
video-menu probe still matches package Q&A.

Observed generated probe:

```text
entrypoint: ringcentral.video.toolbar.video-menu
query: abre ajustes camara cambiar controles de el la ni para revisar sin y
response.entrypoint_id: None
response.can_operate: False
response.answer_text: Usa el panel Participants para explicar el conteo...
```

Because the test only asserts `entrypoint_id is None`, `can_operate is False`,
and a nonblank answer, it passes even when the probe is answered by unrelated
Spanish Q&A rather than by the no-match fallback. That weakens the resolution
of the second review finding: the test no longer pins fallback wording, but it
also no longer proves these localized-only probes are no-match prompts. A safer
probe should also subtract or otherwise avoid package Q&A and alias terms, or
use the synthetic no-overlap package recommended by the risk scan for the
runtime no-match boundary.

### [P3] Handoff docs overstate what the current negative test proves

`docs/agent-handoffs/cycle-141-implementation.md:75` still describes
handpicked localized-purpose fragments and says each response has Spanish
no-match wording containing `No encontre`, even though the current test derives
queries dynamically and no longer asserts fallback wording. The later
"review adjustment" section partly corrects this, but the earlier test-intent
section is stale and can mislead the next cycle.

`docs/agent-handoffs/cycle-141-experience.md:28` calls the current generated
queries "no-match probes." The video-menu generated query currently returns an
unrelated Q&A answer, so the docs should distinguish "no entrypoint match" from
"no-match fallback" unless the test is tightened.

## Resolved From Prior Review

- The first review asked for a real-package candidate-token assertion. The
  current diff adds one for the three Cycle140 RingCentral entrypoints, so the
  main gap is now the missing score-relevant `title_or_id_tokens` field rather
  than absence of a candidate-token test.
- The prior brittle assertion on the exact Spanish fallback spelling was
  removed. That avoids copy-edit failures, but the replacement assertion should
  still prove the prompt reached the intended no-match path.

## Verification

Inspected:

- `git diff -- tests/unit/test_questions.py docs/agent-handoffs/cycle-141-*.md`
- `tests/unit/test_questions.py`
- `docs/agent-handoffs/cycle-141-demand-analysis.md`
- `docs/agent-handoffs/cycle-141-experience.md`
- `docs/agent-handoffs/cycle-141-implementation.md`
- `docs/agent-handoffs/cycle-141-review.md`
- `docs/agent-handoffs/cycle-141-risk-scan.md`
- `docs/agent-handoffs/cycle-141-technical-scan.md`
- `src/ai_presenter/packages/models.py`
- `src/ai_presenter/runtime/questions.py`
- `packages/ringcentral-video.yaml`

Focused tests run:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py::test_ringcentral_spanish_alias_routes_render_optional_display_metadata tests\unit\test_questions.py::test_ringcentral_spanish_display_metadata_is_not_part_of_match_candidates tests\unit\test_questions.py::test_ringcentral_spanish_display_metadata_fragments_do_not_create_matches tests\unit\test_questions.py::test_localized_entrypoint_title_alone_does_not_create_a_match
```

Result: `6 passed in 1.26s`.

Manual localized-only query probe run against the real RingCentral package:

```powershell
@'
from pathlib import Path
from ai_presenter.packages.loader import load_material_package
from ai_presenter.packages.models import match_field_tokens
from ai_presenter.runtime.questions import answer_question
from ai_presenter.runtime.voice import PresenterVoiceSettings

package = load_material_package(Path('packages/ringcentral-video.yaml'))
entrypoint_ids = (
    'ringcentral.video.toolbar.audio-menu',
    'ringcentral.video.toolbar.video-menu',
    'ringcentral.video.more.background',
)
all_candidate_tokens = set().union(*(
    candidate.id_tokens | candidate.title_tokens | candidate.area_tokens | candidate.purpose_tokens
    for candidate in package.entrypoint_match_candidates
))
for entrypoint_id in entrypoint_ids:
    entrypoint = package.entrypoint_by_id(entrypoint_id)
    localized_tokens = match_field_tokens(' '.join([
        entrypoint.localized_titles['es'],
        entrypoint.localized_purposes['es'],
    ]))
    query = ' '.join(sorted(localized_tokens - all_candidate_tokens))
    response = answer_question(
        package=package,
        question=query,
        voice=PresenterVoiceSettings(language='es'),
    )
    print(entrypoint_id, query, response.entrypoint_id, response.can_operate, response.answer_text)
'@ | .\.venv\Scripts\python.exe -
```

Result: audio-menu and background probes returned Spanish no-match fallback;
the video-menu probe returned an unrelated Spanish Participants Q&A answer
with `entrypoint_id is None` and `can_operate is False`.

Workspace notes:

- `.coverage` was already modified and was not touched.
- No source, test, package YAML, or existing Cycle141 handoff docs were edited
  by this rereview.

## Main-Session Resolution

All rereview findings were addressed after this document was written:

- `test_ringcentral_spanish_display_metadata_is_not_part_of_match_candidates`
  now asserts `candidate.title_or_id_tokens == candidate.title_tokens |
  candidate.id_tokens` and includes `title_or_id_tokens` in the localized-token
  exclusion check.
- The localized-only negative probe now subtracts every package candidate token,
  including `title_or_id_tokens`, and calls `_match_entrypoint()` directly.
  This avoids unrelated Q&A answers while preserving the intended entrypoint
  matcher contract.
- The Cycle141 implementation, review, and experience docs were updated to stop
  describing the old handpicked fallback-wording test and to describe the final
  matcher-level guard instead.

Post-resolution focused verification:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py::test_ringcentral_spanish_alias_routes_render_optional_display_metadata tests\unit\test_questions.py::test_ringcentral_spanish_display_metadata_is_not_part_of_match_candidates tests\unit\test_questions.py::test_ringcentral_spanish_display_metadata_fragments_do_not_create_matches tests\unit\test_questions.py::test_localized_entrypoint_title_alone_does_not_create_a_match
```

Result: `6 passed`.
