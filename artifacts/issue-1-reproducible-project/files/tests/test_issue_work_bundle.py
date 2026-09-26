import hashlib
import json
import subprocess
from pathlib import Path

import pytest

from fall_ai_studio.evidence import (
    ISSUE_VERIFICATION_SCHEMA,
    ISSUE_WORK_BUNDLE_SCHEMA,
    verify_bundle,
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_json(path: Path, document: object) -> None:
    path.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _reseal(bundle: Path, changed_path: str) -> None:
    manifest_path = bundle / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    entry = next(item for item in manifest["files"] if item["path"] == changed_path)
    artifact = bundle / changed_path
    entry["sha256"] = _sha256(artifact)
    entry["bytes"] = artifact.stat().st_size
    _write_json(manifest_path, manifest)


@pytest.fixture
def issue_work_bundle(tmp_path: Path) -> Path:
    repository = tmp_path / "repository"
    repository.mkdir()
    source_contents = '[project]\nrequires-python = ">=3.11,<3.12"\n'
    (repository / "pyproject.toml").write_text(source_contents, encoding="utf-8")
    subprocess.run(["git", "init", "--quiet"], cwd=repository, check=True)
    subprocess.run(
        ["git", "config", "user.email", "bundle-tests@example.com"],
        cwd=repository,
        check=True,
    )
    subprocess.run(["git", "config", "user.name", "Bundle Tests"], cwd=repository, check=True)
    subprocess.run(["git", "add", "pyproject.toml"], cwd=repository, check=True)
    subprocess.run(
        ["git", "commit", "--quiet", "-m", "Add project contract"],
        cwd=repository,
        check=True,
    )
    source_commit = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repository,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()

    bundle = repository / "artifacts" / "issue-1-reproducible-project"
    payload = bundle / "files"
    payload.mkdir(parents=True)
    subprocess.run(
        ["git", "bundle", "create", str(bundle / "source.git.bundle"), "--all"],
        cwd=repository,
        check=True,
    )
    (payload / "pyproject.toml").write_text(source_contents, encoding="utf-8")
    commands = [
        "uv sync --frozen --all-groups",
        "uv export --frozen --no-dev --format requirements-txt --output-file requirements.txt",
        "uv run ruff format --check .",
        "uv run ruff check .",
        "uv run pytest -q",
        "uv run fall-ai-studio --help",
    ]
    (bundle / "README.md").write_text(
        "# Issue #1 Work Bundle\n\n"
        "## Outcome\n\nThe reproducible project setup is complete.\n\n"
        "## Work completed\n\nThe frozen environment and checks were verified.\n\n"
        "## Files delivered\n\n"
        "- [Project configuration](files/pyproject.toml)\n\n"
        "The portable source history is [source.git.bundle](source.git.bundle).\n\n"
        "## Verification\n\n" + "\n".join(f"- `{command}`" for command in commands) + "\n\n"
        "## Risks and limitations\n\nThis does not approve simulator results.\n",
        encoding="utf-8",
    )
    _write_json(
        bundle / "verification.json",
        {
            "schema": ISSUE_VERIFICATION_SCHEMA,
            "finished_at": "2026-09-26T22:00:00Z",
            "issue_number": 1,
            "source_commit": source_commit,
            "status": "passed",
            "environment": {
                "checkout": "fresh clone",
                "platform": "test",
                "pytest": "8.4.2",
                "python": "3.11.13",
                "ruff": "0.13.3",
                "uv": "0.12.19",
            },
            "commands": [
                {
                    "command": command,
                    "exit_code": 0,
                    "result": "Command passed.",
                }
                for command in commands
            ],
        },
    )
    content_paths = [
        "README.md",
        "source.git.bundle",
        "verification.json",
        "files/pyproject.toml",
    ]
    entries = []
    for relative_path in content_paths:
        artifact = bundle / relative_path
        entry = {
            "path": relative_path,
            "sha256": _sha256(artifact),
            "bytes": artifact.stat().st_size,
        }
        if relative_path.startswith("files/"):
            entry["source_path"] = relative_path.removeprefix("files/")
        entries.append(entry)
    _write_json(
        bundle / "manifest.json",
        {
            "schema": ISSUE_WORK_BUNDLE_SCHEMA,
            "bundle_id": bundle.name,
            "created_at": "2026-09-26T22:00:00Z",
            "source_commit": source_commit,
            "issue": {
                "number": 1,
                "title": "Establish reproducible Python project and automated checks",
                "url": "https://github.com/ejparnell/example-project-fall-2026/issues/1",
            },
            "required_files": content_paths,
            "files": entries,
        },
    )
    return bundle


def test_issue_work_bundle_is_a_verified_report_with_source_files(
    issue_work_bundle: Path,
) -> None:
    result = verify_bundle(issue_work_bundle)

    assert result.valid
    assert result.checked_files == 4
    assert not result.errors


def test_issue_work_bundle_detects_tampered_source_file(issue_work_bundle: Path) -> None:
    (issue_work_bundle / "files/pyproject.toml").write_text(
        '[project]\nrequires-python = "*"\n', encoding="utf-8"
    )

    result = verify_bundle(issue_work_bundle)

    assert not result.valid
    assert any("files/pyproject.toml SHA-256 mismatch" in error for error in result.errors)


def test_issue_work_bundle_rejects_resealed_file_not_from_source_commit(
    issue_work_bundle: Path,
) -> None:
    (issue_work_bundle / "files/pyproject.toml").write_text(
        '[project]\nrequires-python = "*"\n', encoding="utf-8"
    )
    _reseal(issue_work_bundle, "files/pyproject.toml")

    result = verify_bundle(issue_work_bundle)

    assert not result.valid
    assert any("does not match source commit" in error for error in result.errors)


def test_issue_work_bundle_rejects_resealed_readme_without_report_sections(
    issue_work_bundle: Path,
) -> None:
    (issue_work_bundle / "README.md").write_text("# Files\n", encoding="utf-8")
    _reseal(issue_work_bundle, "README.md")

    result = verify_bundle(issue_work_bundle)

    assert not result.valid
    assert any("README.md is missing report section" in error for error in result.errors)


def test_issue_work_bundle_rejects_failed_or_unrelated_verification(
    issue_work_bundle: Path,
) -> None:
    verification_path = issue_work_bundle / "verification.json"
    verification = json.loads(verification_path.read_text(encoding="utf-8"))
    verification.update({"issue_number": 2, "status": "failed"})
    _write_json(verification_path, verification)
    _reseal(issue_work_bundle, "verification.json")

    result = verify_bundle(issue_work_bundle)

    assert not result.valid
    assert any("issue relationship" in error for error in result.errors)
    assert any("successful verification" in error for error in result.errors)


def test_issue_work_bundle_rejects_unreported_extra_file(issue_work_bundle: Path) -> None:
    (issue_work_bundle / "notes.txt").write_text("not declared\n", encoding="utf-8")

    result = verify_bundle(issue_work_bundle)

    assert not result.valid
    assert any("Undeclared file: notes.txt" in error for error in result.errors)


def test_issue_work_bundle_rejects_unreported_empty_directory(
    issue_work_bundle: Path,
) -> None:
    (issue_work_bundle / "empty-notes").mkdir()

    result = verify_bundle(issue_work_bundle)

    assert not result.valid
    assert any("Undeclared directory: empty-notes" in error for error in result.errors)


def test_issue_work_bundle_cannot_use_a_milestone_name(issue_work_bundle: Path) -> None:
    renamed = issue_work_bundle.with_name("september-baseline-v1")
    issue_work_bundle.rename(renamed)
    manifest_path = renamed / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["bundle_id"] = renamed.name
    _write_json(manifest_path, manifest)

    result = verify_bundle(renamed)

    assert not result.valid
    assert any("directory name" in error for error in result.errors)


def test_issue_work_bundle_requires_reachable_source_commit(
    issue_work_bundle: Path,
) -> None:
    verification_path = issue_work_bundle / "verification.json"
    verification = json.loads(verification_path.read_text(encoding="utf-8"))
    verification["source_commit"] = "0" * 40
    _write_json(verification_path, verification)
    _reseal(issue_work_bundle, "verification.json")
    manifest_path = issue_work_bundle / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["source_commit"] = "0" * 40
    _write_json(manifest_path, manifest)

    result = verify_bundle(issue_work_bundle)

    assert not result.valid
    assert any("source commit is not available" in error for error in result.errors)


def test_issue_work_bundle_requires_environment_and_issue_commands(
    issue_work_bundle: Path,
) -> None:
    verification_path = issue_work_bundle / "verification.json"
    verification = json.loads(verification_path.read_text(encoding="utf-8"))
    verification["environment"] = {}
    verification["commands"] = [{"command": "true", "exit_code": 0, "result": "claimed success"}]
    _write_json(verification_path, verification)
    _reseal(issue_work_bundle, "verification.json")

    result = verify_bundle(issue_work_bundle)

    assert not result.valid
    assert any("environment" in error for error in result.errors)
    assert any("required Issue #1 command" in error for error in result.errors)
