# Getting Started for Fellows

This repository is a worked example, not an empty template. Read the project
[README](README.md), the [September plan](docs/project/september-baseline.md), and the relevant
[decision records](docs/adr) before changing an interface or workflow.

## 1. Create the frozen environment

Install [uv](https://docs.astral.sh/uv/), clone the repository, and run:

```bash
uv sync --frozen --all-groups
```

The project targets Python 3.11. `pyproject.toml` declares dependencies, `uv.lock` freezes the
environment, and `requirements.txt` is a generated Colab bridge.

## 2. Validate inputs before analysis

```bash
uv run fall-ai-studio validate-source
```

The command checks the English source hash, header contract, 2,022 rows, 1,267 Card Records, and
the 60-card Reference Deck. Never silently replace the Authoritative Source with the similarly
named alternate export.

## 3. Run the fast PR checks

```bash
uv run ruff format --check .
uv run ruff check .
uv run pytest
```

Tests exercise the Catalog, Battle, and Evidence interfaces. They use recorded observations and an
in-memory Battle adapter, so pull requests stay fast and do not mislabel a mocked match as CABT
acceptance evidence.

## 4. Run a local simulator smoke test

```bash
uv run fall-ai-studio smoke-match --matches 2
```

Use local matches to develop and diagnose. Do not commit their output as an approved bundle. Only
the manually dispatched **September milestone acceptance** workflow can produce milestone approval
evidence.

## 5. Work from an Issue

Every work item uses the repository Issue template and includes:

- an outcome and context;
- explicit in-scope and out-of-scope boundaries;
- named Artifacts and Bundle contribution;
- observable acceptance criteria and verification commands;
- dependency links; and
- fictional ownership/stakeholder context.

Create a short-lived branch from current `main`, open a linked pull request, include verification
evidence, and merge with a merge commit after required checks and conversations are complete.

## Repository map

| Path | Purpose |
| --- | --- |
| `src/fall_ai_studio/` | Reusable Catalog, Battle, Evidence, and CLI code |
| `tests/` | Public-interface and data-contract tests |
| `config/` | Reviewed Reference Deck configuration |
| `notebooks/` | Thin narrative exploration using the Catalog |
| `artifacts/` | Approved, versioned Artifact Bundles only |
| `.github/workflows/` | Fast PR checks and real CABT milestone workflows |
| `docs/adr/` | Hard-to-reverse or surprising project decisions |
| `docs/project/` | Milestone and Issue source documents |

Fictional Pokémon participants are teaching devices. Do not create fake accounts, assign real
GitHub users to fictional work, or require fictional approvals.
