# Pokémon TCG AI Battle Challenge Example Project

The operating language for the fictional, executable Fall 2026 AI Studio sample project. It distinguishes narrative project roles, delivery records, reproducibility evidence, source data, and the intentionally simple CABT baseline.

## Project Delivery

**Fictional Example Participant**:
A Pokémon-themed placeholder used to demonstrate a Break Through Tech project role. Fictional team members, Challenge Advisors, and the AI Studio Coach appear in narratives and Project fields only; they are never real GitHub accounts, assignees, approvers, or required reviewers.
_Avoid_: Real collaborator, unqualified team member, real CA, real coach

**Fictional Project Board**:
The single GitHub Project named `Pokémon TCG AI Battle Challenge — Fall 2026` that organizes fictional work across September through December. Month-specific views emphasize the Active Project Month while retaining the full timeline.
_Avoid_: Separate monthly board, repository, live Fellow Project Workspace

**Board Ownership Boundary**:
The real GitHub account that owns this repository owns and links the Fictional Project Board. Fictional participants never receive GitHub access or account-based responsibilities.
_Avoid_: Fictional GitHub owner, fake collaborator access, real-person role assignment

**Fictional Project Work Item**:
A repository Issue representing one actionable piece of work and added to the Fictional Project Board. It may deliver teaching code, tests, documentation, or reproducibility evidence; the Issue is the canonical work record, and the board uses no standalone draft items.
_Avoid_: Draft card, board-only task, duplicate task

**Fictional Work Owner**:
The Pokémon-themed team member selected in a Project single-select field and named in the corresponding Issue to show narrative responsibility. The real GitHub Assignees field remains empty.
_Avoid_: GitHub assignee, real collaborator, required reviewer

**Effort**:
The Project's single-select estimate of relative work-item size: Small (S), Medium (M), or Large (L). It is a planning aid distinct from priority or time tracking.
_Avoid_: Priority, actual time tracking, code estimate

**Fictional Project Showcase**:
The use of executable teaching code and collaboration practices that a Fellow team would genuinely use, including tests, evidence, milestones, labels, Project fields, saved views, Issue templates, and pull requests. It excludes production-scale complexity and decorative platform features.
_Avoid_: Exhaustive GitHub feature catalog, decorative board, production-workflow simulation

**Fictional Monthly Milestone**:
The native GitHub Milestone for the Active Project Month, created just in time to frame one monthly outcome. `September Baseline` is the only milestone created now; October Analysis, November Refinement, and December Portfolio remain planned roadmap outcomes until their month becomes active.
_Avoid_: Week-level milestone, future-month work set, branch

**Target Cycle**:
One of four named seven-day Project iterations from the 1st–28th of a fictional month, with a short break before the next month. It records intended sequence, not proof that work occurred then; GitHub timestamps and Work Status remain the honest execution record.
_Avoid_: Backdated execution claim, week-level milestone, continuous cross-month cycle

**Active Project Month**:
The current month in the fictional delivery timeline. Its Issues and Project items form the active work set; completed artifacts remain as history, and future-month Issues are not created early.
_Avoid_: All-month backlog, erased completed work, future-month active work

**Example Issue Label Taxonomy**:
The labels classifying an Issue by `type:` (setup, implementation, experiment, documentation, or review), `area:` (data, agent, evaluation, reproducibility, or portfolio), and `priority:` (high, medium, or low). `needs-ca-feedback` marks actual pending fictional stakeholder context; Work Status is never a label.
_Avoid_: Status label, unprefixed category, label-only work tracking

**Issue Body Contract**:
The required Issue structure: Outcome, Context, In scope, Out of scope, Artifacts and Bundle contribution, Acceptance criteria, Verification, Dependencies and related work, Fictional ownership and stakeholder context, and Risks and limitations. Implementation notes never substitute for observable acceptance or verification evidence.
_Avoid_: Unstructured task list, implementation-only brief, acceptance criteria without verification

**September Baseline Work Set**:
The five dependent Issues that establish the reproducible Python project and checks; validate and freeze the Authoritative Source; implement the Baseline Agent and Reference Deck; run the Baseline Evaluation and assemble its Artifact Bundle; and independently verify and hand off the milestone. The first two target Week 1, followed by one dependent outcome in each remaining Target Cycle.
_Avoid_: Unlinked feature branch, future-month work item, premature handoff

## Integration

**Just-in-Time Branch Rollout**:
An Issue Branch is created only when its Fictional Project Work Item is ready to begin. Future-month and speculative branches are not created in advance.
_Avoid_: Pre-created future branch, all-month branch scaffold, inactive work branch

**Issue Branch**:
A short-lived branch created from current `main` for one Fictional Project Work Item. It is merged only through its linked Pull Request and deleted after merge.
_Avoid_: Durable month branch, shared workstream branch, unlinked branch

**Pull Request**:
The review and integration record linking one Issue Branch and its Issue to Protected Main Branch. It makes the implemented change, automated checks, Artifact evidence, and review outcome inspectable before merge.
_Avoid_: Unlinked code dump, direct push, milestone-wide change set

**Pull Request Contract**:
The required Pull Request structure: Linked Issue, Outcome, Changes, Artifacts and Bundle impact, Verification evidence, Risks and limitations, and Review guidance. A checked box without commands, results, or linked evidence is not verification.
_Avoid_: Orphaned pull request, change list without outcome, unsupported verification claim

**Provenance-Preserving Merge**:
The required merge-commit integration of an approved Pull Request into Protected Main Branch. It preserves the exact reviewed Issue Branch commit named by Workflow Runs and Artifact Manifests after the source branch is deleted.
_Avoid_: Squash merge, rebase merge, rewritten reviewed commit

