# Doctor Question Alias Readiness Design

Date: 2026-05-16

## Context

Package-owned `questionAliases` let localized operator questions route directly to curated RingCentral entrypoints. Cycle 035 made runtime matching deterministic by using a precomputed longest-first order, but duplicate normalized aliases can still be surprising. If two entrypoints own the same normalized alias, the earlier entrypoint wins silently.

`doctor` is the right surface for this because it already validates profile, package, flow, localization, RingCentral config, and voice readiness before a demo.

## Design

Add a material-package diagnostic named `question aliases`.

Healthy packages return:

```text
[OK] question aliases: 49 package-owned aliases have no cross-entrypoint duplicates
```

Packages with conflicts return:

```text
[WARN] question aliases: 1 duplicate normalized package-owned question alias: 'chat' (languages: en) maps to demo.alpha, demo.bravo; first match is demo.alpha
```

Warnings are non-fatal. The current runtime behavior remains deterministic and unchanged.

## Rules

- Normalize using the already-built `EntrypointQuestionAlias.normalized_alias`.
- Group by normalized alias across languages because runtime matching does not use language.
- Warn only when more than one unique entrypoint ID owns the alias.
- Include normalized alias, languages, conflicting entrypoints, and first-match entrypoint.
- Keep output compact if multiple conflicts exist.

## Non-Goals

- No package schema rejection.
- No alias renaming.
- No matching algorithm changes.
- No legacy alias diagnostics.
- No live RingCentral automation.

