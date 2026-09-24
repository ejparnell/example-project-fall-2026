"""Create and independently verify complete Artifact Bundles."""

from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
from collections.abc import Mapping
from dataclasses import asdict, dataclass
from importlib import metadata
from pathlib import Path
from typing import Any

from fall_ai_studio.battle import EvaluationResult
from fall_ai_studio.catalog import Deck, SourceReceipt

BUNDLE_SCHEMA = "fall-ai-studio/artifact-bundle/v1"
INTEGRITY_SCHEMA = "fall-ai-studio/bundle-integrity/v1"
PLAN_SCHEMA = "fall-ai-studio/evaluation-plan/v1"
RECEIPT_SCHEMA = "fall-ai-studio/run-receipt/v1"
MATCH_SCHEMA = "fall-ai-studio/match-result/v1"
SUMMARY_SCHEMA = "fall-ai-studio/evaluation-summary/v1"
VERIFICATION_SCHEMA = "fall-ai-studio/independent-verification/v1"
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
CONTENT_SCHEMAS = {
    "evaluation-plan.json": PLAN_SCHEMA,
    "interpretation.md": "fall-ai-studio/interpretation/v1",
    "limitations.md": "fall-ai-studio/limitations/v1",
    "matches.jsonl": MATCH_SCHEMA,
    "reference-deck.json": "fall-ai-studio/reference-deck/v1",
    "replay.json": "kaggle-environments/replay/v1",
    "run-receipt.json": RECEIPT_SCHEMA,
    "summary.json": SUMMARY_SCHEMA,
}


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


def runtime_dependencies() -> dict[str, str]:
    """Return the dependency versions needed to interpret a recorded run."""

    return {
        "python": ".".join(map(str, sys.version_info[:3])),
        "kaggle-environments": metadata.version("kaggle-environments"),
        "fall-ai-studio-pokemon": metadata.version("fall-ai-studio-pokemon"),
    }


def interpretation_document(evaluation: EvaluationResult) -> str:
    """Explain an evaluation without making an unsupported performance claim."""

    position_zero = evaluation.summary.by_position[0]
    position_one = evaluation.summary.by_position[1]
    return (
        "# Interpretation\n\n"
        f"All {evaluation.summary.completed_matches} planned matches completed with zero invalid "
        "or errored episodes. The Baseline Agent recorded "
        f"{position_zero.wins} wins, {position_zero.losses} losses, and "
        f"{position_zero.draws} draws from player position 0, and "
        f"{position_one.wins} wins, {position_one.losses} losses, and "
        f"{position_one.draws} draws from player position 1.\n\n"
        "These results establish an executable comparison point. They are descriptive only: "
        "September has no minimum win-rate gate and makes no claim of competitive strength.\n"
    )


def limitations_document() -> str:
    """Return the limitations that every September Baseline bundle must retain."""

    return (
        "# Limitations\n\n"
        "- CABT exposes no documented deterministic seed setting, so repeated runs may differ.\n"
        "- Twenty matches are enough for integration evidence, not statistical "
        "performance claims.\n"
        "- Both policies use one fixed Reference Deck; deck quality is not evaluated.\n"
        "- The Integration Control is intentionally first-legal and is not a competitive "
        "opponent.\n"
        "- The Baseline Agent uses action-type priorities only; it does not inspect card text, "
        "optimize damage, or model the opponent.\n"
    )


def evaluation_log(evaluation: EvaluationResult) -> str:
    """Return one structured log event per match plus the final summary."""

    events = [
        json.dumps({"event": "match_completed", **document}, sort_keys=True)
        for document in evaluation.to_match_documents()
    ]
    events.append(
        json.dumps(
            {"event": "evaluation_completed", **evaluation.to_summary_document()}, sort_keys=True
        )
    )
    return "\n".join(events) + "\n"