**Pull Request Verification**:
The fast, portable automated checks required before merge: Ruff formatting and linting, interface-level Pytest tests, Authoritative Source validation, and Bundle Integrity checks. It does not claim that a real CABT match completed.
_Avoid_: Manual spot check, simulator acceptance run, optional CI

**Protected Main Branch**:
The single stable integration branch. It requires an up-to-date Pull Request, Pull Request Verification, and resolved conversations while blocking direct pushes, force pushes, and deletion. The solo-owned example requires no GitHub approval; live multi-person teams should require at least one real collaborator's approval.
_Avoid_: Open trunk, writable default branch, fictional reviewer, unenforceable approval rule

**Milestone Release**:
The annotated Git tag and GitHub Release preserving an accepted Fictional Monthly Milestone from Protected Main Branch. It identifies the approved revision, links committed Artifact Bundles, and attaches an archive identical to each released bundle.
_Avoid_: Month branch, mutable snapshot, unverified release

## Evidence

**Artifact**:
A work product created by project activity, such as source code, configuration, data, results, documentation, a decision record, or review evidence. An Artifact need not contain code.
_Avoid_: Activity without a work product, undocumented claim

**Artifact Bundle**:
A complete package of related Artifacts from one successfully completed task or group of related tasks. It includes the files, an Artifact Manifest, interpretive evidence, and checks confirming it is complete and usable by the next step; partial or failed work is not an approved Artifact Bundle.
_Avoid_: Loose output folder, partial run, failed work, unverified file collection

**Artifact Manifest**:
A machine-readable inventory describing an Artifact Bundle's files, versions, schemas, settings, source relationships, and file hashes. It connects evidence to one source version, code revision, and configuration.
_Avoid_: Handwritten file list, filenames without provenance

**Bundle Integrity**:
Confirmation that an Artifact Bundle contains every declared file and that its hashes, schemas, source relationships, configurations, and required checks match its Artifact Manifest.
_Avoid_: File-presence check, unchecked manifest, assumed completeness

**Workflow Run**:
One recorded execution of ordered project steps using identified source data, code, configuration, software versions, and settings. A run may succeed, fail, or complete with anomalies; only a successful, verified run may support an approved Artifact Bundle.
_Avoid_: Unrecorded execution, notebook state, successful command without provenance

**Milestone Acceptance Run**:
The manually dispatched GitHub Actions Workflow Run on Ubuntu that executes the Baseline Evaluation from an identified commit and produces evidence for the approved Artifact Bundle. Local, Colab, and Kaggle runs support development but cannot approve the milestone bundle.
_Avoid_: Unit test, mocked match, every-commit simulator run, local approval run

**Independent Verification**:
The solo-owned project's second Workflow Run from a fresh checkout and frozen environment, used to confirm Bundle Integrity, repeat the Baseline Evaluation procedure, and record outcome differences without claiming a second-human review or identical random results. In a live team, someone other than the original author performs it.
_Avoid_: Fictional GitHub approval, same-environment rerun, identical-result requirement

## Card Data

**Authoritative Source**:
The approved source-data version from which Workflow Runs begin: `data/pokemon-tcg-ai-battle-challenge-strategy/EN Card Data.csv`, identified by path and SHA-256 hash. A similarly named or modified file does not replace it without a recorded decision.
_Avoid_: Alternate export, newest-looking file, silently corrected source file

**Card Record**:
The Catalog's canonical representation of one simulator `Card ID`, containing invariant card-level fields plus zero to three ordered Card Actions aggregated from source rows. The Authoritative Source contains 1,267 Card Records represented by 2,022 rows.
_Avoid_: CSV row, silently deduplicated row, card name as identifier

**Card Action**:
One ordered move, attack, or ability associated with a Card Record and preserved from its source row's action fields. Missing values are normalized, but source meaning and order are not rewritten.
_Avoid_: Whole card, arbitrary text field, reordered move

**Reference Deck**:
The official 60-card CABT sample deck used unchanged by both the Baseline Agent and Integration Control during the Baseline Evaluation. Holding it constant isolates policy behavior; deck optimization belongs to a later milestone.
_Avoid_: Tuned deck, different opponent deck, September optimization target

## Agent and Evaluation

**Executable Baseline**:
The reproducible Baseline Agent and Reference Deck combination that completes real CABT matches and produces inspectable evidence. It establishes a comparison point without claiming competitive performance.
_Avoid_: CSV-only analysis, mock simulation, final agent

**Integration Control**:
The trivial deterministic first-legal CABT agent used to prove that the deck, harness, and simulator integration can complete a match. It is an execution control, not the strategic baseline.
_Avoid_: Baseline Agent, competitive opponent, strategy claim

**Baseline Agent**:
The first strategy-bearing agent: a deterministic, rule-based policy with documented action priorities and stable tie-breaking. It is evaluated against the Integration Control and remains intentionally simpler than later search- or learning-based agents.
_Avoid_: First-legal agent, final agent, reinforcement-learning policy

**Baseline Policy**:
The frozen September rules: deterministic setup, then `EVOLVE`, `ATTACH`, `ABILITY`, `PLAY`, `ATTACK`, and `END` priority with stable follow-up selection and an eight-action turn guard. It avoids voluntary retreat or discard and performs no card-text search, damage optimization, or opponent modeling.
_Avoid_: Post-result tuning, hidden heuristic, optimized policy

**Baseline Evaluation**:
The series of 20 completed CABT matches between the Baseline Agent and Integration Control, balanced as 10 matches from each player position. Acceptance requires zero invalid or errored episodes plus position-aware outcome and termination summaries; it imposes no minimum win rate and makes only descriptive claims.
_Avoid_: Single-match proof, win-rate gate, seeded-repeatability claim, competitive benchmark
