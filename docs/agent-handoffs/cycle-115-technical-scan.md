# Cycle 115 Technical Scan: Skill Experience Crystallization

Date: 2026-05-16
Scope: technical scan only. This handoff recommends one low-risk documentation artifact and does not implement it.

## Goal

Capture reusable AiPresenter maintenance experience without changing runtime presenter behavior, package YAML, production code, profiles, tests, generated coverage, git history, or Codex home skills.

## Scan Summary

The smallest safe next slice is a repo-local maintenance guide, not a new active presenter skill and not a Codex/superpowers skill.

| Area inspected | Current state | Recommendation |
| --- | --- | --- |
| Agent handoffs | Recent cycles use `docs/agent-handoffs/cycle-###-technical-scan.md` for recommendation-only scans and `cycle-###-experience.md` for cycle-local lessons. | Keep this file as the Cycle 115 scan. Do not use handoffs as the durable artifact for future maintainers. |
| Durable knowledge docs | `docs/knowledge/ringcentral-video/` is the only canonical knowledge bundle today, with source/evidence indexes and focused topic docs such as `runtime-safety-routing.md`. | Add a compact maintenance guide under `docs/knowledge/` only when implementing the next slice. |
| Repo superpowers docs | `docs/superpowers/specs/` and `docs/superpowers/plans/` hold implementation designs and plans, not evergreen runtime or maintainer knowledge. | Do not put the crystallized guide there unless the next cycle is writing a spec/plan rather than durable knowledge. |
| AiPresenter presenter skills | Active presenter skills live in `presenter/skills/*.md`, are referenced by profile `narration.skillPaths`, and are mirrored in `src/ai_presenter/presenter/skills/*.md`. `tests/unit/test_presenter_skill_packaging.py` requires the repo and packaged copies to match. | Do not add an active presenter skill for this slice. That would require profile/package/test changes and would alter provider prompt context. |
| Codex home skills/plugins | Codex skills live outside the repo under `C:\Users\rcadmin\.codex\...`. | Do not edit or recommend editing Codex home skills for AiPresenter maintenance. Keep the artifact inside the repo. |

## Recommended Artifact

Create one docs-only maintenance guide in a future implementation cycle:

```text
docs/knowledge/ai-presenter-maintenance.md
```

Why this location:

- The content is durable repo knowledge, not a transient cycle handoff.
- The topic is repo-wide AiPresenter maintenance, so it should not be placed inside `docs/knowledge/ringcentral-video/`, which is app-package-specific.
- A single file avoids creating a new knowledge subdirectory and index system before there are multiple AiPresenter-wide docs.
- It does not activate any runtime behavior, provider prompt text, profile skill path, packaged resource, or Codex skill.

If maintainers later create multiple AiPresenter-wide knowledge docs, they can promote this to a directory with an index. That should be a separate documentation-structure cycle.

## Content To Include

Keep the guide short and maintenance-oriented. Suggested outline:

1. Purpose and boundaries
   - Explain that the guide is for AiPresenter repo maintenance decisions.
   - State that it is not a runtime presenter skill, package fact source, acceptance evidence log, or Codex skill.
2. Skill layer map
   - Distinguish `presenter/skills/*.md` from `docs/superpowers/*` and Codex home skills.
   - Note that active presenter skills are loaded through profile `narration.skillPaths`.
   - Note that packaged copies under `src/ai_presenter/presenter/skills/` must stay byte-for-byte aligned with repo skills.
3. Experience crystallization rules
   - Durable product/package facts belong under `docs/knowledge/`.
   - Cycle-local lessons belong under `docs/agent-handoffs/`.
   - Implementation designs and task plans belong under `docs/superpowers/specs/` and `docs/superpowers/plans/`.
4. Safe change boundaries
   - Docs-only maintenance notes should not edit package YAML, production code, profiles, tests, or generated coverage.
   - Active presenter skill changes require the mirrored packaged skill update and the presenter-skill packaging test.
   - Runtime safety or RingCentral-specific guidance should link to `docs/knowledge/ringcentral-video/runtime-safety-routing.md` instead of duplicating it.
5. Validation checklist
   - Markdown path checks.
   - Placeholder/trailing-whitespace checks.
   - Scope check proving only the intended guide changed.
   - Optional tests only if an active presenter skill or package resource changes.

## Content To Exclude

- Do not copy full contents of `presenter/soul.md`, `presenter/memory.md`, or `presenter/skills/*.md`.
- Do not add package-specific RingCentral route, privacy, locator, state, or acceptance details except as links to existing knowledge docs.
- Do not include user-private coaching beyond what is already committed in repo docs.
- Do not claim new live acceptance, runtime behavior, package coverage, or safety policy.
- Do not add or modify `narration.skillPaths`.
- Do not modify `src/ai_presenter/presenter/skills/` unless the cycle explicitly changes active presenter skills.
- Do not edit `C:\Users\rcadmin\.codex\skills`, `C:\Users\rcadmin\.codex\superpowers`, or plugin cache content.
- Do not stage `.coverage`.

## Validation For Future Implementation

For the recommended docs-only guide:

```powershell
rg -n "[ \t]$" docs\knowledge\ai-presenter-maintenance.md
rg -n "docs/knowledge/ringcentral-video/runtime-safety-routing.md|presenter/skills|src/ai_presenter/presenter/skills|narration.skillPaths" docs\knowledge\ai-presenter-maintenance.md
git diff --check -- docs\knowledge\ai-presenter-maintenance.md
git status --short --untracked-files=all
```

No pytest command is required for a docs-only guide. If the next cycle instead changes active presenter skills, run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\unit\test_presenter_skill_packaging.py tests\unit\test_config_loader.py -q -o addopts=""
```

## Risk Notes

- Putting the artifact in `presenter/skills/` would silently change provider prompt context once profiles load it, or create drift if profiles do not load it. That is too much behavior surface for an experience-crystallization slice.
- Putting the artifact in `src/ai_presenter/presenter/skills/` without the repo copy would violate the packaging parity convention.
- Putting it under `docs/superpowers/` would make the content look like an implementation spec or plan instead of durable repo knowledge.
- Putting it under `docs/knowledge/ringcentral-video/` would blur repo-wide AiPresenter maintenance with RingCentral Video package knowledge.
- Link validation should stay simple. Validate literal repo paths and avoid broad generated-anchor checking unless a future docs index needs it.
- `.coverage` is already modified in the worktree and must remain unstaged.

## Handoff Scope Check

This Cycle 115 technical scan should create exactly one file:

```text
docs/agent-handoffs/cycle-115-technical-scan.md
```

It intentionally does not implement `docs/knowledge/ai-presenter-maintenance.md`, update indexes, edit active skills, alter package YAML, change tests, touch profiles, or stage `.coverage`.
