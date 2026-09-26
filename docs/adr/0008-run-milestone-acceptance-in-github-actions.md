# Run milestone acceptance in GitHub Actions

The canonical Milestone Acceptance Run will be a manually dispatched GitHub Actions workflow on Ubuntu using Python 3.11 and the frozen `uv.lock` environment. It records the selected source commit and match count, uploads the Run Receipt, logs, match evidence, summary, and replay, and supplies a durable workflow URL for the Artifact Manifest; local, Colab, and Kaggle executions remain useful for development but cannot approve a milestone bundle.
