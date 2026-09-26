import hashlib
import json
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
    bundle = tmp_path / "issue-1-reproducible-project"
    payload = bundle / "files"
    payload.mkdir(parents=True)
    (payload / "pyproject.toml").write_text(
        '[project]\nrequires-python = ">=3.11,<3.12"\n', encoding="utf-8"
    )
    (bundle / "README.md").write_text(
        "# Issue #1 Work Bundle\n\n"
        "## Outcome\n\nThe reproducible project setup is complete.\n\n"
        "## Work completed\n\nThe frozen environment and checks were verified.\n\n"
        "## Files delivered\n\n"
        "- [Project configuration](files/pyproject.toml)\n\n"
        "## Verification\n\nAll required commands passed.\n\n"
        "## Risks and limitations\n\nThis does not approve simulator results.\n",
        encoding="utf-8",
    )
    _write_json(
        bundle / "verification.json",
        {
            "schema": ISSUE_VERIFICATION_SCHEMA,
            "issue_number": 1,
            "source_commit": "1" * 40,
            "status": "passed",
            "environment": {"python": "3.11.13", "uv": "0.8.22"},
            "commands": [
                {
                    "command": "uv sync --frozen --all-groups",
                    "exit_code": 0,
                    "result": "Environment synchronized from uv.lock.",
                }
            ],
        },
    )
    content_paths = ["README.md", "verification.json", "files/pyproject.toml"]
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
            "source_commit": "1" * 40,
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
    assert result.checked_files == 3
    assert not result.errors


def test_issue_work_bundle_detects_tampered_source_file(issue_work_bundle: Path) -> None:
    (issue_work_bundle / "files/pyproject.toml").write_text(
        '[project]\nrequires-python = "*"\n', encoding="utf-8"
    )

    result = verify_bundle(issue_work_bundle)

    assert not result.valid
    assert any("files/pyproject.toml SHA-256 mismatch" in error for error in result.errors)


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
