# Demo Flow Lookup Design

Date: 2026-05-16

## Context

Material package entrypoints now have runtime indexes, but demo flows still use `demo_flow_by_id()` as a linear scan. As packages grow, missing flow IDs should fail fast and consistently across CLI, doctor, runtime, and controller paths.

There is a specific safety trap: the controller currently appends the synthetic `question-answer-demo` flow through `model_copy(update={"demo_flows": ...})`. Pydantic does not rerun validators for that copy path, so private indexes can become stale if flow indexes are added without a safe reconstruction helper.

## Design

Make `MaterialPackage` the owner of demo-flow lookup:

- Build a private `_demo_flows_by_id` index during validation.
- Reject duplicate `demoFlows.id` values.
- Expose a read-only `demo_flows_by_id` mapping for diagnostics/tests.
- Add `demo_flow_by_id(flow_id)` with the existing unknown-flow message shape.
- Keep `runtime.package_demo.demo_flow_by_id()` as a compatibility wrapper that delegates to the package method.
- Add `with_demo_flow(flow)` to rebuild a package through full model validation when a synthetic flow is appended.
- Update controller question-flow construction to use `with_demo_flow()` instead of raw `model_copy(update=...)`.

Do not override Pydantic `model_copy()` in this cycle. A narrow explicit helper is easier to reason about and avoids surprising callers who expect Pydantic copy semantics.

## Behavior

- Unknown flow errors remain shaped as `Unknown demo flow: <id>. Available flows: <ids|none>`.
- Duplicate flow IDs fail package validation.
- `demo_flow_by_id()` lookup becomes index-backed.
- Synthetic `question-answer-demo` remains resolvable by flow lookup after controller question handling.
- CLI and doctor use the same lookup/error source.

## Non-Goals

- No immutable package lists in this cycle.
- No broad refactor of package mutation patterns.
- No change to entrypoint lookup behavior beyond rebuilding indexes through `with_demo_flow()`.

## Acceptance Criteria

- `MaterialPackage.demo_flows_by_id` is read-only.
- `MaterialPackage.demo_flow_by_id()` returns indexed flow objects and raises the unified message.
- Duplicate `demoFlows.id` values fail validation.
- Runtime indexes do not leak into `model_dump()`.
- `with_demo_flow()` returns a rebuilt package where the appended flow is resolvable.
- CLI demo and controller missing-flow errors remain clear and consistent.
- Doctor missing-flow output uses the same unknown-flow message.
- Runtime flow validation happens before desktop setup.
- Controller question-answer synthetic flow works with indexed lookup.

## Risks

- Direct mutation of `package.demo_flows` after validation can still stale indexes; existing code should use `with_demo_flow()` for structural changes.
- Tightening duplicate flow ID validation can reject malformed packages that were previously accepted.
- Some diagnostics tests may need wording updates because doctor should now surface the unified unknown-flow message.
