# Issue #1 Work Bundle: Reproducible Python Project and Automated Checks

This is the detailed completion report for
[Issue #1](https://github.com/ejparnell/example-project-fall-2026/issues/1), **Establish
reproducible Python project and automated checks**. The evidence is tied to source commit
`276a0335e1a6ac5e86edcab67dc2636e10b66608` and includes portable Git history for independently
checking that relationship.

## Outcome

A contributor can create the project environment from a fresh checkout with Python 3.11 and the
committed `uv.lock`, invoke the installed `fall-ai-studio` command, and receive the same fast
format, lint, test, and bundle-integrity feedback used by pull requests. A generated
`requirements.txt` provides the Colab path without becoming a second dependency source.

The repository now also records completed Issues as verified, report-style Issue Work Bundles and
documents the pickup, branch, pull request, merge, and closing-comment lifecycle used for this work.

## Work completed

- Declared Python `>=3.11,<3.12`, the installable `src/` package, console entry point, runtime
  dependencies, development tools, and their exact cross-platform resolution.
- Kept `.python-version`, `pyproject.toml`, and `uv.lock` as the canonical environment contract;
  regenerated `requirements.txt` from that lock rather than maintaining it by hand.
- Configured GitHub Actions to install the frozen environment and run Ruff formatting, Ruff lint,
  the public tests, source/deck validation, and integrity checks for every committed bundle. CABT
  match execution remains outside the fast pull-request gate.
- Added structured Issue and pull request templates that require outcomes, artifacts, verification,
  dependencies, risks, review guidance, and a closure handoff.
- Added a versioned Issue Work Bundle schema. Its verifier rejects changed, missing, extra, unsafe,
  empty-directory, or symlinked content; validates the Issue relationship and report; requires the
  expected Issue #1 checks; and compares each delivered snapshot with its declared Git commit.
- Made the evidence portable by including the complete runtime source plus
  [`source.git.bundle`](source.git.bundle), a complete Git history bundle containing the declared
  source commit.
- Documented that contributors claim Issues, use short-lived Issue branches, merge only after checks
  pass, and leave a concise overview comment after GitHub closes the Issue.

## Files delivered

The `files/` tree preserves 21 repository-relative paths from the verified source commit. Together
these are the environment, automation, interface, integrity, test, decision, and workflow files
needed to review and reproduce Issue #1's delivery.

| Area | Exact file snapshot | Why it is included |
| --- | --- | --- |
| Python selection | [`.python-version`](files/.python-version) | Selects Python 3.11 for local tooling. |
| Project contract | [`pyproject.toml`](files/pyproject.toml) | Declares Python bounds, package, CLI, dependencies, and tool settings. |
| Frozen environment | [`uv.lock`](files/uv.lock) | Pins the complete dependency resolution. |
| Colab export | [`requirements.txt`](files/requirements.txt) | Generated, hash-pinned installation path derived from `uv.lock`. |
| PR automation | [`.github/workflows/checks.yml`](files/.github/workflows/checks.yml) | Runs the frozen install and fast quality/contract checks. |
| Issue configuration | [`.github/ISSUE_TEMPLATE/config.yml`](files/.github/ISSUE_TEMPLATE/config.yml) | Keeps work intake on structured GitHub Issues. |
| Issue template | [`.github/ISSUE_TEMPLATE/work-item.yml`](files/.github/ISSUE_TEMPLATE/work-item.yml) | Requires an agent-ready outcome and evidence contract. |
| Pull request template | [`.github/pull_request_template.md`](files/.github/pull_request_template.md) | Requires linked work, evidence, risks, and closure handoff. |
| Package marker | [`src/fall_ai_studio/__init__.py`](files/src/fall_ai_studio/__init__.py) | Makes the source package installable. |
| Battle runtime | [`src/fall_ai_studio/battle.py`](files/src/fall_ai_studio/battle.py) | Supplies the battle interfaces imported by the public CLI. |
| Catalog runtime | [`src/fall_ai_studio/catalog.py`](files/src/fall_ai_studio/catalog.py) | Supplies the card/source validation interfaces imported by the CLI. |
| Public CLI | [`src/fall_ai_studio/cli.py`](files/src/fall_ai_studio/cli.py) | Implements the configured `fall-ai-studio` entry point. |
| Bundle integrity | [`src/fall_ai_studio/evidence.py`](files/src/fall_ai_studio/evidence.py) | Verifies Issue Work and milestone bundle schemas, including portable provenance. |
| Integrity tests | [`tests/test_issue_work_bundle.py`](files/tests/test_issue_work_bundle.py) | Proves valid reports pass and tampering, incomplete evidence, or false provenance fails. |
| Repository overview | [`README.md`](files/README.md) | Explains setup, evidence types, and their approval boundary. |
| Artifact guide | [`artifacts/README.md`](files/artifacts/README.md) | Defines Issue Work versus approved milestone bundles. |
| Branch decision | [`docs/adr/0003-use-short-lived-issue-branches.md`](files/docs/adr/0003-use-short-lived-issue-branches.md) | Records the branch and merge strategy. |
| Environment decision | [`docs/adr/0005-use-python-3-11-and-uv.md`](files/docs/adr/0005-use-python-3-11-and-uv.md) | Records the Python, uv, lock, and export choices. |
| Bundle decision | [`docs/adr/0011-record-issue-work-bundles.md`](files/docs/adr/0011-record-issue-work-bundles.md) | Records the per-Issue report and exact-file contract. |
| Tracker workflow | [`docs/agents/issue-tracker.md`](files/docs/agents/issue-tracker.md) | Defines claim, branch, PR, merge, and closing-comment steps. |
| Canonical Issue | [`docs/project/september-baseline.md`](files/docs/project/september-baseline.md) | Retains Issue #1's outcome, acceptance, and bundle requirements. |

Supporting evidence consists of [`verification.json`](verification.json), the machine-readable command
receipt; [`source.git.bundle`](source.git.bundle), the portable source history; and `manifest.json`,
the authoritative inventory. The manifest records a SHA-256 digest and byte size for this report,
the receipt, the Git bundle, and every source snapshot, so a reviewer can detect an incomplete or
altered handoff.

## Verification

Verification ran on 2026-09-26 from a new local clone checked out at the detached source commit,
with no pre-existing project virtual environment. The complete machine-readable receipt is in
[`verification.json`](verification.json).

| Command | Result |
| --- | --- |
| `uv sync --frozen --all-groups` | Created a Python 3.11.13 `.venv` and installed all 122 locked packages. |
| `uv export --frozen --no-dev --format requirements-txt --output-file requirements.txt` plus `git diff --exit-code -- requirements.txt` | Regenerated output exactly matched the committed export. |
| `uv run ruff format --check .` | Passed; 10 files already formatted. |
| `uv run ruff check .` | Passed with no lint findings. |
| `uv run pytest -q` | Passed; 48 tests in 5.56 seconds. |
| `uv run fall-ai-studio --help` | Passed and exposed the installed public CLI. |
| `git bundle verify artifacts/issue-1-reproducible-project/source.git.bundle` | Passed; the bundle contains commit `276a0335e1a6ac5e86edcab67dc2636e10b66608` and complete history. |
| Compare every manifested `source_path` with commit `276a0335e1a6ac5e86edcab67dc2636e10b66608` | All 21 delivered snapshots byte-matched the declared source commit. |

Recompute integrity in the repository:

```bash
uv run fall-ai-studio verify-bundle artifacts/issue-1-reproducible-project
```

Or verify the extracted artifact independently of the parent checkout:

```bash
ISSUE_WORK_BUNDLE="$(cd issue-1-reproducible-project && pwd)"
ISSUE_WORK_VENV="$(mktemp -d)/venv"
export ISSUE_WORK_BUNDLE ISSUE_WORK_VENV
export UV_PROJECT_ENVIRONMENT="$ISSUE_WORK_VENV"
export PYTHONDONTWRITEBYTECODE=1
cd "$ISSUE_WORK_BUNDLE/files"
uv sync --frozen --all-groups
uv run fall-ai-studio verify-bundle "$ISSUE_WORK_BUNDLE"
```

The second path uses the bundled runtime code and checks snapshot provenance against the adjacent
`source.git.bundle` rather than relying on Git objects from the original repository. Its virtual
environment and Python bytecode stay outside the sealed artifact, so verification does not change
the bundle it is checking.

## Risks and limitations

- The CABT dependency tree is intentionally large, so the first synchronized install can be slow;
  caching improves speed without changing the locked resolution.
- This Issue proves project setup, fast checks, templates, and the bundle handoff. It does not run a
  CABT match, approve a September milestone bundle, or make a claim about agent behavior.
- The verification receipt describes a local isolated clone. The linked pull request's GitHub
  Actions run supplies separate hosted check evidence before merge.
- The `files/` directory is an auditable snapshot, not a replacement for Git. Development and
  integration continue in the normal repository tree and history.
