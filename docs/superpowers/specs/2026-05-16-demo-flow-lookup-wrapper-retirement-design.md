# Demo Flow Lookup Wrapper Retirement Design

## Problem

Demo flow lookup is indexed on `MaterialPackage`, but `runtime.package_demo` still exposes a `demo_flow_by_id()` wrapper. The wrapper does not add behavior and makes the lookup owner less clear.

## Design

Remove the wrapper and route all production callers to `MaterialPackage.demo_flow_by_id()`. This preserves the same lookup semantics and error messages while leaving `runtime.package_demo` focused on action execution.

## Testing

Unit tests will assert the package demo runtime no longer exports the wrapper. Existing CLI, diagnostics, material package, and runtime factory tests will protect valid-flow and missing-flow behavior.
