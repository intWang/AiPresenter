# RingCentral Host Participants Q&A Design

## Problem

RingCentral Video package knowledge includes Participants panel details and privacy guidance, but a user asking about host controls or participant management receives a generic Participants answer. The Presenter needs a concise answer that maps host-control intent to the safe panel entrypoint and names the boundary around sensitive actions.

## Design

Add one package Q&A item:

- Question: "Where are host controls for participants?"
- Related entrypoint: none. This is intentionally answer-only so host-management intent cannot trigger automatic operation.
- English and Chinese answers explain that Participants is the place to inspect attendee controls, search, invite, and review available host controls.
- Both answers state that identifying names/roles or changing meeting state, such as muting, removing, locking, or similar host actions, requires explicit request and verified visible context.

Keep generic Participants questions routing to the Participants entrypoint. To support that, answer-only Q&A fragment matching should ignore overly broad one-word fragments like `participants` when those fragments already map to an entrypoint. Q&A items with `relatedEntrypointIds` must keep their single-word safety matches, such as `recording`.

## Testing

Question tests will assert English and Chinese prompts return the new Q&A guidance. Localization and doctor readiness tests will move from 8/8 to 9/9 Q&A coverage.
