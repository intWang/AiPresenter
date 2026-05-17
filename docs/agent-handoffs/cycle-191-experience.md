# Cycle 191 Experience Handoff

Date: 2026-05-17

## Lessons Learned

- Group draft commands are useful for checklist context, but operators often need a concrete
  entrypoint draft to get open steps and presenter notes.
- Detail views are the right place for extra commands; priority lists should stay optimized for
  scanning.
- Reusing the existing `acceptance_draft_command()` keeps example commands aligned with the
  canonical draft syntax.
- Blocked and mixed flow targets should stay conservative until a separate workflow requires
  finer-grained examples.

## Future Subagent Prompts

- Check whether the broad P1 target groups should gain suggested validation order in docs.
- Consider a controller-side affordance for copying the focused draft command once UI work
  resumes.
- Keep `.coverage` out of every commit.

## Next-Cycle Backlog

1. Add a suggested order for broad P1 manual target groups if operators need sequencing.
2. Continue language/tone expansion after validation workflow helpers stabilize.
3. Explore lightweight scan-performance observability.
