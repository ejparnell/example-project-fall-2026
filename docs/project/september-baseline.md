# September Baseline delivery plan

This file is the publishable source for the native GitHub milestone, labels, Project fields, and
five September Issues. GitHub Issues become the canonical execution records after publication; this
document remains the reusable teaching reference.

## Milestone

**Title:** September Baseline  
**Due:** September 30, 2026  
**Description:** Establish a reproducible Python 3.11 project, freeze the Authoritative Source,
complete a real CABT round trip with the deterministic Baseline Agent, produce a verified 20-match
Artifact Bundle, and independently verify the milestone handoff.

Weekly sequencing uses four `Target Cycle` iterations, not extra milestones:

| Iteration | Dates |
| --- | --- |
| September — Week 1 | September 1–7, 2026 |
| September — Week 2 | September 8–14, 2026 |
| September — Week 3 | September 15–21, 2026 |
| September — Week 4 | September 22–28, 2026 |

These dates communicate intended sequence. GitHub timestamps and Project Status remain the honest
record of when work actually happens; do not backdate activity.

## Project fields

Use the built-in `Status` field with `Backlog`, `Ready`, `In Progress`, `In Review`, `Blocked`, and
`Done`. Add these custom fields:

| Field | Type | Values |
| --- | --- | --- |
| Target Cycle | Iteration | The four September iterations above; later months are added just in time |
| Fictional Work Owner | Single select | Ash Ketchum, Misty Williams, Brock Harrison, Erika Otsuka, Gary Oak |
| Effort | Single select | Small (S), Medium (M), Large (L) |

Leave real GitHub Assignees blank. Fictional participants have no accounts or approval authority.

## Labels

Every work Issue receives one `type:`, one `area:`, and one `priority:` label. Status belongs only in
the Project field.

| Label | Color | Meaning |
| --- | --- | --- |
| `type: setup` | `1D76DB` | Environment, automation, or repository setup |
| `type: implementation` | `0075CA` | Executable product or test behavior |
| `type: experiment` | `5319E7` | A recorded evaluation or comparison |
| `type: documentation` | `0E8A16` | Narrative or reference artifact |
| `type: review` | `6F42C1` | Verification, acceptance, or handoff |
| `area: data` | `0E8A16` | Source data and Card Records |
| `area: agent` | `D93F0B` | Policy, deck, or simulator integration |
| `area: evaluation` | `006B75` | Match execution and result interpretation |
| `area: reproducibility` | `0052CC` | Environments, provenance, checks, and manifests |
| `area: portfolio` | `BFDADC` | Portfolio-facing explanation or presentation |
| `priority: high` | `B60205` | Required for the active milestone |
| `priority: medium` | `FBCA04` | Important but not immediately blocking |
| `priority: low` | `C2E0C6` | Valuable polish that does not block acceptance |
| `needs-ca-feedback` | `D4C5F9` | Actual pending fictional stakeholder context only |

## Dependency chain

```text
Issue 1 ─┐
         ├─→ Issue 3 ─→ Issue 4 ─→ Issue 5
Issue 2 ─┘
```

## Issue 1 — Establish reproducible Python project and automated checks

**Project metadata:** Erika Otsuka · September — Week 1 · Ready · M  
**Labels:** `type: setup`, `area: reproducibility`, `priority: high`  
**Dependencies:** None

### Outcome

A contributor can create the exact Python 3.11 environment from a fresh checkout and receive fast,
portable feedback from the same formatting, lint, test, and repository-contract checks used on pull
requests.

### Context

Every later Artifact and Workflow Run depends on a known environment and a trustworthy integration
path. Establishing this first prevents notebooks and local machines from becoming hidden sources of
truth.

### In scope

- Canonical `pyproject.toml`, `.python-version`, and `uv.lock`.
- Generated `requirements.txt` for Colab consumers.
- Installable `src/` package and public CLI entry point.
- Fast GitHub Actions PR checks with no CABT match execution.
- Work Item and pull request templates.

### Out of scope

- Card-data semantics, Baseline Policy behavior, real CABT acceptance matches, and approved bundles.
- Notebook execution as a required PR gate.
- Coverage thresholds or production deployment.

### Artifacts and Bundle contribution

`pyproject.toml`, `uv.lock`, `requirements.txt`, `.python-version`, `.github/workflows/checks.yml`,
and repository templates. The later Run Receipt records the resolved Python and dependency versions
from these artifacts, while the bundle README explains the reproducible foundation used for the
completed work.

