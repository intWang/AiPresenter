# Cycle 022 Review Handoff

Date: 2026-05-16
Role: review subagent
Scope: review only; this handoff is the only file created.

## Review Result

Blocked by one spec-compliance finding.

## Findings

### P1: Add coworkers `openSteps` changed despite package-content-only scope

- Evidence: `packages/ringcentral-video.yaml:127` now defines `ringcentral.video.main.add-coworkers` with `action: clickWindowControl`, `target: Add coworkers`, and `controlType: button`.
- The diff shows this route changed from the prior coordinate-based `clickWindowRelative` step to a UIA control step.
- The Cycle 022 spec explicitly limited package edits to `questionAliases`, `localizedQuestions`, `localizedAnswers`, and `relatedEntrypointIds`, and called out no `openSteps` changes.
- `tests/unit/test_material_packages.py:196` also adds coverage that enshrines this changed Add coworkers route shape, so the focused tests now pass while asserting behavior outside the requested slice.
- Safety impact appears bounded because Add coworkers remains non-operable through existing risk classification, but the route change still violates the package-content-only requirement.

## Non-Blocking Observations

- Chinese content in `packages/ringcentral-video.yaml` is real UTF-8. The PowerShell console renders some output as mojibake, but the diff and Python UTF-8 parsing show real Chinese strings.
- The localized answers are generally natural and preserve privacy boundaries for shared screen, invite links, chat/participants, audio/video readiness, network diagnostics, and recording consent.
- The implementation note about `邀请同事` is acceptable: Q&A matching runs before entrypoint alias matching, so the test uses `拉人入会` to prove the Add coworkers package alias path without colliding with the localized invite Q&A.
- No surprising short-alias collision showed up in the focused tests. The shortest aliases remain a residual risk area, especially `声音`, `共享`, `笔记`, and `录制`, but current covered behavior is reasonable.
- The current workspace has additional dirty files under `src/`, broader tests, README, and runbook paths. I did not review those changes for Cycle 022 and do not attribute them to this package-content implementation.

## Verification

- `.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py tests\unit\test_questions.py`
  - Result: `52 passed in 8.94s`
- `.\.venv\Scripts\python -m ruff check --no-cache tests\unit\test_material_packages.py tests\unit\test_questions.py`
  - Result: `All checks passed!`

## Direct Probe Notes

- `怎么邀请别人` resolved to `ringcentral.video.toolbar.invite`, `can_operate=False`.
- `我是第一个人怎么邀请同事入会` resolved to `ringcentral.video.toolbar.invite`, `can_operate=False`, with the localized invite answer.
- `怎么共享屏幕` resolved to `ringcentral.video.toolbar.share`, `can_operate=False`.
- `怎么录制会议` resolved to `ringcentral.video.more.recording`, `can_operate=False`.
- `怎么离开会议` resolved to `ringcentral.video.toolbar.leave`, `can_operate=False`.
- `邀请同事` resolved to the localized invite Q&A before alias matching.
- `拉人入会` resolved to `ringcentral.video.main.add-coworkers`, `can_operate=False`.

## Residual Risk

- The focused tests cover the requested localized Q&A and alias migration path, but they also include a new test for the Add coworkers `openSteps` change, which should be removed or adjusted when the route shape is restored.
- I did not run full pytest or mypy in this review because the user-requested minimum was the two focused commands above.
- Because other workspace files are dirty, integration should ensure Cycle 022 is isolated from unrelated runtime/schema/route-safety changes before merge.

## Recommendation

Do not merge Cycle 022 as-is. Restore `ringcentral.video.main.add-coworkers` `openSteps` and remove the test assertion that requires the changed route shape, then rerun the same focused pytest and ruff checks. After that, the Q&A localization and alias content look acceptable for this slice.
