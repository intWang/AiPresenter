# Cycle 116 Risk Scan: Language And Tone Expansion

Date: 2026-05-16
Scope: documentation-only risk scan for a small language/tone expansion slice. This handoff does not edit production code, package YAML, tests, profiles, coverage, git history, Codex home files, or global user configuration.

## Verdict

Conditional go for a narrow expansion only if Spanish runtime support, tone aliases, voice/provider compatibility, localization reporting, and RingCentral evidence language stay explicitly separated.

No-go for presenting the current Spanish seed as demo-ready. Current source/tests treat Spanish package content as partial coverage: `localization-report --language es` is expected to report `0/51` demo steps, `1/12` Q&A questions, `1/12` Q&A answers, and `questionAliases.es` on `1/27` entrypoints with `3` aliases. Current runtime voice validation also rejects `--language es`. Those are compatible facts only if the next implementation intentionally changes runtime support without redefining partial localization as complete.

The safest shape is:

- Add Spanish runtime support only behind an explicit compatibility matrix, probably OpenAI speech/narration first unless local Spanish SAPI or Piper assets are deliberately added and tested.
- Keep Spanish localization report semantics report-only until Spanish demo narration and Q&A are complete.
- Treat tone aliases as style-only labels. They must not change routing, `can_operate`, `questionPolicy`, interrupt creation, or RingCentral safety policy.
- Keep RingCentral claims evidence-scoped: unit tests, package diagnostics, localization report, manual runbook, and live acceptance are different evidence levels.
- Keep `.coverage` unstaged. It was already modified when this scan began.

## Primary Risks

| Severity | Risk | Failure mode | Impact | Guardrail |
| --- | --- | --- | --- | --- |
| P0 | Spanish runtime enabled without speech route | `PresenterVoiceSettings(language="es")` becomes accepted, but `validate_profile_voice`, `resolve_speech_provider_name`, `voices`, `doctor`, controller readiness, or asset checks still assume only English/Chinese/Japanese local routes. | Demos can launch with a voice profile that cannot actually produce Spanish output, or the controller reports a route as safe when assets are missing. | Define Spanish compatibility in code and tests before enabling it: supported provider(s), unsupported profile messages, selected voice exit codes, and asset diagnostics. |
| P0 | Partial Spanish called complete | The existing Spanish seed is treated as ready because one Q&A and one alias group exist. | Users may expect a Spanish RingCentral tour while scripted narration and most safety Q&A fall back to English. | `localization-report --language es --require-complete` must fail until Spanish reaches complete required coverage. Doctor `--require-localization` must fail for Spanish while coverage is partial. |
| P0 | Tone alias changes policy | New aliases such as privacy/safety/compliance-like terms influence route matching, operation permission, or safety Q&A selection. | A style choice could make sensitive RingCentral controls operable, or hide a safety regression behind a tone selection. | Keep tone normalization inside voice rendering/labels. Run route-parity tests across canonical tones and new aliases. |
| P0 | Spanish aliases overmatch unsafe actions | Spanish control aliases include action/content terms such as recording, reading chat, copying links, starting notes, sharing screen, leaving, inviting, or changing meeting state. | A Spanish prompt can route to an executable or sensitive RingCentral surface without the existing safety Q&A protections. | Add aliases only for safe location/control discovery, and add Spanish safety Q&A or runtime guards before adding action/content wording. |
| P0 | Evidence overclaim | Handoff, README, or runtime text says Spanish is accepted, live-tested, RingCentral-verified, or provider-compatible based only on package data or unit tests. | Reviewers and demo operators can mistake offline coverage for current live RingCentral behavior. | Use exact evidence labels. `Repo-tested` means local tests/diagnostics only; `Accepted` requires dated live/manual acceptance for the current route/build. |
| P1 | Localization report contract drift | `build_localization_status` starts rejecting languages outside `PresenterLanguage`, or alias coverage starts counting toward required completeness. | Partial languages can no longer be inspected safely, or alias-only seeds appear complete. | Preserve arbitrary `--language` reporting and keep required completeness limited to demo narration plus Q&A questions/answers unless a separate design changes the contract. |
| P1 | CLI/controller catalog mismatch | Spanish is added to one surface but not the others: `voices`, `demo`, `doctor`, controller language menu, labels, dry-run output, or logs disagree. | Operators receive conflicting support signals and may launch with the wrong voice route. | Update public choices, aliases, labels, selected voice output, controller labels, and normalized logging together. |
| P1 | Local provider asset assumptions | Spanish is routed through generic `windows-sapi`, `windows-sapi-en`, existing Piper English assets, or Chinese SAPI fallback. | Audio output can be wrong-language or fail late at demo time. | Require OpenAI for Spanish unless adding a named `windows-sapi-es` or Spanish Piper model path with asset checks and failure messages. |
| P1 | Localized fallback wording gap | No-match answers, generated prefixes, or package fallback text remain English while the runtime says "Speak in Spanish." | User-facing output becomes mixed-language and looks less reliable than the support matrix suggests. | Add Spanish no-match text and decide whether fallback package text is translated, left English with explicit partial-localization status, or blocked by localization readiness checks. |
| P1 | RingCentral safety Q&A gaps | Spanish privacy prompts for meeting info, chat, participants, invite links, recordings, notes/transcripts, reactions, raise hand, share, or leave are not covered. | Spanish users can bypass localized safety answers through broad alias/token matching. | Add focused Spanish negative/answer-only tests before adding Spanish aliases beyond the background privacy seed. |
| P2 | Count churn without review | Adding Spanish aliases or Q&A changes doctor totals but tests/docs still expect old counts. | Diagnostics become noisy or stale, making real alias collisions harder to notice. | Update expected counts deliberately and explain whether the change is package data, runtime language support, or both. |
| P2 | Coverage artifact staging | Focused tests update `.coverage`, and the artifact is staged with this docs-only handoff or a later implementation. | The diff violates cycle boundaries and hides a generated artifact. | Run `git status --short` before staging. Leave `.coverage` unstaged; do not reset or delete it unless explicitly requested. |

