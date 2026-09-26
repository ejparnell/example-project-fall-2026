"""Create and independently verify complete Artifact Bundles."""

from __future__ import annotations

import hashlib
import json
import math
import re
import shutil
import sys
import tempfile
from collections import Counter
from collections.abc import Mapping
from dataclasses import asdict, dataclass
from importlib import metadata
from pathlib import Path
from typing import Any

from fall_ai_studio.battle import EvaluationResult
from fall_ai_studio.catalog import (
    AUTHORITATIVE_SOURCE_CARD_COUNT,
    AUTHORITATIVE_SOURCE_PATH,
    AUTHORITATIVE_SOURCE_ROW_COUNT,
    AUTHORITATIVE_SOURCE_SHA256,
    REFERENCE_DECK_SHA256,
    Deck,
    SourceReceipt,
)

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
    "replay.json": "fall-ai-studio/cabt-replay/v1",
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


def summary_document(evaluation: EvaluationResult) -> dict[str, Any]:
    """Serialize a Battle result using the Evidence-owned summary schema."""

    return {
        "schema": SUMMARY_SCHEMA,
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


def match_documents(evaluation: EvaluationResult) -> tuple[dict[str, Any], ...]:
    """Serialize replay-free match evidence without traversing simulator objects."""

    return tuple(
        {
            "schema": MATCH_SCHEMA,
            "match_id": match.match_id,
            "baseline_position": match.baseline_position,
            "outcome": match.outcome,
            "rewards": list(match.rewards),
            "statuses": list(match.statuses),
            "termination": match.termination,
            "step_count": match.step_count,
        }
        for match in evaluation.matches
    )


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
        for document in match_documents(evaluation)
    ]
    events.append(
        json.dumps(
            {"event": "evaluation_completed", **summary_document(evaluation)}, sort_keys=True
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
    receipt: RunReceipt,
) -> dict[str, Any]:
    """Build a provenance-complete receipt for the second Workflow Run."""

    rerun_summary = summary_document(rerun)
    return {
        "schema": VERIFICATION_SCHEMA,
        **asdict(receipt),
        "dependencies": dict(receipt.dependencies),
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
    """Stage, verify, and atomically publish a complete Artifact Bundle."""

    destination_path = Path(destination)
    if destination_path.exists() or destination_path.is_symlink():
        raise FileExistsError(f"Artifact Bundle destination already exists: {destination_path}")
    destination_path.parent.mkdir(parents=True, exist_ok=True)
    staging_root = Path(tempfile.mkdtemp(prefix=".artifact-bundle.", dir=destination_path.parent))
    staging_path = staging_root / destination_path.name
    try:
        _assemble_bundle_contents(
            staging_path,
            bundle_id=destination_path.name,
            evaluation=evaluation,
            source=source,
            deck=deck,
            deck_path=deck_path,
            receipt=receipt,
            interpretation=interpretation,
            limitations=limitations,
        )
        staging_path.replace(destination_path)
        staging_root.rmdir()
    except BaseException:
        shutil.rmtree(staging_root, ignore_errors=True)
        raise
    return destination_path


def _assemble_bundle_contents(
    destination: str | Path,
    *,
    bundle_id: str,
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
        json.dumps(document, sort_keys=True) + "\n" for document in match_documents(evaluation)
    )
    (bundle / "matches.jsonl").write_text(matches_text, encoding="utf-8")
    _write_json(bundle / "summary.json", summary_document(evaluation))
    replay_match = next((match for match in evaluation.matches if match.replay is not None), None)
    if replay_match is None:
        raise ValueError("An Artifact Bundle requires one representative replay")
    _write_json(
        bundle / "replay.json",
        {
            "schema": CONTENT_SCHEMAS["replay.json"],
            "match_id": replay_match.match_id,
            "baseline_position": replay_match.baseline_position,
            "replay": replay_match.replay,
        },
    )
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
        "bundle_id": bundle_id,
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
    if path.is_symlink():
        errors.append(f"{label} must not be a symbolic link")
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError, UnicodeError) as error:
        errors.append(f"{label} is not readable JSON: {error}")
        return None


def _read_matches(path: Path, errors: list[str]) -> list[dict[str, Any]]:
    matches: list[dict[str, Any]] = []
    if path.is_symlink():
        errors.append("matches.jsonl must not be a symbolic link")
        return matches
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
    except (OSError, UnicodeError) as error:
        errors.append(f"matches.jsonl is unreadable: {error}")
    return matches


def _expected_outcome(match: Mapping[str, Any]) -> str | None:
    rewards = match.get("rewards")
    position = match.get("baseline_position")
    if (
        not isinstance(rewards, list)
        or len(rewards) != 2
        or not all(type(value) in {int, float} and math.isfinite(value) for value in rewards)
        or type(position) is not int
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
    replay: Mapping[str, Any],
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
    code_revision = receipt.get("code_revision")
    if not isinstance(code_revision, str) or re.fullmatch(r"[0-9a-f]{40}", code_revision) is None:
        errors.append("Run Receipt code revision must be a full lowercase commit SHA")
    if manifest.get("bundle_id") != bundle.name:
        errors.append("Artifact Manifest bundle_id does not match its directory")
    if manifest.get("created_at") != receipt.get("finished_at"):
        errors.append("Artifact Manifest creation time does not match the Run Receipt")
    if manifest.get("source") != receipt.get("source"):
        errors.append("Authoritative Source relationship does not match the Run Receipt")
    expected_source = {
        "path": AUTHORITATIVE_SOURCE_PATH,
        "sha256": AUTHORITATIVE_SOURCE_SHA256,
        "row_count": AUTHORITATIVE_SOURCE_ROW_COUNT,
        "card_count": AUTHORITATIVE_SOURCE_CARD_COUNT,
    }
    if receipt.get("source") != expected_source:
        errors.append("Authoritative Source contract is not the frozen September source")
    if manifest.get("dependencies") != receipt.get("dependencies"):
        errors.append("Dependency versions do not match the Run Receipt")
    dependencies = receipt.get("dependencies")
    if (
        not isinstance(dependencies, dict)
        or dependencies.get("kaggle-environments") != "1.32.7"
        or dependencies.get("fall-ai-studio-pokemon") != "0.1.0"
        or not isinstance(dependencies.get("python"), str)
        or not dependencies["python"].startswith("3.11.")
    ):
        errors.append("Run Receipt dependency versions do not match the September contract")
    workflow = manifest.get("workflow", {})
    expected_workflow = {
        "run_id": receipt.get("run_id"),
        "url": receipt.get("workflow_url"),
        "status": receipt.get("status"),
    }
    if workflow != expected_workflow:
        errors.append("Workflow Run relationship does not match the Run Receipt")
    if not isinstance(workflow, dict) or workflow.get("status") != "succeeded":
        errors.append("Artifact Manifest does not record a successful Workflow Run")
    if receipt.get("status") != "succeeded":
        errors.append("Run Receipt does not record a successful Workflow Run")
    workflow_url = receipt.get("workflow_url")
    run_id = receipt.get("run_id")
    if (
        receipt.get("environment") != "github-actions/linux"
        or receipt.get("command") != "fall-ai-studio acceptance-run --matches 20"
        or not isinstance(run_id, str)
        or not run_id.isdigit()
        or workflow_url
        != f"https://github.com/ejparnell/example-project-fall-2026/actions/runs/{run_id}"
    ):
        errors.append("Run Receipt is not canonical GitHub Actions acceptance provenance")

    configuration = manifest.get("configuration", {})
    if not isinstance(configuration, dict):
        errors.append("Artifact Manifest configuration is not an object")
        configuration = {}
    deck_hash = _sha256(bundle / "reference-deck.json")
    if deck_hash != REFERENCE_DECK_SHA256:
        errors.append("Reference Deck is not the frozen official September deck")
    if configuration.get("deck_sha256") != deck_hash:
        errors.append("Reference Deck hash does not match the Artifact Manifest")
    receipt_deck = receipt.get("deck", {})
    expected_receipt_deck = {
        "name": deck.get("name"),
        "sha256": deck_hash,
        "source": deck.get("source"),
    }
    if receipt_deck != expected_receipt_deck:
        errors.append("Reference Deck hash does not match the Run Receipt")
    if plan.get("random_seed") is not None or configuration.get("random_seed") is not None:
        errors.append("September Evaluation must retain the documented unseeded configuration")

    positions = plan.get("baseline_positions")
    if not isinstance(positions, list) or any(
        type(position) is not int or position not in {0, 1} for position in positions
    ):
        errors.append("Evaluation Plan baseline_positions is invalid")
        positions = []
    position_counts = {"0": positions.count(0), "1": positions.count(1)}
    match_count = len(matches)
    declared_counts = (
        plan.get("match_count"),
        summary.get("match_count"),
        configuration.get("match_count"),
        len(positions),
        match_count,
    )
    if any(type(count) is not int or count != 20 for count in declared_counts):
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
            outcome
            for match in matches
            if match.get("baseline_position") == position
            and isinstance((outcome := match.get("outcome")), str)
            and outcome in {"win", "loss", "draw"}
        )
        outcomes_by_position[str(position)] = {
            "wins": outcomes["win"],
            "losses": outcomes["loss"],
            "draws": outcomes["draw"],
        }
    terminations = Counter(
        termination
        for match in matches
        if isinstance((termination := match.get("termination")), str)
    )
    for match in matches:
        if match.get("schema") != MATCH_SCHEMA:
            errors.append(f"Match {match.get('match_id')} has an unsupported schema")
        if type(match.get("match_id")) is not int or match.get("match_id", 0) <= 0:
            errors.append("Match ID must be a positive integer")
        if type(match.get("baseline_position")) is not int:
            errors.append(f"Match {match.get('match_id')} position must be an integer")
        if type(match.get("step_count")) is not int or match.get("step_count", 0) <= 0:
            errors.append(f"Match {match.get('match_id')} step_count must be a positive integer")
        expected_outcome = _expected_outcome(match)
        if expected_outcome is None or match.get("outcome") != expected_outcome:
            errors.append(f"Match {match.get('match_id')} outcome does not match its rewards")
        statuses = match.get("statuses")
        if match.get("termination") != "completed" or statuses != ["DONE", "DONE"]:
            errors.append(f"Match {match.get('match_id')} did not complete cleanly")
    if summary.get("by_baseline_position") != outcomes_by_position:
        errors.append("Evaluation summary outcomes do not match matches.jsonl")
    summary_counts = (
        summary.get("match_count"),
        summary.get("completed_matches"),
        summary.get("invalid_or_error_matches"),
    )
    if any(type(count) is not int or count < 0 for count in summary_counts):
        errors.append("Evaluation summary counts must be non-negative integers")
    summary_positions = summary.get("by_baseline_position")
    if not isinstance(summary_positions, dict) or any(
        not isinstance(position_summary, dict)
        or any(
            type(position_summary.get(field)) is not int or position_summary.get(field, -1) < 0
            for field in ("wins", "losses", "draws")
        )
        for position_summary in summary_positions.values()
    ):
        errors.append("Evaluation position summaries must contain non-negative integer counts")
    summary_terminations = summary.get("terminations")
    if not isinstance(summary_terminations, dict) or any(
        not isinstance(name, str) or type(count) is not int or count < 0
        for name, count in summary_terminations.items()
    ):
        errors.append("Evaluation termination counts must be non-negative integers")
    if summary.get("terminations") != dict(terminations):
        errors.append("Evaluation summary terminations do not match matches.jsonl")
    if summary.get("completed_matches") != terminations["completed"]:
        errors.append("Completed match count does not match matches.jsonl")
    if summary.get("invalid_or_error_matches") != match_count - terminations["completed"]:
        errors.append("Invalid or error match count does not match matches.jsonl")
    if summary.get("accepted") is not True or terminations != Counter({"completed": 20}):
        errors.append("Evaluation summary does not satisfy September acceptance")

    replay_match_id = plan.get("replay_match_id")
    replay_match = next(
        (match for match in matches if match.get("match_id") == replay_match_id), None
    )
    replay_payload = replay.get("replay")
    if (
        replay.get("schema") != CONTENT_SCHEMAS["replay.json"]
        or type(replay_match_id) is not int
        or type(replay.get("match_id")) is not int
        or replay.get("match_id") != replay_match_id
        or replay_match is None
        or type(replay.get("baseline_position")) is not int
        or replay.get("baseline_position") != replay_match.get("baseline_position")
        or not isinstance(replay_payload, dict)
        or replay_payload.get("name") != "cabt"
        or type(replay_payload.get("schema_version")) is not int
        or replay_payload.get("schema_version") != 1
        or replay_payload.get("statuses") != ["DONE", "DONE"]
        or not isinstance(replay_payload.get("rewards"), list)
        or not all(
            type(value) in {int, float} and math.isfinite(value)
            for value in replay_payload.get("rewards", [])
        )
        or replay_payload.get("rewards") != replay_match.get("rewards")
        or not isinstance(replay_payload.get("steps"), list)
        or not replay_payload.get("steps")
        or len(replay_payload.get("steps", [])) != replay_match.get("step_count")
    ):
        errors.append("Representative Replay does not match its planned completed CABT match")


def _verify_bundle(bundle: Path, *, require_integrity: bool) -> IntegrityResult:
    errors: list[str] = []
    if bundle.is_symlink() or not bundle.is_dir():
        return IntegrityResult(False, 0, (f"Bundle directory does not exist: {bundle}",), "")
    children = list(bundle.iterdir())
    for child in children:
        if child.is_symlink():
            errors.append(f"Bundle entry must not be a symbolic link: {child.name}")
        elif not child.is_file():
            errors.append(f"Undeclared non-file entry: {child.name}")
    manifest_path = bundle / "manifest.json"
    manifest_hash = (
        _sha256(manifest_path) if manifest_path.is_file() and not manifest_path.is_symlink() else ""
    )
    actual_files = {path.name for path in children if path.is_file() and not path.is_symlink()}
    expected_files = set(REQUIRED_BUNDLE_FILES)
    if not require_integrity:
        expected_files.remove("integrity.json")
    for missing in sorted(expected_files - actual_files):
        errors.append(f"Missing required file: {missing}")
    for extra in sorted(actual_files - set(REQUIRED_BUNDLE_FILES)):
        errors.append(f"Undeclared file: {extra}")

    if not manifest_path.is_file() or manifest_path.is_symlink():
        return IntegrityResult(False, 0, tuple(errors), manifest_hash)
    manifest = _read_json(manifest_path, "manifest.json", errors)
    if not isinstance(manifest, dict):
        return IntegrityResult(False, 0, tuple(errors), manifest_hash)
    if manifest.get("schema") != BUNDLE_SCHEMA:
        errors.append("manifest.json has an unsupported schema")
    required_files = manifest.get("required_files")
    if (
        not isinstance(required_files, list)
        or not all(isinstance(name, str) for name in required_files)
        or len(required_files) != len(REQUIRED_BUNDLE_FILES)
        or len(set(required_files)) != len(required_files)
        or set(required_files) != set(REQUIRED_BUNDLE_FILES)
    ):
        errors.append(
            "manifest.json required_files contains duplicates or does not match the Bundle contract"
        )

    entries = manifest.get("files", [])
    if not isinstance(entries, list):
        errors.append("manifest.json file inventory is not a list")
        entries = []
    entry_names = {
        name
        for entry in entries
        if isinstance(entry, dict) and isinstance((name := entry.get("path")), str)
    }
    if (
        len(entries) != len(CONTENT_FILES)
        or len(entry_names) != len(entries)
        or entry_names != set(CONTENT_FILES)
    ):
        errors.append(
            "manifest.json file inventory contains duplicate paths or does not match the Bundle "
            "contract"
        )
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
        if artifact.is_symlink() or not artifact.is_file():
            continue
        checked += 1
        if _sha256(artifact) != entry.get("sha256"):
            errors.append(f"{name} SHA-256 mismatch")
        if artifact.stat().st_size != entry.get("bytes"):
            errors.append(f"{name} byte-size mismatch")
        if _media_type(name) != entry.get("media_type"):
            errors.append(f"{name} media type does not match the Bundle contract")
    if checked != len(CONTENT_FILES):
        errors.append("Recomputed checked-file count does not match the Bundle contract")

    receipt = _read_json(bundle / "run-receipt.json", "run-receipt.json", errors)
    summary = _read_json(bundle / "summary.json", "summary.json", errors)
    plan = _read_json(bundle / "evaluation-plan.json", "evaluation-plan.json", errors)
    deck = _read_json(bundle / "reference-deck.json", "reference-deck.json", errors)
    replay = _read_json(bundle / "replay.json", "replay.json", errors)
    matches = _read_matches(bundle / "matches.jsonl", errors)
    if not isinstance(replay, dict):
        errors.append("replay.json must contain a Representative Replay object")
    if all(isinstance(document, dict) for document in (receipt, summary, plan, deck, replay)):
        _verify_relationships(
            bundle=bundle,
            manifest=manifest,
            receipt=receipt,
            summary=summary,
            plan=plan,
            deck=deck,
            replay=replay,
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
            if report.get("checked_files") != checked or checked != len(CONTENT_FILES):
                errors.append("integrity.json checked_files does not match the Bundle contract")

    return IntegrityResult(not errors, checked, tuple(errors), manifest_hash)
