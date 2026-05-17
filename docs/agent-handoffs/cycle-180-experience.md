# Cycle 180 Experience Handoff

Date: 2026-05-17

## Lessons Learned

- Participants intent has two separate meanings: opening the Participants panel and disclosing participant identity, roles, host/moderator status, or private meeting state.
- Explicit panel language is the safe operable path: `participants panel`, `open participants panel`, `show participants panel`, `participants button`, and similar location/control-surface prompts may route to `ringcentral.video.toolbar.participants`.
- Broad `show participants` is privacy-adjacent. It should receive guidance about names, roles/private tabs, explicit user request, and verified visible context rather than opening the panel.
- Presenter-meta prefixes should not blur safety boundaries. `Please be brief and open participants panel` remains operable; `Please be brief and show participants` stays answer-only.
- No YAML alias was needed. The cycle's important distinction belongs in Q&A/privacy matching and route policy, not in broad participant aliases.
- `entrypoint_id` is still only identification. `can_operate` and interrupt creation remain the execution gates.
- Participant privacy tests need to assert both sides: safe panel prompts produce interrupts, while identity/role/host prompts produce no entrypoint, no operation, and no controller demo.

## Future Subagent Prompts

- Add localized participant privacy coverage without widening aliases. Start with English, Spanish, Japanese, and Chinese prompts for show participants, list participants, who is in the meeting, read participant names, show roles, and who is host/moderator.
- Audit participant-related Q&A for accidental `relatedEntrypointIds`. If any privacy Q&A references the Participants panel, prove `can_operate=False` and no interrupt is created.
- Add a regression matrix for mixed presenter-meta prompts: safe panel navigation should start or queue `question-answer-demo`; identity, role, and host disclosure should stay answer-only.
- Search for host/security-control phrasing near Participants, including mute, remove, admit, lock, unlock, and waiting-room/security terms. Keep them answer-only unless a future policy explicitly designs safe operation.
- Review diagnostics only if YAML aliases change. This cycle intentionally avoided adding a broad `show participants` alias.

## Next-Cycle Backlog

1. Add localized participant privacy sentinels before expanding any participant aliases.
2. Keep `show participants` and mixed-meta variants in the focused regression slice as answer-only privacy guidance.
3. Preserve explicit panel/button phrasing as the only operable participant navigation path.
4. Re-check controller idle/running behavior for safe panel prompts and unsafe disclosure prompts after any routing changes.
5. Document the participant boundary in durable RingCentralVideo knowledge if future cycles touch privacy, host controls, or participant aliases.