### Acceptance criteria

- [ ] `uv sync --frozen --all-groups` creates a Python 3.11 environment from a fresh checkout.
- [ ] `requirements.txt` is generated from `uv.lock` and is not hand-maintained.
- [ ] PR checks run Ruff format, Ruff lint, interface tests, data-contract checks, and committed
      Bundle Integrity checks without executing CABT matches.
- [ ] The Issue and pull request templates require outcome, Artifact, verification, risk, and
      dependency evidence, plus the intended bundle README contribution.

### Verification

```bash
uv sync --frozen --all-groups
uv run ruff format --check .
uv run ruff check .
uv run pytest
```

The linked pull request must show the successful `Pull request checks` workflow.

### Dependencies and related work

This Issue unblocks #3. #2 can proceed in the same Target Cycle after the package scaffold exists
locally, but #3 cannot start until both are complete.

### Fictional ownership and stakeholder context

Erika Otsuka owns the narrative work. Professor Juniper wants the environment commands to be usable
as a teaching example. Neither is a GitHub assignee or required reviewer.

### Risks and limitations

The CABT dependency is large and can make first-time installation slow. Passing fast checks proves
the scaffold is reproducible; it does not prove that a real simulator match completes.

## Issue 2 — Validate and freeze authoritative English source

**Project metadata:** Misty Williams · September — Week 1 · Ready · M  
**Labels:** `type: implementation`, `area: data`, `priority: high`  
**Dependencies:** None

### Outcome

Callers receive 1,267 trustworthy Card Records from the unchanged authoritative English export,
with zero-to-three ordered Card Actions per record and an inspectable Source Receipt.

### Context

The export contains 2,022 rows because action data repeats card-level fields. Treating every row as
a card or silently selecting the alternate export would corrupt deck and analysis logic.

### In scope

- Freeze `EN Card Data.csv` by exact path and SHA-256.
- Normalize only blanks, `n/a`, and the `Previos stage` header at the Catalog boundary.
- Reject inconsistent repeated card-level values.
- Aggregate ordered actions without dropping source evidence.
- Add a thin executed exploration notebook using the Catalog interface.

### Out of scope

- Editing either supplied CSV, combining exports, translating Japanese data, and agent behavior.
- General-purpose dataframe cleaning or speculative schema abstraction.

### Artifacts and Bundle contribution

The Catalog module, data-contract tests, Source Receipt, data guide, and
`notebooks/01_card_catalog_exploration.ipynb`. The Source Receipt becomes the manifest's source
relationship. The later bundle README reports the EDA findings, source anomalies, normalization and
aggregation choices, preserved source content, and downstream implications. That summary includes
the source shape, action and stage/type distributions, structural missingness and the no-imputation
decision, the retained no-action records, the in-memory header correction, and why the alternate
English export was not combined with the authoritative source.

### Acceptance criteria

- [ ] The source hash is
      `507d8d670c9c3c8d58f400d42eed09270b6b01354332770081bdb455d53b8c84`.
- [ ] The Catalog reports 2,022 rows and 1,267 Card Records.
- [ ] Action-count distribution is 8 records with 0, 536 with 1, 691 with 2, and 32 with 3.
- [ ] A repeated Card ID with inconsistent card-level fields raises a validation error.
- [ ] The notebook imports the Catalog rather than reimplementing parsing and records anomalies and
      limitations with one compact visualization.
- [ ] Its findings and handling decisions are concise enough to carry into the bundle README without
      requiring a reviewer to rerun or read the notebook.

### Verification

```bash
uv run fall-ai-studio validate-source
uv run pytest tests/test_catalog.py tests/test_data_contract.py
```

Expected command output includes the authoritative hash, `row_count: 2022`, and `card_count: 1267`.

### Dependencies and related work

This Issue unblocks #3. It records the source decision in ADR 0002 and the Card Record decision
in ADR 0009.

### Fictional ownership and stakeholder context

Misty Williams owns the narrative work. Professor Elm wants the alternate export retained for
traceability, not silently promoted. Neither is a GitHub assignee or required reviewer.

### Risks and limitations

The source is frozen by hash, not asserted to be complete or error-free in every card field. The
loader normalizes a known header typo without editing or silently correcting source content.

## Issue 3 — Implement deterministic CABT baseline agent and legal deck

