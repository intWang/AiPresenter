# RingCentral Video Locator Matrix

Date: 2026-05-16

## Locator Confidence Legend

- `High repo confidence`: covered by stable package model and low-risk route, but still needs live dated acceptance.
- `Medium repo confidence`: UIA target exists but depends on label, occurrence, or panel state.
- `Low repo confidence`: coordinate fallback, overloaded occurrence, modal cleanup, or known layout variant.
- `Cycle 003 live observed`: confirmed only for RingCentral Video `26.2.20.355`, `en-US`, 100% DPI, window bounds `(500, 196, 1420, 836)`, empty-room state.
- `Explain only`: no executable route by design.

## Current Entrypoint Matrix

| Entrypoint | Locator Type | Cleanup | Confidence | Verification Need |
| --- | --- | --- | --- | --- |
| `ringcentral.develop.video.tab` | legacy profile action: focus + tab | none | Medium repo confidence | Verify RingCentralDevelop tab label and focus path. |
| `ringcentral.develop.video.start` | legacy profile action: button | none | Medium repo confidence | Verify Start button label and meeting process launch. |
| `ringcentral.video.overview` | explain-only | none | Explain only | No locator needed. |
| `ringcentral.video.top.meeting-info` | coordinate `x=31,y=21` | Escape | Low repo confidence | Verify top-left icon at window sizes/DPI. |
| `ringcentral.video.top.network-quality` | coordinate `x=68,y=21` | Escape | Low repo confidence | Verify signal icon location and hover/click behavior. |
| `ringcentral.video.top.views` | coordinate `xFromRight=237,y=21` | Escape | Low repo confidence | Verify right-side layout, fullscreen variants. |
| `ringcentral.video.top.report-issue` | coordinate `xFromRight=168,y=21` | modal | Low repo confidence | Verify dialog close path; Escape was previously unreliable. |
| `ringcentral.video.main.add-coworkers` | UIA `Add coworkers` button | modal | Low repo confidence | Cycle 003 saw `Add coworkers` button bounds `(1029,493,1329,541)`. Manually validate modal close on live RingCentral before relying on it. |
| `ringcentral.video.toolbar.audio` | UIA `Mute`, alternate `Unmute` | none | Medium repo confidence | Verify current accessible names. |
| `ringcentral.video.toolbar.audio-menu` | UIA `More`, occurrence 1 | Escape | Low repo confidence | Cycle 003 saw first visible `More` at `(633,766,652,785)` in empty-room state; verify system-default-audio toast behavior. |
| `ringcentral.video.toolbar.video` | UIA `Start video`, alternate `Stop video` | none | Medium repo confidence | Verify current accessible names. |
| `ringcentral.video.toolbar.video-menu` | UIA `More`, occurrence 2 | Escape | Low repo confidence | Cycle 003 saw second visible `More` at `(708,766,727,785)` in empty-room state; verify camera menu labels. |
| `ringcentral.video.settings.video` | UIA `More` occurrence 2 -> `More video settings` | settings | Low repo confidence | Verify route opens Video settings panel. |
| `ringcentral.video.settings.background` | UIA `More` occurrence 3 -> `Background` | settings | Low repo confidence | Verify More occurrence and Settings tab. |
| `ringcentral.video.settings.background.blur` | UIA `More` occurrence 3 -> `Background` -> `Blur` | settings | Low repo confidence | Verify Blur tile is available and selected state is safe. |
| `ringcentral.video.toolbar.share` | UIA `Share` | Escape | Medium repo confidence | Verify picker opens and final Share is not clicked. |
| `ringcentral.video.toolbar.invite` | UIA `Invite` | modal | Medium repo confidence | Verify modal close and private link redaction. |
| `ringcentral.video.toolbar.participants` | UIA `Participants` | toggle | Medium repo confidence | Verify toggle closes panel reliably. |
| `ringcentral.video.toolbar.chat` | UIA `Chat` | toggle | Medium repo confidence | Verify no private chat text is read. |
| `ringcentral.video.toolbar.react` | UIA `React` | Escape | Medium repo confidence | Verify reaction strip opens without sending reaction. |
| `ringcentral.video.toolbar.raise-hand` | UIA `Raise hand`, alternate `onconf.reactions.REMOVE_RAISE_HAND` | toggle | Medium repo confidence | Verify state toggle and hand lowering. |
| `ringcentral.video.toolbar.more` | UIA `More`, occurrence 3 | Escape | Low repo confidence | Cycle 003 saw overflow `More` at `(1181,762,1256,834)` as the third visible `More`; verify participant/layout variants. |
| `ringcentral.video.more.recording` | explain-only | none | Explain only | Add locator only with confirmation workflow. |
| `ringcentral.video.more.notes` | UIA `More` occurrence 3 -> `onconf.controls.NOTES`, alternate `Notes` | sidePanel | Low repo confidence | Resolve direct Notes vs More Notes variants. |
| `ringcentral.video.more.background` | UIA `More` occurrence 3 -> `Background` | settings | Low repo confidence | Verify opens Background settings and close path. |
| `ringcentral.video.more.settings` | UIA `More` occurrence 3 -> `Settings` | settings | Low repo confidence | Verify last-opened Settings panel behavior. |
| `ringcentral.video.toolbar.leave` | explain-only | none | Explain only | Keep non-executable until confirmation workflow exists. |

## Locator Risks

- Coordinates assume stable window geometry and DPI.
- `More` occurrence matching assumes toolbar order and visibility.
- Cycle 003 observed empty-room toolbar order but not participant-heavy, narrow, fullscreen, or localized variants.
- Modal cleanup uses blocker clearing and may depend on dialog shape.
- Side-panel cleanup uses a hard-coded close point in runtime cleanup.
- Settings cleanup assumes close button or Escape works across tabs.
- English UIA labels are assumed; localized RingCentral UI is not supported yet.

## Next Locator Work

1. Capture a dated UIA snapshot for each executable entrypoint.
2. Replace coordinate routes with UIA labels when reliable.
3. Split Notes variants into separate applicability rules or observation records.
4. Record window bounds and DPI next to every coordinate fallback.
5. Add screenshot references or sanitized control tree fixtures before expanding automation.
