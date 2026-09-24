import hashlib
import json
from pathlib import Path

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


def test_artifact_bundle_is_complete_and_detects_tampering(tmp_path):
    source_path = Path("data/pokemon-tcg-ai-battle-challenge-strategy/EN Card Data.csv")
    catalog = load_catalog(source_path)
    deck_path = Path("config/reference-deck.json")
    deck = load_deck(deck_path, catalog)
    simulations = [
        SimulationResult(
            rewards=(1.0, -1.0),
            statuses=("DONE", "DONE"),
            termination="completed",
            step_count=20,
            replay={"schema_version": 1, "steps": []} if match_id == 1 else None,
        )
        for match_id in range(1, 21)
    ]
    evaluation = run_evaluation(
        EvaluationPlan.balanced(match_count=20),
        InMemoryBattleAdapter(simulations),
        deck=deck.card_ids,
    )
    receipt = RunReceipt(
        run_id="test-run-001",
        status="succeeded",
        started_at="2026-09-24T14:00:00Z",
        finished_at="2026-09-24T14:01:00Z",
        code_revision="0123456789abcdef",
        environment="test",
        workflow_url="https://example.test/actions/runs/1",
        command="fall-ai-studio evaluate --matches 20",
        dependencies={"kaggle-environments": "1.32.7", "python": "3.11.13"},
    )
    bundle = tmp_path / "september-baseline-v1"

    assemble_bundle(
        bundle,
        evaluation=evaluation,
        source=catalog.source,
        deck=deck,
        deck_path=deck_path,
        receipt=receipt,
        interpretation="The results are descriptive, not a competitive benchmark.\n",
        limitations="CABT does not expose a documented deterministic seed.\n",
    )

    assert verify_bundle(bundle).valid
    manifest = json.loads((bundle / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["dependencies"] == receipt.dependencies
    assert {entry["path"]: entry["schema"] for entry in manifest["files"]} == {
        name: CONTENT_SCHEMAS[name] for name in CONTENT_FILES
    }

    matches_path = bundle / "matches.jsonl"
    matches = matches_path.read_text(encoding="utf-8").splitlines()
    first_match = json.loads(matches[0])
    first_match["outcome"] = "loss"
    matches[0] = json.dumps(first_match, sort_keys=True)
    matches_path.write_text("\n".join(matches) + "\n", encoding="utf-8")
    _reseal(bundle, "matches.jsonl")
    tampered = verify_bundle(bundle)
    assert not tampered.valid
    assert any("outcome does not match its rewards" in error for error in tampered.errors)
    assert any("summary outcomes do not match" in error for error in tampered.errors)
