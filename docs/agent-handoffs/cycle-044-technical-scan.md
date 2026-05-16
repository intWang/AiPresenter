# Cycle 044 Technical Scan

## Current State

`MaterialPackage.demo_flow_by_id()` owns indexed flow lookup and helpful missing-flow errors. A thin wrapper remains in `runtime.package_demo`, and production imports use it from the CLI, diagnostics, and one factory path.

## Proposed Implementation

- Remove `demo_flow_by_id()` from `src/ai_presenter/runtime/package_demo.py`.
- Remove unused `DemoFlow` import from that module.
- Update `src/ai_presenter/cli.py` demo/controller commands to call `loaded_package.demo_flow_by_id(flow)` directly.
- Update `src/ai_presenter/runtime/diagnostics.py` to call `material_package.demo_flow_by_id(flow_id)` directly.
- Update `_run_material_demo_on_handle()` in `src/ai_presenter/runtime/factory.py` to call `material_package.demo_flow_by_id(flow_id)` directly.

## TDD Plan

1. Replace the old wrapper delegation unit test with a red test asserting `package_demo` no longer exports `demo_flow_by_id`.
2. Run the focused test and observe failure while the wrapper still exists.
3. Remove the wrapper and update call sites.
4. Run package demo, CLI, diagnostics, and runtime factory focused tests.

## Risk Notes

Behavior risk is low because the wrapper only delegates to the package method. The main risk is a stale import path in production or tests, which focused tests and `rg` should catch.
