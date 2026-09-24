import json
from pathlib import Path

import pytest

from fall_ai_studio.battle import (
    BaselineAgent,
    EvaluationPlan,
    InMemoryBattleAdapter,
    IntegrationControl,
    SimulationResult,
    run_evaluation,
)

OBSERVATIONS = json.loads(Path("tests/fixtures/cabt-observations.json").read_text())


def test_baseline_agent_uses_the_frozen_main_action_priority():
    agent = BaselineAgent(deck=(3,) * 60)

    action = agent(OBSERVATIONS["main_phase"])

    assert action == [3]


def test_baseline_agent_forces_progress_after_eight_non_terminal_actions():
    agent = BaselineAgent(deck=(3,) * 60)
    observation = {
        "current": {"turn": 7, "yourIndex": 0, "result": -1},
        "select": {
            "type": 0,
            "minCount": 1,
            "maxCount": 1,
            "option": [{"type": 7}, {"type": 13}, {"type": 14}],
        },
    }

    first_eight = [agent(observation) for _ in range(8)]
    guarded_action = agent(observation)

    assert first_eight == [[0]] * 8
    assert guarded_action == [1]


def test_baseline_agent_never_bypasses_the_progress_guard_with_avoid_actions():
    agent = BaselineAgent(deck=(3,) * 60)
    play_observation = {
        "current": {"turn": 7, "yourIndex": 0, "result": -1},
        "select": {
            "type": 0,
            "minCount": 1,
            "maxCount": 1,
            "option": [{"type": 7}],
        },
    }
    for _ in range(8):
        agent(play_observation)
    avoid_only_observation = {
        **play_observation,
        "select": {
            "type": 0,
            "minCount": 1,
            "maxCount": 1,
            "option": [{"type": 11}, {"type": 12}],
        },
    }

    with pytest.raises(RuntimeError, match="no ATTACK or END"):
        agent(avoid_only_observation)


def test_agents_resolve_non_main_selections_stably():
    baseline = BaselineAgent(deck=(3,) * 60)
    control = IntegrationControl(deck=(3,) * 60)

    assert baseline(OBSERVATIONS["yes_no"]) == [1]
    assert baseline(OBSERVATIONS["follow_up"]) == [0, 1]
    assert control(OBSERVATIONS["main_phase"]) == [0]


def test_balanced_evaluation_reports_outcomes_by_baseline_position():
    player_zero_wins = [
        SimulationResult(
            rewards=(1.0, -1.0),
            statuses=("DONE", "DONE"),
            termination="completed",
            step_count=12,
        )
        for _ in range(20)
    ]
    adapter = InMemoryBattleAdapter(player_zero_wins)

    evaluation = run_evaluation(EvaluationPlan.balanced(match_count=20), adapter, deck=(3,) * 60)

    assert evaluation.summary.completed_matches == 20
    assert evaluation.summary.invalid_or_error_matches == 0
    assert evaluation.summary.by_position[0].wins == 10
    assert evaluation.summary.by_position[1].losses == 10
    assert [match.baseline_position for match in evaluation.matches] == [0] * 10 + [1] * 10
