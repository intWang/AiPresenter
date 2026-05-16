# Cycle 115 Risk Scan: Skill/Experience Crystallization

Date: 2026-05-16
Scope: documentation-only risk scan for a candidate maintenance cycle. This handoff does not edit production code, package YAML, tests, profiles, coverage, git history, Codex home skills, or global user configuration.

## Verdict

Conditional go for a repo-local planning and documentation pass that distills AiPresenter maintenance experience into guardrails, checklists, and reusable review notes.

No-go for creating, installing, testing, or publishing a real Codex skill in this cycle. Also no-go for any change that generalizes AiPresenter-specific rules into global Codex behavior, treats old runbook notes as current truth without verification, implies live RingCentral acceptance evidence, modifies files outside this repository, or stages `.coverage`.

The safest shape is:

- Produce repo-local documentation only, preferably under `docs/agent-handoffs/` or a separately approved docs path.
- Describe lessons as AiPresenter maintenance guidance, not as a universal Codex skill.
- Keep all RingCentral claims explicitly tied to dated evidence already present in the repo, and label anything else as a recommendation or hypothesis.
- Leave `C:\Users\rcadmin\.codex\` and other user/global configuration untouched.
- Run `git status --short` before handoff and keep `.coverage` unstaged.

## Primary Risks

| Severity | Risk | Failure mode | Impact | Guardrail |
| --- | --- | --- | --- | --- |
| P0 | Untested real Codex skill | The cycle creates or installs a live skill that changes Codex behavior without a test plan, rollback path, or isolated validation. | Future maintenance sessions can inherit unreviewed instructions, causing broad behavior drift outside the intended AiPresenter scope. | Do not create or modify `.codex/skills`, global plugins, or Codex home files. Keep this cycle advisory and repo-local unless a later implementation cycle has explicit approval and verification criteria. |
| P0 | Global/user home modification | Work writes to `C:\Users\rcadmin\.codex\`, user profiles, shell startup files, or shared Codex configuration. | The cycle violates the requested boundary and can affect unrelated repositories or future sessions. | Treat all paths outside `C:\Users\rcadmin\Documents\Repos\AiPresenter` as read-only context. If a future skill is proposed, draft its content inside repo docs first. |
| P0 | Over-generalizing project rules | AiPresenter-specific safety, RingCentral, package, and handoff conventions become framed as universal agent rules. | Other projects may receive inappropriate constraints, while AiPresenter maintainers may lose the local rationale behind the rules. | Use project-scoped language: "for AiPresenter maintenance" and "for RingCentral package evidence." Separate transferable patterns from local rules. |
| P0 | Implied live RingCentral evidence | The crystallized guidance says a behavior is live-accepted, observed in RingCentral, or production-proven without dated live-run artifacts. | Reviewers may trust stale or offline evidence as current UI truth, leading to unsafe package or runtime changes. | Require exact evidence labels: unit test, offline package review, runbook note, live RingCentral run, date, and artifact path. Do not promote undocumented observations into acceptance evidence. |
| P1 | Stale runbook docs | Existing handoffs, runbooks, or maintenance notes are summarized as current operating procedure even when the app or package schema has moved on. | Maintainers can cargo-cult obsolete instructions, miss newer safety checks, or reintroduce old limitations. | Cross-reference any runbook-derived rule with current source/tests in a later approved implementation cycle. In this advisory scan, mark stale-doc risk plainly instead of resolving it. |
| P1 | Skill wording becomes too directive | A proposed skill uses absolute language that overrides maintainer judgment or conflicts with explicit cycle instructions. | Future agents may prioritize the skill over user constraints or local evidence review. | If a future skill is drafted, make it conditional, scoped, and subordinate to explicit user instructions and repo policies. Include no claims of authority over unrelated repositories. |
| P1 | Privacy and evidence leakage | Experience notes include raw prompts, meeting identifiers, invite links, participant names, transcripts, chat text, or generated answers copied from local runs. | Documentation becomes a retention surface for sensitive RingCentral or user data. | Use abstract examples or sanitized fixtures only. Keep evidence references to file paths, commands, and summary outcomes unless the source is already an approved fixture. |
| P1 | Documentation churn masks review surface | The cycle edits broad docs, runbooks, skills, or generated files while presenting itself as a narrow crystallization step. | Reviewers cannot tell which guidance is new, verified, stale, or speculative. | Create exactly one handoff file for this scan. Any later docs consolidation should be a separate cycle with a bounded file list. |
| P2 | Unverified maintenance folklore | Lessons learned are phrased as facts because they "usually worked" in previous cycles. | Local practice can harden into process debt and block better fixes. | Label recommendations by confidence and evidence source. Keep unresolved items in a checklist rather than turning them into rules. |
| P2 | Coverage artifact staging | Focused inspection or accidental test runs leave `.coverage` modified and it is staged with the handoff. | The diff violates cycle constraints and hides a generated artifact inside a docs-only change. | Before staging or handoff, run `git status --short`; leave `.coverage` unstaged and do not delete or reset it unless explicitly requested. |

## Guardrails

Proceed only if all of these remain true:

- Cycle 115 creates exactly one file: `docs/agent-handoffs/cycle-115-risk-scan.md`.
- No production code, package YAML, tests, profiles, coverage files, git history, Codex home skills, or user/global configuration are edited.
- The candidate work remains a risk scan and review aid, not an implementation of a real Codex skill.
- Any future skill proposal is drafted as repo-local text first and reviewed before installation or activation.
- AiPresenter-specific rules stay scoped to AiPresenter maintenance, RingCentral package review, and this repository's handoff practices.
- Runbook-derived guidance is marked as potentially stale unless it is verified against current source, tests, or dated live artifacts in a later approved cycle.
- Live RingCentral claims require dated artifacts and clear evidence type. Offline tests and handoff summaries are not described as live acceptance.
- No raw user prompts, meeting data, invite links, participant names, chat text, transcripts, or generated answer bodies are copied into guidance.
- `.coverage` remains unstaged.

## No-Go Triggers

Stop the cycle if any proposed action does one of these:

- Creates, installs, edits, or tests a real Codex skill under `C:\Users\rcadmin\.codex\` or any global plugin/skill location.
- Modifies files outside the AiPresenter repository.
- Edits production code, package YAML, tests, profiles, coverage artifacts, git history, or Codex home skills.
- Rewrites runbooks or other docs beyond this single risk-scan file.
- Presents stale handoff or runbook content as current fact without verification.
- Claims live RingCentral validation without a dated live-run artifact.
- Copies sensitive or user-specific RingCentral data into documentation.
- Uses absolute agent instructions that could override explicit future user requests.
- Stages `.coverage`.

## Review Checklist

Use this checklist before approving any later Cycle 115 implementation or crystallization work.

- [ ] Diff contains only the approved file(s) for that later cycle; this advisory scan itself remains a single-file docs change.
- [ ] No files under `C:\Users\rcadmin\.codex\` or other user/global configuration paths are changed.
- [ ] Any proposed skill content is repo-local draft text, not an installed or active skill.
- [ ] Guidance is explicitly scoped to AiPresenter maintenance and does not claim universal Codex behavior.
- [ ] Project-specific rules identify their source: current source, current tests, prior handoff, runbook, or dated live artifact.
- [ ] Stale or unverified runbook-derived items are labeled for review instead of promoted to requirements.
- [ ] Live RingCentral evidence is only claimed when the artifact path and date are present.
- [ ] Privacy-sensitive examples are sanitized and do not include raw prompts, meeting IDs, invite links, participant names, chats, transcripts, or generated answer bodies.
- [ ] The review separates guardrails from recommendations so maintainers know what is blocking versus advisory.
- [ ] `git status --short` is reviewed before staging; `.coverage` is not staged.

## Suggested Future Verification

For this advisory handoff, a markdown diff check and git status review are enough.

For any later cycle that drafts a repo-local skill or maintenance playbook, recommended checks are:

```powershell
git diff --check -- docs\agent-handoffs\cycle-115-risk-scan.md
git status --short
```

If a future cycle is explicitly authorized to create a real Codex skill, require a separate plan before implementation that covers install location, scope boundaries, test fixture inputs, rollback steps, privacy review, and proof that no global/user configuration is changed without direct approval.
