# Issue tracker

This repository uses GitHub Issues in `ejparnell/example-project-fall-2026` as the canonical work
tracker. The native GitHub Project organizes those Issues; it does not replace them with draft
cards.

## Read

```bash
gh issue list --repo ejparnell/example-project-fall-2026
gh issue view NUMBER --repo ejparnell/example-project-fall-2026
```

## Write

Publishing or changing Issues requires an authenticated `gh` session with access to the repository.
Use the body contract in `.github/ISSUE_TEMPLATE/work-item.yml` and the prepared September source in
`docs/project/september-baseline.md`. Leave GitHub Assignees empty for fictional participants.

Do not fabricate timestamps, approvals, people, dependency state, workflow evidence, or completion.
Record native blocking links where available and retain the same edges in each Issue's dependency
section.

## Work and close

1. Select an unblocked Issue, assign the real contributor, and leave a short pickup comment naming
   the branch and intended verification. Do not assign fictional narrative participants.
2. Create a short-lived `issue/NUMBER-short-name` branch from current `main`.
3. Open one focused pull request with `Closes #NUMBER`, a passing check run, and a complete Issue
   Work Bundle under `artifacts/issue-N-short-name/`.
4. Keep the Issue open until the pull request is merged. Merge with a merge commit after required
   checks pass, then delete the short-lived branch.
5. After GitHub closes the Issue, add a brief closing comment summarizing the delivered outcome,
   linked pull request, bundle README, verification evidence, limitations, and newly unblocked work.

The closing comment is the concise tracker handoff. The bundle README is the detailed report and
must carry the exact supporting files rather than relying on the comment or pull request history.
