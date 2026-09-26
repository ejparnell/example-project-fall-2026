# Artifact Bundles

This directory holds two deliberately different bundle types. Both are complete, integrity-checked
handoffs with a report-style `README.md`; neither is a loose collection of output files.

## Issue Work Bundles

Each completed Issue commits one `issue-N-short-name/` directory through its linked pull request.
That bundle contains:

- a `README.md` report of the outcome, work completed, important decisions or findings,
  verification, and limitations;
- `files/`, preserving the exact repository-relative paths of the source, configuration,
  automation, documentation, and tests needed to review the Issue's result;
- `verification.json`, recording the source commit, environment, commands, and results; and
- `manifest.json`, binding the Issue, source commit, inventory, byte sizes, and SHA-256 hashes.

Run `uv run fall-ai-studio verify-bundle artifacts/issue-N-short-name` to recompute integrity. The
bundle is an issue handoff and audit record; normal Git history remains the integration mechanism.

## Approved milestone bundles

Only complete, verified bundles from successful GitHub Actions Milestone Acceptance Runs belong
in a milestone bundle such as `september-baseline-v1/`. Exploratory, local, failed, and bulky run
outputs stay in ignored `output/` or `.artifacts/` directories.

The September process is:

1. Dispatch **September milestone acceptance** for a protected-`main` commit.
2. Download the `september-baseline-v1` workflow artifact, start with its `README.md` overview, and
   inspect the linked evidence and Run Receipt.
3. Commit the unchanged bundle directory at `artifacts/september-baseline-v1/` through a linked
   pull request.
4. Dispatch **September independent verification** from the new protected-`main` commit.
5. After verification succeeds, create an annotated tag and GitHub Release and attach the exact
   archive produced by the acceptance run.

The milestone bundle is intentionally absent until the canonical workflow has succeeded. An Issue
Work Bundle records completion of its bounded Issue; it must not be presented as approval of a
monthly outcome or simulator evaluation.

Every approved bundle starts with its own `README.md`. That README is a report of the work captured
by the bundle—not merely a file list. It summarizes what was completed, the important findings, how
data conditions or other findings were handled, the resulting evidence, limitations, and how to
verify the bundle. For EDA work, it reports the observed data shape, quality findings, transformations
or non-transformations, anomaly handling, and downstream implications.
