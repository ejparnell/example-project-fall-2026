"""Run a stable baseline policy behind a simulator-independent interface."""

from __future__ import annotations

from collections import Counter
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from enum import IntEnum
from typing import Any, Protocol


class SelectType(IntEnum):
    MAIN = 0
    YES_NO = 9


class OptionType(IntEnum):
    YES = 1
    NO = 2
    PLAY = 7
    ATTACH = 8
    EVOLVE = 9
    ABILITY = 10
    DISCARD = 11
    RETREAT = 12
    ATTACK = 13
    END = 14


MAIN_ACTION_PRIORITY = (
    OptionType.EVOLVE,
    OptionType.ATTACH,
    OptionType.ABILITY,
    OptionType.PLAY,
    OptionType.ATTACK,
    OptionType.END,
)


class BaselineAgent:
    """Deterministic September policy; it deliberately avoids card-text strategy."""

    def __init__(self, deck: Sequence[int]) -> None:
        self._deck = tuple(deck)
        self.reset()

    def reset(self) -> None:
        """Reset state when a simulator starts a new match."""
        self._turn: int | None = None
        self._non_terminal_actions = 0

    def __call__(
        self, observation: Mapping[str, Any], configuration: Mapping[str, Any] | None = None
    ) -> list[int]:
        del configuration
        selection = observation.get("select")
        if selection is None:
            return list(self._deck)

        options = selection.get("option", [])
        if selection.get("type") == SelectType.MAIN:
            turn = observation.get("current", {}).get("turn")
            if turn != self._turn:
                self._turn = turn
                self._non_terminal_actions = 0
            priority = MAIN_ACTION_PRIORITY
            guard_active = self._non_terminal_actions >= 8
            if guard_active:
                priority = (OptionType.ATTACK, OptionType.END)
            for desired_type in priority:
                for index, option in enumerate(options):
                    if option.get("type") == desired_type:
                        if desired_type not in {OptionType.ATTACK, OptionType.END}:
                            self._non_terminal_actions += 1
                        return [index]
            if guard_active:
                raise RuntimeError("Baseline progress guard found no ATTACK or END option")
        if selection.get("type") == SelectType.YES_NO:
            for index, option in enumerate(options):
                if option.get("type") == OptionType.YES:
                    return [index]

        count = min(int(selection.get("maxCount", 1)), len(options))
        return list(range(count))


class IntegrationControl:
    """The simulator's intentionally trivial first-legal execution control."""

    def __init__(self, deck: Sequence[int]) -> None:
        self._deck = tuple(deck)

    def reset(self) -> None:
        """Provide the lifecycle hook expected by Kaggle Environments."""

    def __call__(
        self, observation: Mapping[str, Any], configuration: Mapping[str, Any] | None = None
    ) -> list[int]:
        del configuration
        selection = observation.get("select")
        if selection is None:
            return list(self._deck)
        options = selection.get("option", [])
        count = min(int(selection.get("maxCount", 1)), len(options))
        return list(range(count))


@dataclass(frozen=True)
class EvaluationPlan:
    baseline_positions: tuple[int, ...]
    replay_match_id: int = 1

    @classmethod
    def balanced(cls, *, match_count: int) -> EvaluationPlan:
        if match_count <= 0 or match_count % 2:
            raise ValueError("A balanced Evaluation Plan requires a positive, even match count")
        per_position = match_count // 2
        return cls((0,) * per_position + (1,) * per_position)


@dataclass(frozen=True)
class SimulationResult:
    rewards: tuple[float, float]
    statuses: tuple[str, str]
    termination: str
    step_count: int
    replay: Mapping[str, Any] | None = None


Agent = Callable[..., list[int]]


class BattleAdapter(Protocol):
    def run_match(
        self,
        *,
        match_id: int,
        agents: tuple[Agent, Agent],
        capture_replay: bool,
    ) -> SimulationResult: ...


class InMemoryBattleAdapter:
    """Deterministic adapter for exercising the Battle interface without CABT."""

    def __init__(self, results: Sequence[SimulationResult]) -> None:
        self._results = tuple(results)

    def run_match(
        self,
        *,
        match_id: int,
        agents: tuple[Agent, Agent],
        capture_replay: bool,
    ) -> SimulationResult:
        del agents, capture_replay
        try:
            return self._results[match_id - 1]
        except IndexError as error:
            raise ValueError(f"No in-memory result configured for match {match_id}") from error


