# Use Python 3.11 and uv

The Example Project will target Python 3.11, declare dependencies and tool configuration in `pyproject.toml`, and commit `uv.lock` as the exact environment lock used locally and in CI. A generated `requirements.txt` will provide a familiar Colab installation path without becoming a second hand-maintained dependency source; this balances reproducible Workflow Runs with the access patterns Fellows are likely to use.
