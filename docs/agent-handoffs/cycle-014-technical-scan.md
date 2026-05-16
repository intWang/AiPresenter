# Cycle 014 Technical Scan: Demo Flow Lookup

Date: 2026-05-16

## Existing Seams

- `runtime.package_demo.demo_flow_by_id()` currently scans `package.demo_flows`.
- `MaterialPackage` already owns entrypoint lookup through private indexes.
- `controller._target_with_question_flow()` appends a synthetic flow with `model_copy(update={"demo_flows": ...})`.
- `factory._run_material_demo_on_handle()` looks up the flow after desktop/provider setup has already happened in public entry points.

## Recommended Design

- Add `_demo_flows_by_id`, `demo_flows_by_id`, and `demo_flow_by_id()` to `MaterialPackage`.
- Reject duplicate flow IDs in package validation.
- Add `with_demo_flow(flow)` to rebuild through `MaterialPackage.model_validate()`.
- Update controller synthetic flow construction to use `with_demo_flow()`.
- Keep `runtime.package_demo.demo_flow_by_id()` as a compatibility wrapper delegating to the package method.
- Add early flow preflight in public runtime entry points.
- Update diagnostics to surface the unified unknown-flow message.

## Test Strategy

- Package index/read-only/unknown/duplicate/copy tests.
- Controller synthetic question-flow test that resolves via indexed flow lookup.
- CLI controller missing-flow test.
- Doctor missing-flow message test.
- Runtime fail-before-desktop test.

## Risks

- Direct list mutation after validation can still stale indexes; this cycle handles known structural mutation through `with_demo_flow()`.
- Avoid overriding `model_copy()` because that changes Pydantic expectations broadly.
