# Cycle 143 Experience Notes

## What Changed

Cycle143 aligned durable docs with the Cycle142 CLI marker contract:

- README now explains `entrypoints --language` as package-local entrypoint
  display metadata inspection.
- README names `Spanish` and `es-MX` as aliases that normalize to package key
  `es` and therefore print `Language: es`.
- The language lifecycle now records the Spanish marker contract:
  `Language: es`, `(title: localized)`, `(title: fallback)`, `(localized)`,
  and `(fallback)`.
- A small docs guard in `tests/unit/test_cli.py` prevents README/lifecycle
  wording from drifting back into runtime-support claims.

## Useful Pattern

When a cycle is "docs-only" but the risk is durable wording drift, call the
scope documentation-focused instead of absolutely tests-free. A focused docs
guard is acceptable when it reads documentation text and does not exercise or
change product behavior.

For user-facing docs, keep the command contract short:

- what command to run;
- what resolved package key is printed;
- what localized/fallback markers mean;
- what the markers do not prove.

For lifecycle docs, keep the maintainer boundary explicit:

- marker output is package-local inspection;
- optional display metadata is not required localization;
- marker output is not query routing, provider readiness, controller/demo
  execution, or live RingCentral Video acceptance.

## Review Lesson

The first README edit still omitted `Spanish` / `es-MX`, even though the cycle
was motivated by alias-aware CLI inspection. If a cycle starts from a behavior
guard, the docs acceptance criteria should mirror every behavior axis that made
the guard valuable: canonical key, aliases, localized markers, fallback markers,
and no-runtime-support boundary.

## Next Cycle Seed

Consider a small maintenance pass that audits `docs/knowledge/ringcentral-video`
for similar "inspection versus acceptance" wording and collects any stale or
ambiguous RingCentral Video validation phrases into one cleanup plan.
