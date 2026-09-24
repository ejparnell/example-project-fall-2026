import hashlib
import json
from pathlib import Path

import pytest

from fall_ai_studio.battle import (
    EvaluationPlan,
    InMemoryBattleAdapter,
    SimulationResult,
    run_evaluation,
)
from fall_ai_studio.catalog import load_catalog, load_deck
from fall_ai_studio.evidence import (
    CONTENT_FILES,
    CONTENT_SCHEMAS,
    RunReceipt,
    assemble_bundle,
    verify_bundle,
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _reseal(bundle: Path, changed_name: str) -> None:
    manifest_path = bundle / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    entry = next(item for item in manifest["files"] if item["path"] == changed_name)
    entry["sha256"] = _sha256(bundle / changed_name)
    entry["bytes"] = (bundle / changed_name).stat().st_size
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    integrity_path = bundle / "integrity.json"
    integrity = json.loads(integrity_path.read_text(encoding="utf-8"))
    integrity["manifest_sha256"] = _sha256(manifest_path)
    integrity_path.write_text(
        json.dumps(integrity, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


class FragileReplay(dict):
    """Behave like Kaggle's Struct-backed replay during dataclass conversion."""

    def __init__(self) -> None:
        super().__init__()


@pytest.fixture
def bundle(tmp_path):
    source_path = Path("data/pokemon-tcg-ai-battle-challenge-strategy/EN Card Data.csv")
    catalog = load_catalog(source_path)
    deck_path = Path("config/reference-deck.json")
    deck = load_deck(deck_path, catalog)
    replay = FragileReplay()
    replay.update(
        {
            "name": "cabt",
            "schema_version": 1,
            "statuses": ["DONE", "DONE"],
            "rewards": [1.0, -1.0],
            "steps": [[{"status": "DONE"}, {"status": "DONE"}]] * 20,
        }
    )
    simulations = [
        SimulationResult(
            rewards=(1.0, -1.0),
            statuses=("DONE", "DONE"),
            termination="completed",
            step_count=20,
            replay=replay if match_id == 1 else None,
        )
        for match_id in range(1, 21)
    ]
    evaluation = run_evaluation(
        EvaluationPlan.balanced(match_count=20),
        InMemoryBattleAdapter(simulations),
        deck=deck.card_ids,
    )
    receipt = RunReceipt(
        run_id="1",
        status="succeeded",
        started_at="2026-09-24T14:00:00Z",
        finished_at="2026-09-24T14:01:00Z",
        code_revision="0123456789abcdef0123456789abcdef01234567",
        environment="github-actions/linux",
        workflow_url=("https://github.com/ejparnell/example-project-fall-2026/actions/runs/1"),
        command="fall-ai-studio acceptance-run --matches 20",
        dependencies={
            "fall-ai-studio-pokemon": "0.1.0",
            "kaggle-environments": "1.32.7",
            "python": "3.11.13",
        },
    )
    destination = tmp_path / "september-baseline-v1"
    assemble_bundle(
        destination,
        evaluation=evaluation,
        source=catalog.source,
        deck=deck,
        deck_path=deck_path,
        receipt=receipt,
        interpretation="The results are descriptive, not a competitive benchmark.\n",
        limitations="CABT does not expose a documented deterministic seed.\n",
    )
    return destination, receipt


def test_artifact_bundle_is_complete_and_detects_tampering(bundle):
    bundle_path, receipt = bundle
    assert verify_bundle(bundle_path).valid
    manifest = json.loads((bundle_path / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["dependencies"] == receipt.dependencies
    assert {entry["path"]: entry["schema"] for entry in manifest["files"]} == {
        name: CONTENT_SCHEMAS[name] for name in CONTENT_FILES
    }

    matches_path = bundle_path / "matches.jsonl"
    matches = matches_path.read_text(encoding="utf-8").splitlines()
    first_match = json.loads(matches[0])
    first_match["outcome"] = "loss"
    matches[0] = json.dumps(first_match, sort_keys=True)
    matches_path.write_text("\n".join(matches) + "\n", encoding="utf-8")
    _reseal(bundle_path, "matches.jsonl")
    tampered = verify_bundle(bundle_path)
    assert not tampered.valid
    assert any("outcome does not match its rewards" in error for error in tampered.errors)
    assert any("summary outcomes do not match" in error for error in tampered.errors)


def test_bundle_rejects_resealed_false_source_and_workflow_provenance(bundle):
    bundle_path, _ = bundle
    receipt_path = bundle_path / "run-receipt.json"
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    receipt["source"]["path"] = "wrong.csv"
    receipt["source"]["sha256"] = "0" * 64
    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    manifest_path = bundle_path / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["source"] = receipt["source"]
    manifest["workflow"]["run_id"] = "different-run"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    _reseal(bundle_path, "run-receipt.json")

    integrity = verify_bundle(bundle_path)
    assert not integrity.valid
    assert any("Authoritative Source contract" in error for error in integrity.errors)
    assert any("Workflow Run relationship" in error for error in integrity.errors)


def test_bundle_rejects_resealed_invalid_replay(bundle):
    bundle_path, _ = bundle
    replay_path = bundle_path / "replay.json"
    replay_path.write_text("{}\n", encoding="utf-8")
    _reseal(bundle_path, "replay.json")

    integrity = verify_bundle(bundle_path)
    assert not integrity.valid
    assert any("Representative Replay" in error for error in integrity.errors)


def test_bundle_rejects_resealed_non_reference_deck(bundle):
    bundle_path, _ = bundle
    deck_path = bundle_path / "reference-deck.json"
    deck = json.loads(deck_path.read_text(encoding="utf-8"))
    deck["cards"] = [deck["cards"][0]] * 60
    deck_path.write_text(json.dumps(deck, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    false_hash = _sha256(deck_path)

    receipt_path = bundle_path / "run-receipt.json"
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    receipt["deck"]["sha256"] = false_hash
    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    manifest_path = bundle_path / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["configuration"]["deck_sha256"] = false_hash
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    _reseal(bundle_path, "reference-deck.json")
    _reseal(bundle_path, "run-receipt.json")

    integrity = verify_bundle(bundle_path)
    assert not integrity.valid
    assert any("frozen official September deck" in error for error in integrity.errors)


@pytest.mark.parametrize(
    ("filename", "mutate"),
    [
        ("summary.json", lambda document: document.update({"accepted": "yes"})),
        ("matches.jsonl", lambda document: document.update({"step_count": "unknown"})),
        ("matches.jsonl", lambda document: document.update({"rewards": [True, False]})),
    ],
)
def test_bundle_rejects_wrong_evidence_types(bundle, filename, mutate):
    bundle_path, _ = bundle
    path = bundle_path / filename
    if filename.endswith(".jsonl"):
        lines = path.read_text(encoding="utf-8").splitlines()
        document = json.loads(lines[0])
        mutate(document)
        lines[0] = json.dumps(document, sort_keys=True)
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    else:
        document = json.loads(path.read_text(encoding="utf-8"))
        mutate(document)
        path.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    _reseal(bundle_path, filename)
    assert not verify_bundle(bundle_path).valid


def test_bundle_rejects_claimed_seed_and_replay_length_mismatch(bundle):
    bundle_path, _ = bundle
    plan_path = bundle_path / "evaluation-plan.json"
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    plan["random_seed"] = 42
    plan_path.write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    manifest_path = bundle_path / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["configuration"]["random_seed"] = 42
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    _reseal(bundle_path, "evaluation-plan.json")
    replay_path = bundle_path / "replay.json"
    replay = json.loads(replay_path.read_text(encoding="utf-8"))
    replay["replay"]["steps"] = replay["replay"]["steps"][:-1]
    replay_path.write_text(json.dumps(replay, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    _reseal(bundle_path, "replay.json")

    integrity = verify_bundle(bundle_path)
    assert not integrity.valid
    assert any("unseeded" in error for error in integrity.errors)
    assert any("Representative Replay" in error for error in integrity.errors)


@pytest.mark.parametrize("filename", ["summary.json", "matches.jsonl"])
def test_invalid_utf8_returns_integrity_error(bundle, filename):
    bundle_path, _ = bundle
    (bundle_path / filename).write_bytes(b"\xff\xfe")
    integrity = verify_bundle(bundle_path)
    assert not integrity.valid
    assert any(filename in error for error in integrity.errors)


def test_bundle_rejects_duplicate_manifest_entries(bundle):
    bundle_path, _ = bundle
    manifest_path = bundle_path / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["required_files"].append(manifest["required_files"][0])
    manifest["files"].append(manifest["files"][0])
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    integrity_path = bundle_path / "integrity.json"
    integrity_report = json.loads(integrity_path.read_text(encoding="utf-8"))
    integrity_report["manifest_sha256"] = _sha256(manifest_path)
    integrity_path.write_text(
        json.dumps(integrity_report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    integrity = verify_bundle(bundle_path)
    assert not integrity.valid
    assert integrity.checked_files == 9
    assert any("duplicate" in error for error in integrity.errors)


def test_failed_assembly_leaves_no_partial_destination(bundle, tmp_path):
    _, receipt = bundle
    catalog = load_catalog(Path("data/pokemon-tcg-ai-battle-challenge-strategy/EN Card Data.csv"))
    deck_path = Path("config/reference-deck.json")
    deck = load_deck(deck_path, catalog)
    simulations = [
        SimulationResult(
            rewards=(1.0, -1.0),
            statuses=("DONE", "DONE"),
            termination="completed",
            step_count=20,
        )
        for _ in range(20)
    ]
    evaluation = run_evaluation(
        EvaluationPlan.balanced(match_count=20),
        InMemoryBattleAdapter(simulations),
        deck=deck.card_ids,
    )
    destination = tmp_path / "failed-bundle"
    with pytest.raises(ValueError, match="representative replay"):
        assemble_bundle(
            destination,
            evaluation=evaluation,
            source=catalog.source,
            deck=deck,
            deck_path=deck_path,
            receipt=receipt,
            interpretation="Interpretation\n",
            limitations="Limitations\n",
        )
    assert not destination.exists()


@pytest.mark.parametrize(
    ("filename", "mutate"),
    [
        ("manifest.json", lambda document: document.update({"required_files": None})),
        (
            "evaluation-plan.json",
            lambda document: document.update({"baseline_positions": [{}]}),
        ),
    ],
)
def test_malformed_documents_return_integrity_errors(bundle, filename, mutate):
    bundle_path, _ = bundle
    path = bundle_path / filename
    document = json.loads(path.read_text(encoding="utf-8"))
    mutate(document)
    path.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if filename == "manifest.json":
        integrity_path = bundle_path / "integrity.json"
        integrity = json.loads(integrity_path.read_text(encoding="utf-8"))
        integrity["manifest_sha256"] = _sha256(path)
        integrity_path.write_text(
            json.dumps(integrity, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    else:
        _reseal(bundle_path, filename)

    assert not verify_bundle(bundle_path).valid


def test_bundle_rejects_undeclared_directories_and_symlinks(bundle, tmp_path):
    bundle_path, _ = bundle
    (bundle_path / "extra").mkdir()
    assert not verify_bundle(bundle_path).valid
    (bundle_path / "extra").rmdir()
    external = tmp_path / "outside.json"
    external.write_text("{}\n", encoding="utf-8")
    (bundle_path / "replay.json").unlink()
    (bundle_path / "replay.json").symlink_to(external)
    assert not verify_bundle(bundle_path).valid