## Guardrails

Proceed only if all of these remain true:

- This advisory scan creates exactly one file: `docs/agent-handoffs/cycle-116-risk-scan.md`.
- No production code, tests, profiles, packages, `.coverage`, Codex home files, git history, or user/global configuration are edited by this scan.
- Spanish package localization and Spanish runtime voice support are tracked as separate states.
- A partial Spanish package seed remains incomplete in localization reports and readiness checks.
- Any Spanish runtime support has explicit provider rules and user-facing unsupported-profile errors.
- New tone aliases normalize to existing canonical tones or a clearly tested new canonical tone, and tone remains style-only.
- RingCentral safety routing remains Q&A-first, answer-only where configured, and non-operable for sensitive/destructive surfaces.
- Documentation avoids live RingCentral acceptance, locale, provider, or voice-asset claims unless a dated evidence artifact is named.
- `.coverage` remains unstaged.

## No-Go Triggers

Stop the implementation if any proposed change does one of these:

- Allows `--language es` while `voices`, `doctor`, controller readiness, or asset checks cannot explain which speech route is supported.
- Routes Spanish through English/Chinese local voice assets without an explicit test-backed fallback policy.
- Makes `localization-report --package ringcentral-video --language es --require-complete` pass before required Spanish demo narration and Q&A are complete.
- Restricts `localization-report --language` to only runtime-supported presenter languages and loses report-only inspection for partial languages.
- Uses alias coverage as required localization completeness.
- Adds Spanish aliases for sensitive actions or private content before adding safety Q&A/route tests.
- Lets any tone alias change `entrypoint_id`, `can_operate`, `questionPolicy`, or interrupt creation.
- Claims live RingCentral validation, Spanish locale acceptance, or provider compatibility from unit tests, docs, or package YAML alone.
- Edits production code, tests, profiles, packages, `.coverage`, Codex home files, or git history as part of this documentation-only scan.
- Stages `.coverage`.

## Verification Checklist

For this documentation-only handoff:

- [ ] Diff contains only `docs/agent-handoffs/cycle-116-risk-scan.md`.
- [ ] `git diff --check -- docs\agent-handoffs\cycle-116-risk-scan.md` passes.
- [ ] `git status --short` is reviewed; `.coverage` is still unstaged and not modified by this scan.

For a later implementation cycle:

- [ ] Add/update voice tests for Spanish aliases, labels, unsupported-language behavior changing intentionally, render instruction text, no-match fallback, and provider validation.
- [ ] Add/update voice asset tests for the chosen Spanish route. If Spanish is OpenAI-only, local SAPI/Piper/fake profiles should report unsupported unless explicitly allowed.
- [ ] Add/update CLI tests for `voices`, targeted `voices --profile ... --language es`, `demo --language es --dry-run`, `doctor --language es`, and controller labels.
- [ ] Add/update localization tests proving Spanish remains partial until complete: `0/51` demo steps, `1/12` Q&A questions, `1/12` Q&A answers, `1/27` entrypoints, `3` aliases unless package YAML intentionally changes.
- [ ] Add Spanish question-routing tests for the privacy/background seed, plus negative tests for recording, notes/transcript, meeting info, chat, participants, invite links, share, leave/end, reactions, and raise hand before adding aliases in those areas.
- [ ] Run tone route-parity tests across canonical tones and every new alias; assert `entrypoint_id`, `can_operate`, and interrupt behavior stay unchanged.
- [ ] Run doctor/package diagnostics and deliberately update alias/Q&A counts only when package data changes.
- [ ] Check README/runbook/handoff wording for evidence-level precision: no "accepted" or "live verified" claim without a dated live/manual artifact.
- [ ] Run `git diff --check` and `git status --short`; confirm `.coverage` is not staged.

Suggested focused commands for the implementation cycle:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_voice.py tests\unit\test_voice_assets.py tests\unit\test_cli.py tests\unit\test_diagnostics.py tests\unit\test_material_packages.py
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py::test_ringcentral_sensitive_prompt_routing_is_tone_invariant
.\.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language es
.\.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language es --require-complete
.\.venv\Scripts\ai-presenter voices
git diff --check
git status --short
```

Expect the Spanish `--require-complete` command to fail until Spanish required coverage is intentionally completed. If it passes before then, treat that as a release blocker.

## Coverage Staging Warning

`.coverage` was already modified at the start of this scan. Do not stage, delete, overwrite, or reset it from this subagent. If tests in a later cycle update it again, keep it unstaged unless the user explicitly assigns coverage artifact maintenance.
