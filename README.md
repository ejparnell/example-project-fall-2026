# Pokémon TCG AI Battle Challenge — Fall 2026 Example

This repository is an executable, fictional example of a Fall AI Studio Challenge Project. It
demonstrates how code, Issues, pull requests, decisions, Workflow Runs, and Artifact Bundles fit
together around a small but real CABT baseline.

Ash Ketchum, Misty Williams, Brock Harrison, Erika Otsuka, Gary Oak, Professor Oak, Professor Elm,
and Professor Juniper are fictional narrative participants. They are not GitHub accounts,
assignees, approvers, or real program staff.

## September outcome

The **September Baseline** milestone establishes a reproducible comparison point:

- the supplied English card export is frozen by path and SHA-256;
- one Card Record is built per simulator Card ID without hiding repeated action rows;
- the official CABT 60-card sample deck is held constant;
- a deterministic rule-based Baseline Agent plays a first-legal Integration Control;
- 20 real CABT matches are balanced across both player positions; and
- a successful GitHub Actions run produces a complete, independently verifiable Artifact Bundle.

September is an integration baseline, not a competitive benchmark. It has no minimum win-rate
gate and makes no seeded-repeatability claim.

## Architecture

Reusable logic lives behind three public module seams:

| Module | Responsibility | Public evidence |
| --- | --- | --- |
| [Catalog](src/fall_ai_studio/catalog.py) | Normalize and validate the Authoritative Source; aggregate Card Actions; validate the Reference Deck | Source Receipt and data-contract tests |
| [Battle](src/fall_ai_studio/battle.py) | Apply the Baseline Policy and execute a balanced Evaluation Plan through CABT or an in-memory adapter | Match records, position-aware summary, representative replay |
| [Evidence](src/fall_ai_studio/evidence.py) | Assemble manifests and Run Receipts; recompute Bundle Integrity | Complete Artifact Bundle or explicit integrity errors |

The [CLI](src/fall_ai_studio/cli.py), workflows, and
[exploration notebook](notebooks/01_card_catalog_exploration.ipynb) are thin callers of those
interfaces. Acceptance-critical logic does not live only in a notebook.

## Quick start

Install [uv](https://docs.astral.sh/uv/), then use the frozen Python 3.11 environment:

```bash
uv sync --frozen --all-groups
uv run fall-ai-studio validate-source
uv run ruff format --check .
uv run ruff check .
uv run pytest
```

Run two development matches through the real simulator:

```bash
uv run fall-ai-studio smoke-match --matches 2
```

This smoke command proves local integration only. It cannot approve a milestone bundle. The
canonical 20-match acceptance and independent-verification runs are manually dispatched GitHub
Actions workflows.

For Colab, `requirements.txt` is generated from `uv.lock`; it is not a second hand-maintained
dependency source.

## Baseline Policy

During the main action selection, the Baseline Agent uses this stable priority:

```text
EVOLVE → ATTACH → ABILITY → PLAY → ATTACK → END
```

It avoids voluntary `RETREAT` and `DISCARD`, selects stable first options for setup and follow-up
choices, answers yes to initiated effects, and forces `ATTACK` or `END` after eight non-terminal
main actions. It does not inspect card text, optimize damage, tune the deck, or model the opponent.

The Integration Control selects the first legal option. It exists to prove CABT integration and is
not presented as a strategy-bearing baseline.

## Evidence and approval

An Artifact Bundle is a complete package from one successful task or related group of tasks. It
contains the files, a machine-readable Artifact Manifest, interpretive evidence, and checks proving
the package is complete and usable by the next step. Partial and failed work is not an approved
bundle.

The September workflow produces:

- the Reference Deck and Evaluation Plan;
- a Run Receipt tied to the source hash, code revision, dependency versions, and workflow URL;
- 20 machine-readable match records and a position-aware summary;
- one representative replay;
- interpretation and limitations;
- a manifest of file hashes and relationships; and
- an integrity report that can be recomputed rather than trusted.

See [the Artifact Bundle handoff](artifacts/README.md) and the
[September delivery plan](docs/project/september-baseline.md).

## Project workflow

- `main` is the only durable integration branch.
- Work begins on short-lived Issue Branches created from current `main`.
- Pull requests link an Issue, show verification evidence, resolve conversations, and merge with a
  merge commit.
- Fast PR checks run formatting, lint, public-interface tests, the data contract, and committed
  bundle integrity. They do not run CABT.
- Accepted monthly outcomes use annotated tags and GitHub Releases, not durable month branches.
- This solo-owned example requires zero fictional approvals. A live multi-person team should
  require at least one real collaborator's approval.

The complete decision record is in [docs/adr](docs/adr), and the project vocabulary is in
[CONTEXT.md](CONTEXT.md).

## Fictional team narrative

| Fictional participant | Example focus |
| --- | --- |
| Ash Ketchum | Evaluation runs and Artifact Bundle assembly |
| Misty Williams | Authoritative Source and Card Records |
| Brock Harrison | Baseline Agent and simulator integration |
| Erika Otsuka | Reproducible environment and automated checks |
| Gary Oak | Independent verification and milestone handoff |

Fictional ownership appears in Issue bodies and Project fields. Real GitHub Assignees remain empty.

## Data and rights

The Authoritative Source is
`data/pokemon-tcg-ai-battle-challenge-strategy/EN Card Data.csv`, SHA-256
`507d8d670c9c3c8d58f400d42eed09270b6b01354332770081bdb455d53b8c84`. The file remains unchanged;
the Catalog normalizes its `Previos stage` header at load time. See [the data guide](data/README.md).

This repository does not grant a blanket open-source license. It combines original teaching code
with third-party Pokémon challenge data and reference materials whose relicensing rights have not
been established. Any later code-license decision requires real rights-holder or Challenge Advisor
confirmation; third-party materials are not relicensed here.

## Fall roadmap

| Month | Planned milestone outcome | Outcome |
| --- | --- | --- |
| September | September Baseline | Executable, reproducible baseline and approved Artifact Bundle |
| October | October Analysis | Evidence-led matchup and failure analysis |
| November | November Refinement | Strategy comparison and reproducibility refinement |
| December | December Portfolio | Final narrative, presentation, and portfolio handoff |

Only the active month's native milestone and Issues are created. Later rows remain roadmap plans
until their month becomes active. Weekly sequencing uses the Project's `Target Cycle` iteration
field rather than week-level milestones.
