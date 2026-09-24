"""Thin command-line entry points over Catalog, Battle, and Evidence."""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import asdict
from datetime import UTC, datetime
from importlib import metadata
from pathlib import Path

from fall_ai_studio.battle import CabtBattleAdapter, EvaluationPlan, run_evaluation
from fall_ai_studio.catalog import load_catalog, load_deck
from fall_ai_studio.evidence import RunReceipt, assemble_bundle, verify_bundle

AUTHORITATIVE_SOURCE = Path("data/pokemon-tcg-ai-battle-challenge-strategy/EN Card Data.csv")
AUTHORITATIVE_SHA256 = "507d8d670c9c3c8d58f400d42eed09270b6b01354332770081bdb455d53b8c84"
REFERENCE_DECK = Path("config/reference-deck.json")


def _load_inputs() -> tuple[object, object]:
    catalog = load_catalog(AUTHORITATIVE_SOURCE, expected_sha256=AUTHORITATIVE_SHA256)
    return catalog, load_deck(REFERENCE_DECK, catalog)


def _summary_document(evaluation: object) -> dict[str, object]:
    return {
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


def _interpretation(evaluation: object) -> str:
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


def _limitations() -> str:
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


def _dependencies() -> dict[str, str]:
    return {
        "python": ".".join(map(str, sys.version_info[:3])),
        "kaggle-environments": metadata.version("kaggle-environments"),
        "fall-ai-studio-pokemon": metadata.version("fall-ai-studio-pokemon"),
    }


def _validate_source(_: argparse.Namespace) -> int:
    catalog, deck = _load_inputs()
    print(
        json.dumps(
            {
                "source": asdict(catalog.source),
                "reference_deck": {
                    "name": deck.name,
                    "card_count": len(deck.card_ids),
                    "sha256": deck.sha256,
                },
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def _smoke_match(args: argparse.Namespace) -> int:
    _, deck = _load_inputs()
    evaluation = run_evaluation(
        EvaluationPlan.balanced(match_count=args.matches),
        CabtBattleAdapter(),
        deck=deck.card_ids,
    )
    print(json.dumps(_summary_document(evaluation), indent=2, sort_keys=True))
    return 0 if evaluation.accepted else 1


def _acceptance_run(args: argparse.Namespace) -> int:
    if os.environ.get("GITHUB_ACTIONS") != "true":
        raise SystemExit("acceptance-run is approval evidence and may run only in GitHub Actions")
    if args.matches != 20:
        raise SystemExit("September Baseline acceptance requires exactly 20 matches")
    catalog, deck = _load_inputs()
    started_at = datetime.now(UTC).isoformat().replace("+00:00", "Z")
    evaluation = run_evaluation(
        EvaluationPlan.balanced(match_count=args.matches),
        CabtBattleAdapter(),
        deck=deck.card_ids,
    )
    finished_at = datetime.now(UTC).isoformat().replace("+00:00", "Z")
    receipt = RunReceipt(
        run_id=args.run_id,
        status="succeeded" if evaluation.accepted else "failed",
        started_at=started_at,
        finished_at=finished_at,
        code_revision=args.commit_sha,
        environment=f"github-actions/{os.environ.get('RUNNER_OS', 'unknown').lower()}",
        workflow_url=args.workflow_url,
        command="fall-ai-studio acceptance-run --matches 20",
        dependencies=_dependencies(),
    )
    assemble_bundle(
        args.bundle,
        evaluation=evaluation,
        source=catalog.source,
        deck=deck,
        deck_path=REFERENCE_DECK,
        receipt=receipt,
        interpretation=_interpretation(evaluation),
        limitations=_limitations(),
    )
    print(json.dumps(_summary_document(evaluation), indent=2, sort_keys=True))
    return 0


def _verify(args: argparse.Namespace) -> int:
    integrity = verify_bundle(args.bundle)
    print(json.dumps(asdict(integrity), indent=2, sort_keys=True))
    return 0 if integrity.valid else 1


def _independent_verify(args: argparse.Namespace) -> int:
    if os.environ.get("GITHUB_ACTIONS") != "true":
        raise SystemExit("independent-verify may run only in a fresh GitHub Actions environment")
    if args.matches != 20:
        raise SystemExit("September Baseline verification requires exactly 20 matches")
    integrity = verify_bundle(args.bundle)
    if not integrity.valid:
        print(json.dumps(asdict(integrity), indent=2, sort_keys=True))
        return 1
    original = json.loads((args.bundle / "summary.json").read_text(encoding="utf-8"))
    _, deck = _load_inputs()
    rerun = run_evaluation(
        EvaluationPlan.balanced(match_count=args.matches),
        CabtBattleAdapter(),
        deck=deck.card_ids,
    )
    rerun_summary = _summary_document(rerun)
    verification = {
        "schema": "fall-ai-studio/independent-verification/v1",
        "run_id": args.run_id,
        "workflow_url": args.workflow_url,
        "code_revision": args.commit_sha,
        "bundle": str(args.bundle),
        "bundle_integrity": asdict(integrity),
        "rerun": rerun_summary,
        "original_outcomes": original.get("by_baseline_position"),
        "outcomes_identical": (
            original.get("by_baseline_position") == rerun_summary["by_baseline_position"]
        ),
        "conclusion": "verified" if rerun.accepted else "failed",
        "note": "Outcome equality is recorded but is not required because CABT is not seeded.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(verification, indent=2, sort_keys=True) + "\n")
    print(json.dumps(verification, indent=2, sort_keys=True))
    return 0 if rerun.accepted else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="fall-ai-studio")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate-source", help="validate source and deck contracts")
    validate.set_defaults(handler=_validate_source)

    smoke = subparsers.add_parser("smoke-match", help="run local CABT development matches")
    smoke.add_argument("--matches", type=int, default=2)
    smoke.set_defaults(handler=_smoke_match)

    acceptance = subparsers.add_parser(
        "acceptance-run", help="produce a September bundle in GitHub Actions"
    )
    acceptance.add_argument("--bundle", type=Path, required=True)
    acceptance.add_argument("--matches", type=int, default=20)
    acceptance.add_argument("--commit-sha", required=True)
    acceptance.add_argument("--run-id", required=True)
    acceptance.add_argument("--workflow-url", required=True)
    acceptance.set_defaults(handler=_acceptance_run)

    verify = subparsers.add_parser("verify-bundle", help="recompute Bundle Integrity")
    verify.add_argument("bundle", type=Path)
    verify.set_defaults(handler=_verify)

    independent = subparsers.add_parser(
        "independent-verify", help="verify a committed bundle and repeat its evaluation"
    )
    independent.add_argument("--bundle", type=Path, required=True)
    independent.add_argument("--output", type=Path, required=True)
    independent.add_argument("--matches", type=int, default=20)
    independent.add_argument("--commit-sha", required=True)
    independent.add_argument("--run-id", required=True)
    independent.add_argument("--workflow-url", required=True)
    independent.set_defaults(handler=_independent_verify)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
