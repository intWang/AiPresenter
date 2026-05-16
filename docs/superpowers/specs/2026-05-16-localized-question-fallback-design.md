# Localized Question Fallback Design

## Problem

Ai Presenter supports Chinese voice settings and localized RingCentral Q&A, but the fallback used when no control matches is still English. This creates an awkward language switch at the exact point where the Presenter should be calm and understandable.

## Design

Add a tiny language-keyed fallback text map in `runtime.questions` and use it only in the no-match branch. The selected text will still pass through the existing voice rendering path, preserving tone handling and logging behavior.

## Testing

Add a focused Chinese no-match test that verifies the response is localized, non-operable, and has no entrypoint ID. Existing question tests continue to cover English fallback behavior and matching precedence.
