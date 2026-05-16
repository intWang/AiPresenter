# Cycle 044 Demand Analysis

## Recommended Slice

Retire the `runtime.package_demo.demo_flow_by_id()` compatibility wrapper and route callers directly through `MaterialPackage.demo_flow_by_id()`.

## User Value

Ai Presenter already indexes demo flows on the material package. Keeping a second wrapper in the package demo runtime makes flow lookup look like executor behavior, even though the source of truth is the package model. Removing the wrapper gives maintainers one obvious lookup path and reduces confusion before future demo-flow automation work.

## Acceptance Criteria

- CLI demo and controller dry runs still load valid flows and preserve missing-flow error text.
- Doctor flow diagnostics still report missing flows through the package model error.
- Runtime factory execution uses `material_package.demo_flow_by_id()` directly.
- `ai_presenter.runtime.package_demo` no longer exports `demo_flow_by_id`.
- Existing package action executor behavior is unchanged.

## Out Of Scope

- No changes to `MaterialPackage.demo_flow_by_id()` behavior or error text.
- No flow-index schema changes.
- No RingCentral flow content changes.
- No acceptance draft or validation target changes.