def independent_verification_document(
    *,
    integrity: IntegrityResult,
    original_summary: Mapping[str, Any],
    rerun: EvaluationResult,
    source: SourceReceipt,
    deck: Deck,
    bundle: Path,
    started_at: str,
    finished_at: str,
    code_revision: str,
    run_id: str,
    workflow_url: str,
    environment: str,
    command: str,
    dependencies: Mapping[str, str],
) -> dict[str, Any]:
    """Build a provenance-complete receipt for the second Workflow Run."""

    rerun_summary = rerun.to_summary_document()
    return {
        "schema": VERIFICATION_SCHEMA,
        "status": "succeeded" if rerun.accepted else "failed",
        "started_at": started_at,
        "finished_at": finished_at,
        "run_id": run_id,
        "workflow_url": workflow_url,
        "code_revision": code_revision,
        "environment": environment,
        "command": command,
        "dependencies": dict(dependencies),
        "source": asdict(source),
        "deck": {"name": deck.name, "sha256": deck.sha256, "source": deck.source},
        "evaluation_plan": {
            "match_count": len(rerun.plan.baseline_positions),
            "baseline_positions": list(rerun.plan.baseline_positions),
            "replay_match_id": rerun.plan.replay_match_id,
            "random_seed": None,
        },
        "bundle": str(bundle),
        "bundle_integrity": asdict(integrity),
        "rerun": rerun_summary,
        "original_outcomes": original_summary.get("by_baseline_position"),
        "outcomes_identical": (
            original_summary.get("by_baseline_position") == rerun_summary["by_baseline_position"]
        ),
        "conclusion": "verified" if rerun.accepted else "failed",
        "note": "Outcome equality is recorded but is not required because CABT is not seeded.",
    }


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_json(path: Path, document: Any) -> None:
    path.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _media_type(name: str) -> str:
    if name.endswith(".json"):
        return "application/json"
    if name.endswith(".jsonl"):
        return "application/x-ndjson"
    return "text/markdown"


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
            "schema": PLAN_SCHEMA,
            "match_count": len(evaluation.plan.baseline_positions),
            "baseline_positions": list(evaluation.plan.baseline_positions),
            "replay_match_id": evaluation.plan.replay_match_id,
            "random_seed": None,
            "random_seed_note": "CABT exposes no documented deterministic seed setting.",
        },
    )
    receipt_document = {
        "schema": RECEIPT_SCHEMA,
        **asdict(receipt),
        "dependencies": dict(receipt.dependencies),
        "source": asdict(source),
        "deck": {"name": deck.name, "sha256": deck.sha256, "source": deck.source},
    }
    _write_json(bundle / "run-receipt.json", receipt_document)
    matches_text = "".join(
        json.dumps(document, sort_keys=True) + "\n" for document in evaluation.to_match_documents()
    )
    (bundle / "matches.jsonl").write_text(matches_text, encoding="utf-8")
    _write_json(bundle / "summary.json", evaluation.to_summary_document())
    replay = next((match.replay for match in evaluation.matches if match.replay is not None), None)
    if replay is None:
        raise ValueError("An Artifact Bundle requires one representative replay")
    _write_json(bundle / "replay.json", replay)
    (bundle / "interpretation.md").write_text(interpretation, encoding="utf-8")
    (bundle / "limitations.md").write_text(limitations, encoding="utf-8")

    inventory = [
        {
            "path": name,
            "schema": CONTENT_SCHEMAS[name],
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
        "dependencies": dict(receipt.dependencies),
        "source": asdict(source),
        "workflow": {
            "run_id": receipt.run_id,
            "url": receipt.workflow_url,
            "status": receipt.status,
        },
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


def _read_json(path: Path, label: str, errors: list[str]) -> Any | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as error:
        errors.append(f"{label} is not readable JSON: {error}")
        return None


def _read_matches(path: Path, errors: list[str]) -> list[dict[str, Any]]:
    matches: list[dict[str, Any]] = []
    try:
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            try:
                document = json.loads(line)
            except json.JSONDecodeError as error:
                errors.append(f"matches.jsonl line {line_number} is invalid JSON: {error}")
                continue
            if not isinstance(document, dict):
                errors.append(f"matches.jsonl line {line_number} is not an object")
                continue
            matches.append(document)
    except OSError as error:
        errors.append(f"matches.jsonl is unreadable: {error}")
    return matches


def _expected_outcome(match: Mapping[str, Any]) -> str | None:
    rewards = match.get("rewards")
    position = match.get("baseline_position")
    if (
        not isinstance(rewards, list)
        or len(rewards) != 2
        or not all(isinstance(value, (int, float)) for value in rewards)
        or position not in {0, 1}
    ):
        return None
    baseline_reward = rewards[position]
    control_reward = rewards[1 - position]
    if baseline_reward > control_reward:
        return "win"
    if baseline_reward < control_reward:
        return "loss"
    return "draw"


def _verify_relationships(
    *,
    bundle: Path,
    manifest: Mapping[str, Any],
    receipt: Mapping[str, Any],
    summary: Mapping[str, Any],
    plan: Mapping[str, Any],
    deck: Mapping[str, Any],
    matches: list[dict[str, Any]],
    errors: list[str],
) -> None:
    if receipt.get("schema") != RECEIPT_SCHEMA:
        errors.append("run-receipt.json has an unsupported schema")
    if summary.get("schema") != SUMMARY_SCHEMA:
        errors.append("summary.json has an unsupported schema")
    if plan.get("schema") != PLAN_SCHEMA:
        errors.append("evaluation-plan.json has an unsupported schema")
    if deck.get("schema") != CONTENT_SCHEMAS["reference-deck.json"]:
        errors.append("reference-deck.json has an unsupported schema")
    if manifest.get("code_revision") != receipt.get("code_revision"):
        errors.append("Code revision relationship does not match the Run Receipt")
    if manifest.get("source") != receipt.get("source"):
        errors.append("Authoritative Source relationship does not match the Run Receipt")
    if manifest.get("dependencies") != receipt.get("dependencies"):
        errors.append("Dependency versions do not match the Run Receipt")
    workflow = manifest.get("workflow", {})
    if not isinstance(workflow, dict) or workflow.get("status") != "succeeded":
        errors.append("Artifact Manifest does not record a successful Workflow Run")
    if receipt.get("status") != "succeeded":
        errors.append("Run Receipt does not record a successful Workflow Run")

    configuration = manifest.get("configuration", {})
    if not isinstance(configuration, dict):
        errors.append("Artifact Manifest configuration is not an object")
        configuration = {}
    deck_hash = _sha256(bundle / "reference-deck.json")
    if configuration.get("deck_sha256") != deck_hash:
        errors.append("Reference Deck hash does not match the Artifact Manifest")
    receipt_deck = receipt.get("deck", {})
    if not isinstance(receipt_deck, dict) or receipt_deck.get("sha256") != deck_hash:
        errors.append("Reference Deck hash does not match the Run Receipt")

    positions = plan.get("baseline_positions")
    if not isinstance(positions, list) or any(position not in {0, 1} for position in positions):
        errors.append("Evaluation Plan baseline_positions is invalid")
        positions = []
    position_counts = {"0": positions.count(0), "1": positions.count(1)}
    match_count = len(matches)
    declared_counts = {
        plan.get("match_count"),
        summary.get("match_count"),
        configuration.get("match_count"),
        len(positions),
        match_count,
    }
    if declared_counts != {20}:
        errors.append("September Evaluation must contain exactly 20 consistently declared matches")
    if position_counts != {"0": 10, "1": 10}:
        errors.append("Evaluation Plan must assign 10 matches to each baseline position")
    if configuration.get("baseline_matches_by_position") != position_counts:
        errors.append("Baseline position configuration does not match the Evaluation Plan")
    if [match.get("match_id") for match in matches] != list(range(1, match_count + 1)):
        errors.append("Match IDs must be contiguous and ordered from 1")
    if [match.get("baseline_position") for match in matches] != positions:
        errors.append("Match positions do not match the Evaluation Plan")

    outcomes_by_position: dict[str, dict[str, int]] = {}
    for position in (0, 1):
        outcomes = Counter(
            match.get("outcome") for match in matches if match.get("baseline_position") == position
        )
        outcomes_by_position[str(position)] = {
            "wins": outcomes["win"],
            "losses": outcomes["loss"],
            "draws": outcomes["draw"],
        }
    terminations = Counter(match.get("termination") for match in matches)
    for match in matches:
        if match.get("schema") != MATCH_SCHEMA:
            errors.append(f"Match {match.get('match_id')} has an unsupported schema")
        expected_outcome = _expected_outcome(match)
        if expected_outcome is None or match.get("outcome") != expected_outcome:
            errors.append(f"Match {match.get('match_id')} outcome does not match its rewards")
        statuses = match.get("statuses")
        if match.get("termination") != "completed" or statuses != ["DONE", "DONE"]:
            errors.append(f"Match {match.get('match_id')} did not complete cleanly")
    if summary.get("by_baseline_position") != outcomes_by_position:
        errors.append("Evaluation summary outcomes do not match matches.jsonl")
    if summary.get("terminations") != dict(terminations):
        errors.append("Evaluation summary terminations do not match matches.jsonl")
    if summary.get("completed_matches") != terminations["completed"]:
        errors.append("Completed match count does not match matches.jsonl")
    if summary.get("invalid_or_error_matches") != match_count - terminations["completed"]:
        errors.append("Invalid or error match count does not match matches.jsonl")
    if not summary.get("accepted") or terminations != Counter({"completed": 20}):
        errors.append("Evaluation summary does not satisfy September acceptance")


def _verify_bundle(bundle: Path, *, require_integrity: bool) -> IntegrityResult:
    errors: list[str] = []
    if not bundle.is_dir():
        return IntegrityResult(False, 0, (f"Bundle directory does not exist: {bundle}",), "")
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
    manifest = _read_json(manifest_path, "manifest.json", errors)
    if not isinstance(manifest, dict):
        return IntegrityResult(False, 0, tuple(errors), manifest_hash)
    if manifest.get("schema") != BUNDLE_SCHEMA:
        errors.append("manifest.json has an unsupported schema")
    if set(manifest.get("required_files", [])) != set(REQUIRED_BUNDLE_FILES):
        errors.append("manifest.json required_files does not match the Bundle contract")

    entries = manifest.get("files", [])
    if not isinstance(entries, list):
        errors.append("manifest.json file inventory is not a list")
        entries = []
    entry_names = {entry.get("path") for entry in entries if isinstance(entry, dict)}
    if entry_names != set(CONTENT_FILES):
        errors.append("manifest.json file inventory does not match the Bundle contract")
    checked = 0
    for entry in entries:
        if not isinstance(entry, dict):
            errors.append("manifest.json contains an invalid file entry")
            continue
        name = entry.get("path")
        if not isinstance(name, str) or Path(name).name != name:
            errors.append("manifest.json contains an unsafe file path")
            continue
        if entry.get("schema") != CONTENT_SCHEMAS.get(name):
            errors.append(f"{name} schema declaration does not match the Bundle contract")
        artifact = bundle / name
        if not artifact.is_file():
            continue
        checked += 1
        if _sha256(artifact) != entry.get("sha256"):
            errors.append(f"{name} SHA-256 mismatch")
        if artifact.stat().st_size != entry.get("bytes"):
            errors.append(f"{name} byte-size mismatch")
        if _media_type(name) != entry.get("media_type"):
            errors.append(f"{name} media type does not match the Bundle contract")

    receipt = _read_json(bundle / "run-receipt.json", "run-receipt.json", errors)
    summary = _read_json(bundle / "summary.json", "summary.json", errors)
    plan = _read_json(bundle / "evaluation-plan.json", "evaluation-plan.json", errors)
    deck = _read_json(bundle / "reference-deck.json", "reference-deck.json", errors)
    replay = _read_json(bundle / "replay.json", "replay.json", errors)
    matches = _read_matches(bundle / "matches.jsonl", errors)
    if not isinstance(replay, dict):
        errors.append("replay.json must contain a replay object")
    if all(isinstance(document, dict) for document in (receipt, summary, plan, deck)):
        _verify_relationships(
            bundle=bundle,
            manifest=manifest,
            receipt=receipt,
            summary=summary,
            plan=plan,
            deck=deck,
            matches=matches,
            errors=errors,
        )

    if require_integrity and (bundle / "integrity.json").is_file():
        report = _read_json(bundle / "integrity.json", "integrity.json", errors)
        if isinstance(report, dict):
            if report.get("schema") != INTEGRITY_SCHEMA:
                errors.append("integrity.json has an unsupported schema")
            if report.get("manifest_sha256") != manifest_hash:
                errors.append("integrity.json does not refer to the current manifest")
            if report.get("valid") is not True or report.get("errors") != []:
                errors.append("integrity.json does not record a valid bundle")
            if report.get("checked_files") != len(CONTENT_FILES):
                errors.append("integrity.json checked_files does not match the Bundle contract")

    return IntegrityResult(not errors, checked, tuple(errors), manifest_hash)
