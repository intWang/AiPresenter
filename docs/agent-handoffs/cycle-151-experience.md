# Cycle 151 Experience: Spanish Alias Boundary

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`

## What This Cycle Learned

- Let the demand scan break ties. Cycle 151's highest-value slice was Spanish
  alias/display polish, not a new tone. It improves operator input ergonomics
  while staying inside existing canonical language `es`.
- The technical scan's `empathetic -> support` idea is still a good next-cycle
  candidate. It was deferred because doing tone and language alias work in one
  cycle would muddy the user-facing boundary.
- The risk scan's wording discipline matters. Use narrow verbs such as
  `normalizes`, `lists`, `reports`, and `checks`; reserve `supports`,
  `validated`, `ready`, and `accepted` for sentences that name the exact
  provider, profile, command, and evidence source.
- Spanish aliases do not expand provider support. They only map additional
  input spellings, such as `es-419`, `es-la`, `latam-spanish`,
  `latin-american-spanish`, and `Espa\u00f1ol`, to existing `es`.

## TDD Evidence Pattern

- Red should come from focused tests before the runtime alias map changes:
  language normalization rejects the new aliases, public alias tuples omit
  them, package key resolution does not normalize them, and `voices` output
  does not list them.
- Green should come only after adding the aliases to `_LANGUAGE_ALIASES` and
  rerunning the focused voice and CLI tests. Passing catalog tests should also
  prove non-ASCII aliases remain ASCII-safe in output, for example
  `espa\\xf1ol`.
- Do not use final passing tests as the whole story. Future handoffs should
  record the red failure symptom and the green command/output summary so the
  cycle remains auditable.

## Safe Alias Wording

- Say "the alias normalizes user input to canonical `es`."
- Say "`voices` lists aliases separately from profile compatibility."
- Say "`entrypoints --language <alias>` reports package-local display keys; it
  is not runtime voice validation."
- Avoid "Spanish is ready", "all profiles support Spanish", "provider-ready",
  "validated in RingCentral", or "alias unlocks runtime support."
- Keep display contracts plain: `language_label("es") == "Spanish"` and
  package-local output should still show `Language: es`.

## Next Cycle Suggestions

- If continuing alias polish, add a narrow package-local smoke around
  `entrypoints --language es-419` or `localization-report --language
  Espa\u00f1ol`, while keeping unknown package-only keys such as `de` raw.
- If returning to tone work, implement `empathetic -> support` as an alias-only
  TDD slice with runtime normalization, public alias tuple, and `voices` catalog
  coverage.
- Keep Spanish local SAPI/Piper support, provider routing expansion, live
  RingCentral acceptance, package YAML changes, profiles, README edits, and
  `.coverage` out of alias-only cycles unless a future task explicitly expands
  scope.
