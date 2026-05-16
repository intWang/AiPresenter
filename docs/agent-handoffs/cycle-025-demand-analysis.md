# Cycle 025 Demand Analysis: RingCentral Flow Localization Closure

Date: 2026-05-16
Scope: Review only; no code changes recommended in this handoff.

## Recommendation

Use Cycle 025 to close the last RingCentral Video demo-flow Chinese narration gap by localizing
`meeting-controls-tour` and adding one reusable package-level localization coverage test.

This is the best small slice because recent cycles already localized Q&A, aliases,
`meeting-control-map-demo`, `vbg-blur-demo`, `meeting-basics-demo`, and adaptive Invite narration.
The remaining public flow gap is now narrow and easy to explain: `meeting-controls-tour` still has
0/22 `narration.localizedText.zh` entries while every other RingCentral demo flow has complete
Chinese narration.

## Evidence From Current Workspace

- `vbg-blur-demo`: 4/4 steps have Chinese localized narration.
- `meeting-basics-demo`: 3/3 steps have Chinese localized narration.
- `meeting-control-map-demo`: 22/22 steps have Chinese localized narration.
- `meeting-controls-tour`: 0/22 steps have Chinese localized narration.
- RingCentral Q&A coverage is complete for current package data: 8/8 items have Chinese localized
  questions and answers.
- Chinese question alias support is broad: 49 package-owned zh alias records.
- `tests/unit/test_material_packages.py` currently asserts Chinese coverage for
  `meeting-control-map-demo` and the two short flows, but not for all demo flows.
- `README.md` and the manual runbook steer active Chinese/demo usage toward
  `meeting-control-map-demo`, so the user-facing breakage is limited but still confusing when
  operators list or select the older long tour.

## User Value

- Chinese users can run any RingCentral package demo flow without falling back to English narration.
- Operators no longer need hidden knowledge that `meeting-control-map-demo` is localized while
  `meeting-controls-tour` is not.
- A reusable coverage test prevents future demo flows from quietly shipping English-only narration
  after the package has established Chinese as a supported output family.

## Proposed Acceptance Criteria

- Add `narration.localizedText.zh` to all 22 existing `meeting-controls-tour` steps in
  `packages/ringcentral-video.yaml`.
- Preserve the existing English `narration.text` strings as ASCII and do not change flow IDs,
  step IDs, action operations, entrypoint IDs, placement, or action offsets.
- Chinese copy should be authored naturally and preserve visible RingCentral UI labels such as
  `Invite`, `Participants`, `Chat`, `Mute`, `Share`, `React`, `Raise hand`, `More`, `Notes`,
  `Settings`, and `Leave` where those labels match the UI.
- Add or generalize a test in `tests/unit/test_material_packages.py` proving every RingCentral demo
  flow step has nonblank `localized_text["zh"]` with at least one CJK character.
- Add one render assertion for a `meeting-controls-tour` step using
  `PresenterVoiceSettings(language="zh")` so the test proves runtime narration selection uses the
  localized string.
- Run focused package tests, then the full unit suite if time allows.

## Risks

- The long tour overlaps heavily with `meeting-control-map-demo`; copied-but-not-identical Chinese
  phrasing can drift between two 22-step explanations.
- PowerShell may display Chinese as mojibake even when files are valid UTF-8. Judge by file encoding
  and tests, not terminal rendering.
- Some `meeting-controls-tour` steps explain risky or privacy-sensitive controls. Localization
  should keep the current safety posture: recording and leave remain explain-only, and share/chat/
  invite/participants copy should not imply the presenter reads private content.
- A blanket coverage test will affect future demo-flow authors. That is useful, but implementers
  should decide whether the policy is "all RingCentral flows need zh" rather than only adding the
  test for the currently known flows.

## Out Of Scope

- Do not change runtime localization fallback, voice routing, provider selection, CLI flags, or
  controller behavior.
- Do not add new languages beyond existing `en` and `zh`.
- Do not rename, remove, or alias `meeting-controls-tour` in this cycle.
- Do not change RingCentral open-step locators, adaptive demo behavior, or manual acceptance
  evidence levels.
- Do not run live RingCentralVideo acceptance as part of this localization slice.

## Alternatives Considered

- **Flow-list localization report in CLI:** Useful for operator awareness, but it leaves the actual
  unsupported Chinese flow in place. Better as a follow-up once coverage is complete.
- **Document the gap only:** Low risk, but Cycle 023 and 024 already narrowed the problem enough
  that implementation is now the higher-value move.
- **Retire or alias `meeting-controls-tour`:** Possible later, but it changes user-facing flow
  selection semantics. Localizing it first is smaller and preserves compatibility.
- **UI/control surface improvement:** The controller already defaults to the requested flow and the
  README/runbook promote `meeting-control-map-demo`. The last obvious RingCentral UX mismatch is
  content coverage, not a missing control.

## Suggested Verification

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py
```

If focused tests pass and the cycle edits only package/test/docs files, run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q
```

## Follow-Up After Cycle 025

Once all RingCentral demo flows have Chinese coverage, consider a small CLI or docs improvement that
surfaces per-flow localization status in `ai-presenter flows --package ringcentral-video`, or a
separate reporting helper for package maintainers. That should be a separate UX slice, not mixed
with the YAML localization work.
