# Approved Artifact Bundles

Only complete, verified bundles from successful GitHub Actions Milestone Acceptance Runs belong
here. Exploratory, local, failed, and bulky run outputs stay in ignored `output/` or `.artifacts/`
directories.

The September process is:

1. Dispatch **September milestone acceptance** for a protected-`main` commit.
2. Download the `september-baseline-v1` workflow artifact, start with its `README.md` overview, and
   inspect the linked evidence and Run Receipt.
3. Commit the unchanged bundle directory at `artifacts/september-baseline-v1/` through a linked
   pull request.
4. Dispatch **September independent verification** from the new protected-`main` commit.
5. After verification succeeds, create an annotated tag and GitHub Release and attach the exact
   archive produced by the acceptance run.

The directory is intentionally empty until the canonical workflow has succeeded. Local output must
not be presented as an approved Artifact Bundle.

Every approved bundle starts with its own `README.md`. That README is a report of the work captured
by the bundle—not merely a file list. It summarizes what was completed, the important findings, how
data conditions or other findings were handled, the resulting evidence, limitations, and how to
verify the bundle. For EDA work, it reports the observed data shape, quality findings, transformations
or non-transformations, anomaly handling, and downstream implications.
