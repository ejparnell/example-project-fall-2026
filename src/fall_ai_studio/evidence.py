"""Create and independently verify complete Artifact Bundles."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from fall_ai_studio.battle import EvaluationResult
from fall_ai_studio.catalog import Deck, SourceReceipt

BUNDLE_SCHEMA = "fall-ai-studio/artifact-bundle/v1"
INTEGRITY_SCHEMA = "fall-ai-studio/bundle-integrity/v1"
REQUIRED_BUNDLE_FILES = (
    "evaluation-plan.json",
    "integrity.json",
    "interpretation.md",
    "limitations.md",
    "manifest.json",
    "matches.jsonl",
    "reference-deck.json",
    "replay.json",
    "run-receipt.json",
    "summary.json",
)
CONTENT_FILES = tuple(
    name for name in REQUIRED_BUNDLE_FILES if name not in {"integrity.json", "manifest.json"}
)


@dataclass(frozen=True)
class RunReceipt:
    run_id: str
    status: str
    started_at: str
    finished_at: str
    code_revision: str
    environment: str
    workflow_url: str
    command: str
    dependencies: Mapping[str, str]


@dataclass(frozen=True)
class IntegrityResult:
    valid: bool
    checked_files: int
    errors: tuple[str, ...]
    manifest_sha256: str


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_json(path: Path, document: Any) -> None:
    path.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _media_type(name: str) -> str:
    if name.endswith(".json") or name.endswith(".jsonl"):
        return "application/json"
    return "text/markdown"


def _match_document(match: Any) -> dict[str, Any]:
    document = asdict(match)
    document.pop("replay", None)
    return document


def _summary_document(evaluation: EvaluationResult) -> dict[str, Any]:
    return {
        "schema": "fall-ai-studio/evaluation-summary/v1",
        "accepted": evaluation.accepted,
        "match_count": evaluation.summary.match_count,
        "completed_matches": evaluation.summary.completed_matches,
        "invalid_or_error_matches": evaluation.summary.invalid_or_error_matches,
        "by_baseline_position": {
            str(position): asdict(summary)
            for position, summary in evaluation.summary.by_position.items()
        },
        "terminations": dict(evaluation.summary.terminations),
    }


def assemble_bundle(
    destination: str | Path,
    *,
    evaluation: EvaluationResult,
    source: SourceReceipt,
    deck: Deck,
    deck_path: str | Path,
    receipt: RunReceipt,
    interpretation: str,
    limitations: str,
) -> Path:
    """Write a complete bundle, refusing partial or unsuccessful run evidence."""

    if not evaluation.accepted:
        raise ValueError("Only a completed, zero-error evaluation can form an Artifact Bundle")
    if receipt.status != "succeeded":
        raise ValueError("Only a successful Workflow Run can form an Artifact Bundle")
    bundle = Path(destination)
    if bundle.exists() and any(bundle.iterdir()):
        raise FileExistsError(f"Artifact Bundle destination is not empty: {bundle}")
    bundle.mkdir(parents=True, exist_ok=True)

    (bundle / "reference-deck.json").write_bytes(Path(deck_path).read_bytes())
    _write_json(
        bundle / "evaluation-plan.json",
        {
            "schema": "fall-ai-studio/evaluation-plan/v1",
            "match_count": len(evaluation.plan.baseline_positions),
            "baseline_positions": list(evaluation.plan.baseline_positions),
            "replay_match_id": evaluation.plan.replay_match_id,
            "random_seed": None,
            "random_seed_note": "CABT exposes no documented deterministic seed setting.",
        },
    )
    receipt_document = {
        "schema": "fall-ai-studio/run-receipt/v1",
        **asdict(receipt),
        "source": asdict(source),
        "deck": {"name": deck.name, "sha256": deck.sha256, "source": deck.source},
    }
    _write_json(bundle / "run-receipt.json", receipt_document)
    matches_text = "".join(
        json.dumps(_match_document(match), sort_keys=True) + "\n" for match in evaluation.matches
    )
    (bundle / "matches.jsonl").write_text(matches_text, encoding="utf-8")
    _write_json(bundle / "summary.json", _summary_document(evaluation))
    replay = next((match.replay for match in evaluation.matches if match.replay is not None), None)
    if replay is None:
        raise ValueError("An Artifact Bundle requires one representative replay")
    _write_json(bundle / "replay.json", replay)
    (bundle / "interpretation.md").write_text(interpretation, encoding="utf-8")
    (bundle / "limitations.md").write_text(limitations, encoding="utf-8")

    inventory = [
        {
            "path": name,
            "sha256": _sha256(bundle / name),
            "bytes": (bundle / name).stat().st_size,
            "media_type": _media_type(name),
        }
        for name in CONTENT_FILES
    ]
    manifest = {
        "schema": BUNDLE_SCHEMA,
        "bundle_id": bundle.name,
        "created_at": receipt.finished_at,
        "code_revision": receipt.code_revision,
        "source": asdict(source),
        "workflow": {"run_id": receipt.run_id, "url": receipt.workflow_url},
        "configuration": {
            "match_count": len(evaluation.matches),
            "baseline_matches_by_position": {
                "0": evaluation.plan.baseline_positions.count(0),
                "1": evaluation.plan.baseline_positions.count(1),
            },
            "deck_sha256": deck.sha256,
            "random_seed": None,
        },
        "required_files": list(REQUIRED_BUNDLE_FILES),
        "files": inventory,
    }
    _write_json(bundle / "manifest.json", manifest)
    provisional = _verify_bundle(bundle, require_integrity=False)
    _write_json(
        bundle / "integrity.json",
        {
            "schema": INTEGRITY_SCHEMA,
            "valid": provisional.valid,
            "verified_at": receipt.finished_at,
            "checked_files": provisional.checked_files,
            "manifest_sha256": provisional.manifest_sha256,
            "errors": list(provisional.errors),
        },
    )
    final = verify_bundle(bundle)
    if not final.valid:
        raise ValueError(f"New Artifact Bundle failed integrity checks: {final.errors}")
    return bundle


def verify_bundle(path: str | Path) -> IntegrityResult:
    """Recompute Bundle Integrity without trusting the stored integrity report."""

    return _verify_bundle(Path(path), require_integrity=True)


def _verify_bundle(bundle: Path, *, require_integrity: bool) -> IntegrityResult:
    errors: list[str] = []
    manifest_path = bundle / "manifest.json"
    manifest_hash = _sha256(manifest_path) if manifest_path.is_file() else ""
    actual_files = {path.name for path in bundle.iterdir() if path.is_file()}
    expected_files = set(REQUIRED_BUNDLE_FILES)
    if not require_integrity:
        expected_files.remove("integrity.json")
    for missing in sorted(expected_files - actual_files):
        errors.append(f"Missing required file: {missing}")
    for extra in sorted(actual_files - set(REQUIRED_BUNDLE_FILES)):
        errors.append(f"Undeclared file: {extra}")

    if not manifest_path.is_file():
        return IntegrityResult(False, 0, tuple(errors), manifest_hash)
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as error:
        errors.append(f"manifest.json is not readable JSON: {error}")
        return IntegrityResult(False, 0, tuple(errors), manifest_hash)
    if manifest.get("schema") != BUNDLE_SCHEMA:
        errors.append("manifest.json has an unsupported schema")
    if set(manifest.get("required_files", [])) != set(REQUIRED_BUNDLE_FILES):
        errors.append("manifest.json required_files does not match the Bundle contract")

    entries = manifest.get("files", [])
    entry_names = {entry.get("path") for entry in entries if isinstance(entry, dict)}
    if entry_names != set(CONTENT_FILES):
        errors.append("manifest.json file inventory does not match the Bundle contract")
    checked = 0
    for entry in entries:
        name = entry.get("path")
        artifact = bundle / name if isinstance(name, str) else None
        if artifact is None or not artifact.is_file():
            continue
        checked += 1
        if _sha256(artifact) != entry.get("sha256"):
            errors.append(f"{name} SHA-256 mismatch")
        if artifact.stat().st_size != entry.get("bytes"):
            errors.append(f"{name} byte-size mismatch")

    try:
        receipt = json.loads((bundle / "run-receipt.json").read_text(encoding="utf-8"))
        summary = json.loads((bundle / "summary.json").read_text(encoding="utf-8"))
        plan = json.loads((bundle / "evaluation-plan.json").read_text(encoding="utf-8"))
        if manifest.get("code_revision") != receipt.get("code_revision"):
            errors.append("Code revision relationship does not match the Run Receipt")
        if manifest.get("source") != receipt.get("source"):
            errors.append("Authoritative Source relationship does not match the Run Receipt")
        if manifest.get("configuration", {}).get("match_count") != summary.get("match_count"):
            errors.append("Evaluation match count does not match the manifest")
        if plan.get("match_count") != summary.get("match_count"):
            errors.append("Evaluation Plan match count does not match the summary")
        if not summary.get("accepted"):
            errors.append("Evaluation summary is not accepted")
        if summary.get("invalid_or_error_matches") != 0:
            errors.append("Evaluation contains invalid or errored matches")
    except (json.JSONDecodeError, OSError) as error:
        errors.append(f"Bundle relationship evidence is unreadable: {error}")

    if require_integrity and (bundle / "integrity.json").is_file():
        try:
            report = json.loads((bundle / "integrity.json").read_text(encoding="utf-8"))
            if report.get("schema") != INTEGRITY_SCHEMA:
                errors.append("integrity.json has an unsupported schema")
            if report.get("manifest_sha256") != manifest_hash:
                errors.append("integrity.json does not refer to the current manifest")
            if report.get("valid") is not True:
                errors.append("integrity.json does not record a valid bundle")
        except (json.JSONDecodeError, OSError) as error:
            errors.append(f"integrity.json is unreadable: {error}")

    return IntegrityResult(not errors, checked, tuple(errors), manifest_hash)
