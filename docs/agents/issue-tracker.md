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