**Project metadata:** Brock Harrison · September — Week 2 · Blocked · L  
**Labels:** `type: implementation`, `area: agent`, `priority: high`  
**Dependencies:** #1 and #2

### Outcome

The official 60-card CABT sample deck and deterministic Baseline Agent complete real CABT matches
from either player position, while the first-legal Integration Control remains clearly separated
from the strategy-bearing baseline.

### Context

A CSV-only example cannot demonstrate the Challenge's core integration. The first strategy must be
transparent and stable enough to inspect without being mistaken for a competitive final agent.

### In scope

- Reviewed Reference Deck configuration copied from `kaggle-environments==1.32.7`.
- Frozen Baseline Policy: `EVOLVE → ATTACH → ABILITY → PLAY → ATTACK → END`.
- Stable setup/follow-up choices, yes for initiated effects, and an eight-action progress guard.
- First-legal Integration Control, CABT adapter, recorded observations, and in-memory test adapter.

### Out of scope

- Deck optimization, card-text search, damage optimization, opponent modeling, search, or learning.
- Win-rate acceptance gates and a claim of deterministic CABT episodes.

### Artifacts and Bundle contribution

`config/reference-deck.json`, the Battle module, recorded observation fixtures, and public-interface
tests. The exact deck and dependency version are copied into the later bundle, whose README explains
the implemented policy, the Integration Control distinction, and what the smoke evidence does and
does not establish.

### Acceptance criteria

- [ ] The Reference Deck contains exactly 60 known Card IDs and matches the official sample deck.
- [ ] Recorded-observation tests prove action priority, stable follow-ups, and the progress guard.
- [ ] A local two-match CABT smoke run completes once with the Baseline Agent in each position and
      reports zero invalid or errored matches.
- [ ] The Integration Control is identified as an execution control, not the Baseline Agent.

### Verification

```bash
uv run pytest tests/test_battle.py
uv run fall-ai-studio smoke-match --matches 2
```

Attach the smoke summary to the pull request as development evidence; do not approve a bundle from
the local run.

### Dependencies and related work

Blocked by #1 and #2. Completion unblocks #4.

### Fictional ownership and stakeholder context

Brock Harrison owns the narrative work. Professor Oak wants a transparent comparison point before
any complex strategy. Neither is a GitHub assignee or required reviewer.

### Risks and limitations

The fixed deck and rule policy are integration examples, not claims of competitive strength. CABT
does not expose a documented deterministic seed, so complete reruns may produce different outcomes.

## Issue 4 — Run CABT baseline and assemble Artifact Bundle

**Project metadata:** Ash Ketchum · September — Week 3 · Backlog · L  
**Labels:** `type: experiment`, `area: evaluation`, `priority: high`  
**Dependencies:** #3

### Outcome

A manually dispatched GitHub Actions Workflow Run completes 20 real CABT matches—10 with the
Baseline Agent in each position—and produces a complete `september-baseline-v1` candidate bundle
with zero invalid or errored episodes.

### Context

Acceptance evidence must identify the code, source, deck, environment, settings, results, and
interpretation. It must also give the next reader a self-contained overview of the completed work,
findings, handling decisions, limitations, and detailed evidence. Loose output files, a successful
command without provenance, or a bundle with only a file list are not an Artifact Bundle.

### In scope

- Balanced Evaluation Plan and structured Match Results.
- GitHub Actions acceptance workflow from an explicit protected-`main` commit.
- A bundle `README.md` covering completed setup, EDA, baseline implementation, evaluation findings,
  handling decisions, limitations, verification, and an evidence-file guide.
- Run Receipt, manifest, hashes, summary, representative replay, interpretation, and limitations.
- Candidate archive upload for inspection and later unchanged release attachment.

### Out of scope

- A minimum win rate, statistical significance, post-result policy tuning, local approval, and
  automatically committing workflow output.

### Artifacts and Bundle contribution

The complete candidate directory `output/september-baseline-v1/` and
`september-baseline-v1.zip`, uploaded by the Workflow Run. After inspection, the unchanged directory
is committed at `artifacts/september-baseline-v1/` through a pull request. Its `README.md` is the
human entry point; the manifest and integrity report prove that overview travels with the detailed
evidence.

### Acceptance criteria