class CabtBattleAdapter:
    """Run matches through the real CABT environment shipped by Kaggle."""

    def run_match(
        self,
        *,
        match_id: int,
        agents: tuple[Agent, Agent],
        capture_replay: bool,
    ) -> SimulationResult:
        del match_id
        from kaggle_environments import make

        environment = make("cabt", debug=True)
        steps = environment.run(list(agents))
        final = steps[-1]
        statuses = tuple(str(state.status) for state in final)
        rewards = tuple(float(state.reward or 0.0) for state in final)
        if "INVALID" in statuses:
            termination = "invalid"
        elif any(status in {"ERROR", "TIMEOUT"} for status in statuses):
            termination = "error"
        elif statuses == ("DONE", "DONE"):
            termination = "completed"
        else:
            termination = "unexpected"
        replay = environment.toJSON() if capture_replay else None
        return SimulationResult(
            rewards=(rewards[0], rewards[1]),
            statuses=(statuses[0], statuses[1]),
            termination=termination,
            step_count=len(steps),
            replay=replay,
        )


@dataclass(frozen=True)
class MatchResult:
    match_id: int
    baseline_position: int
    outcome: str
    rewards: tuple[float, float]
    statuses: tuple[str, str]
    termination: str
    step_count: int
    replay: Mapping[str, Any] | None = None


@dataclass(frozen=True)
class PositionSummary:
    wins: int
    losses: int
    draws: int


@dataclass(frozen=True)
class EvaluationSummary:
    match_count: int
    completed_matches: int
    invalid_or_error_matches: int
    by_position: Mapping[int, PositionSummary]
    terminations: Mapping[str, int]


@dataclass(frozen=True)
class EvaluationResult:
    plan: EvaluationPlan
    matches: tuple[MatchResult, ...]
    summary: EvaluationSummary

    @property
    def accepted(self) -> bool:
        return (
            self.summary.completed_matches == self.summary.match_count
            and self.summary.invalid_or_error_matches == 0
        )


def run_evaluation(
    plan: EvaluationPlan,
    adapter: BattleAdapter,
    *,
    deck: Sequence[int],
) -> EvaluationResult:
    """Run the Baseline Agent against the Integration Control under one plan."""

    matches: list[MatchResult] = []
    for match_id, baseline_position in enumerate(plan.baseline_positions, start=1):
        baseline = BaselineAgent(deck)
        control = IntegrationControl(deck)
        agents: tuple[Agent, Agent]
        if baseline_position == 0:
            agents = (baseline, control)
        else:
            agents = (control, baseline)
        simulation = adapter.run_match(
            match_id=match_id,
            agents=agents,
            capture_replay=match_id == plan.replay_match_id,
        )
        baseline_reward = simulation.rewards[baseline_position]
        control_reward = simulation.rewards[1 - baseline_position]
        if baseline_reward > control_reward:
            outcome = "win"
        elif baseline_reward < control_reward:
            outcome = "loss"
        else:
            outcome = "draw"
        matches.append(
            MatchResult(
                match_id=match_id,
                baseline_position=baseline_position,
                outcome=outcome,
                rewards=simulation.rewards,
                statuses=simulation.statuses,
                termination=simulation.termination,
                step_count=simulation.step_count,
                replay=simulation.replay,
            )
        )

    by_position: dict[int, PositionSummary] = {}
    for position in (0, 1):
        outcomes = Counter(
            match.outcome for match in matches if match.baseline_position == position
        )
        by_position[position] = PositionSummary(
            wins=outcomes["win"], losses=outcomes["loss"], draws=outcomes["draw"]
        )
    terminations = Counter(match.termination for match in matches)
    completed = terminations["completed"]
    summary = EvaluationSummary(
        match_count=len(matches),
        completed_matches=completed,
        invalid_or_error_matches=len(matches) - completed,
        by_position=by_position,
        terminations=dict(terminations),
    )
    return EvaluationResult(plan, tuple(matches), summary)
