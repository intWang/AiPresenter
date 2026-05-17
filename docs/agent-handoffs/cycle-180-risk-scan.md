# Cycle 180 Risk Scan

Date: 2026-05-17

## Findings

Opening the Participants panel is an operable location/control request. Reading participant names, roles, host/moderator status, chat content, or private tabs is answer-only. Muting others, removing people, locking/unlocking, or changing security settings is answer-only.

`entrypoint_id` alone is not permission; `can_operate` and `create_question_interrupt_step(...)` remain the execution gates.

## Must Not Break

- `participants`, `participants panel`, `open participants panel`, `panel de participantes`, and explicit panel-location prompts may route to `ringcentral.video.toolbar.participants`, `can_operate=True`, and create/start/queue a question demo.
- Ambiguous `show participants` must stay text-only unless a future cycle deliberately reclassifies it with privacy tests.
- `Who is in the meeting?`, `List participants`, `Read participant names`, `Show participant roles`, `Who is host or moderator?`, and mixed-meta variants must stay `entrypoint_id=None`, `can_operate=False`, no interrupt.
- `Mute all participants`, `Remove a participant`, `Lock the meeting`, `Unlock the meeting`, and security-setting prompts must stay answer-only with no Participants-panel interrupt.
- Do not add `relatedEntrypointIds` to participant identity or host-control privacy Q&A unless the route remains non-operable.
- Preserve Q&A-first routing before presenter-meta and entrypoint matching.
- Preserve `questionPolicy: answerOnly`, `_can_operate(...)`, and `create_question_interrupt_step(...)` as independent gates.
- Live/manual validation must not record participant names, roles, chat text, invite links, emails, or meeting IDs.

## Risk Matrix

| Risk | Likelihood | Impact | Current Signal | Mitigation |
| --- | --- | --- | --- | --- |
| Broad participant alias makes identity prompts operable | Medium | High | Participants is safe to open, but identity wording is nearby | Keep exact panel aliases; test name/role/host prompts against no entrypoint and no interrupt |
| `relatedEntrypointIds` added to privacy Q&A | Low/Medium | High | Q&A response uses first related entrypoint if present | Keep participant identity and host-control Q&A unlinked or prove `can_operate=False` |
| Presenter-meta prefix changes route | Medium | High | Recent cycles touched mixed-meta routing | Keep mixed-meta tests for safe panel opening and unsafe list/read/host prompts |
| Localized alias ambiguity | Medium | Medium/High | Chinese `谁在会议里` currently routes to panel while English `Who is in the meeting?` routes privacy Q&A | Add localized identity prompts before expanding aliases; document intentional panel-only meanings |
| Host/security controls become executable | Medium | High | `_RISKY_ENTRYPOINT_WORDS` covers lock/mute but future remove/admit routes may need new guards | Treat new host/security entrypoints as answer-only until role, consent, locator, and cleanup policy exist |
| Live evidence leaks private values | Medium | High | Docs require sanitized UIA and no screenshots unless needed | Use disposable meetings; record only counts/control labels; redact names/roles/messages |

## Recommended Verification

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -B -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests\unit\test_questions.py tests\unit\test_controller_session.py tests\unit\test_controller.py -k "participant or participants or host_controls or safe_mixed_meta or sensitive_mixed_meta"
```

Run diagnostics if YAML aliases or Q&A prompts change.