- [ ] Exactly 20 matches complete, with 10 from each Baseline Agent position.
- [ ] The summary reports zero invalid or errored matches and position-aware win/loss/draw counts.
- [ ] The bundle contains all eleven required files and passes recomputed Bundle Integrity.
- [ ] `README.md` summarizes the work completed across predecessor Issues; reports the EDA findings
      (including source shape, action and stage/type distributions, structural missingness, and
      source-selection implications) and how they were handled; states the baseline results and
      limitations; and links both candidate and committed verification commands plus the detailed
      evidence files.
- [ ] The manifest names the evaluated commit, authoritative source hash, deck hash, dependency
      versions, configuration, and workflow URL.
- [ ] Interpretation makes no competitive or seeded-repeatability claim.

### Verification

Dispatch **September milestone acceptance** with the full protected-`main` commit SHA, then run:

```bash
uv run fall-ai-studio verify-bundle output/september-baseline-v1
```

Link the Workflow Run and uploaded artifact in the Issue and pull request.

### Dependencies and related work

Blocked by #3. The unchanged committed candidate unblocks #5.

### Fictional ownership and stakeholder context

Ash Ketchum owns the narrative work. Professor Oak wants outcome differences described rather than
tuned away. Neither is a GitHub assignee or required reviewer.

### Risks and limitations

Twenty unseeded matches support integration acceptance, not statistical performance conclusions.
Only the GitHub Actions run may approve a candidate; local output remains development evidence.

## Issue 5 — Independently verify and hand off September baseline

**Project metadata:** Gary Oak · September — Week 4 · Backlog · M  
**Labels:** `type: review`, `area: reproducibility`, `priority: high`  
**Dependencies:** #4

### Outcome

A second Workflow Run from a fresh checkout verifies the committed bundle, repeats the 20-match
procedure, records outcome differences without requiring equality, and supplies the evidence needed
for an annotated September release.

### Context

This solo-owned example cannot truthfully claim fictional human review. Independent Verification
therefore means technical independence of checkout, frozen environment, integrity computation, and
rerun. Live teams should additionally use a different real person.

### In scope

- Fresh GitHub Actions checkout and `uv sync --frozen`.
- Recomputed Bundle Integrity, including the manifested README overview, and repeated 20-match
  Evaluation Plan.
- Machine-readable verification receipt with original and rerun outcomes.
- Milestone handoff, annotated tag, GitHub Release, and unchanged acceptance archive.

### Out of scope

- Fabricated approval, identical random outcomes, changing the accepted bundle during verification,
  and deleting old branches before confirming they contain no unique work.

### Artifacts and Bundle contribution

`independent-verification.json`, the second Workflow Run URL, the closed September milestone, and
the annotated tag/release. Verification is evidence about the bundle; it does not rewrite it.

### Acceptance criteria

- [ ] A fresh workflow verifies all bundle files, hashes, schemas, and source/config relationships.
- [ ] The README provides an accurate handoff from completed work and findings to the supporting
      evidence, including EDA handling decisions, limitations, and verification instructions.
- [ ] The rerun completes 20 matches with 10 per position and zero invalid or errored matches.
- [ ] Original and rerun outcome counts are both recorded; equality is not required.
- [ ] The Issue explicitly states that technical independence is not second-human review.
- [ ] The milestone closes only after all five Issues are complete and the release attaches the
      exact archive produced by the acceptance run.

### Verification

Dispatch **September independent verification** from the protected-`main` commit containing the
bundle. Inspect `independent-verification.json`, confirm `conclusion: verified`, and link the run to
the Issue and release notes.

### Dependencies and related work

Blocked by #4. This Issue completes the September Baseline milestone and supplies the starting
evidence for October Analysis.

### Fictional ownership and stakeholder context

Gary Oak owns the narrative work. Professor Juniper wants the handoff language to distinguish
technical rerun independence from a real collaborator's approval. Neither is a GitHub assignee or
required reviewer.

### Risks and limitations

A fresh workflow is technically independent but is not second-human review. Because CABT is
unseeded, outcome equality is recorded for comparison and never required for verification.

## Branch and release policy

Create each Issue Branch just in time from current `main`; link it with `Closes #N`; merge only after
required checks and conversations are complete; use a merge commit; delete the source branch after
merge. The exact reviewed commit remains reachable through the merge graph and can be named in Run
Receipts.

At milestone completion, create an annotated `september-baseline-v1` tag from protected `main`,
publish a GitHub Release, attach the exact acceptance archive, and close the native milestone. Do
not use `dev` or durable month branches as release records.
