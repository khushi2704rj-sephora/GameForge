"""Prisoner's Dilemma — iterated with configurable strategies and noise."""
from __future__ import annotations
import random
import time
from app.models.schemas import (
    GameInfo, ParameterSpec, SimulationResult, RoundData, Equilibrium,
)
from app.simulations.base import BaseGame

STRATEGIES = {
    "always_cooperate": lambda _history, _opp_history: "C",
    "always_defect": lambda _history, _opp_history: "D",
    "random": lambda _h, _o: random.choice(["C", "D"]),
    "tit_for_tat": lambda _h, opp: "C" if not opp else opp[-1],
    "grim_trigger": lambda _h, opp: "D" if "D" in opp else "C",
    "pavlov": lambda h, opp: (
        "C" if not h else ("C" if h[-1] == opp[-1] else "D")
    ),
}

PAYOFF_MATRIX = {
    ("C", "C"): (3, 3),
    ("C", "D"): (0, 5),
    ("D", "C"): (5, 0),
    ("D", "D"): (1, 1),
}


class PrisonersDilemma(BaseGame):
    def info(self) -> GameInfo:
        return GameInfo(
            id="prisoners_dilemma",
            name="Prisoner's Dilemma",
            category="classical",
            tier=1,
            short_description="The canonical cooperation-vs-defection dilemma.",
            long_description=(
                "Two players simultaneously choose to Cooperate (C) or Defect (D). "
                "Mutual cooperation yields a moderate reward, mutual defection yields "
                "a low punishment, and unilateral defection yields the highest payoff "
                "for the defector but nothing for the cooperator. The iterated version "
                "allows strategies like Tit-for-Tat to sustain cooperation."
            ),
            parameters=[
                ParameterSpec(name="rounds", type="int", default=100, min=1, max=10000,
                              description="Number of rounds to play"),
                ParameterSpec(name="noise", type="float", default=0.0, min=0, max=0.5,
                              description="Probability of action being flipped randomly"),
                ParameterSpec(name="strategy_p1", type="select", default="tit_for_tat",
                              options=list(STRATEGIES.keys()),
                              description="Strategy for Player 1"),
                ParameterSpec(name="strategy_p2", type="select", default="always_defect",
                              options=list(STRATEGIES.keys()),
                              description="Strategy for Player 2"),
            ],
            available=True,
            engine="browser",
            tags=["cooperation", "classic", "iterated"],
            theory_card=(
                "## Nash Equilibrium\n"
                "In the one-shot game, (Defect, Defect) is the unique Nash equilibrium — "
                "even though (Cooperate, Cooperate) Pareto-dominates it.\n\n"
                "## Iterated Play\n"
                "Robert Axelrod's tournaments (1980) showed that **Tit-for-Tat** — "
                "cooperate first, then mirror the opponent — is remarkably effective.\n\n"
                "## Key Insight\n"
                "The 'shadow of the future' (repeated interaction) can sustain cooperation "
                "that is impossible in a one-shot game."
            ),
        )

    def compute(self, config: dict) -> SimulationResult:
        t0 = time.time()
        rounds = config.get("rounds", 100)
        noise = config.get("noise", 0.0)
        s1_name = config.get("strategy_p1", "tit_for_tat")
        s2_name = config.get("strategy_p2", "always_defect")

        s1 = STRATEGIES.get(s1_name, STRATEGIES["random"])
        s2 = STRATEGIES.get(s2_name, STRATEGIES["random"])

        h1: list[str] = []
        h2: list[str] = []
        round_data: list[RoundData] = []
        total_p1, total_p2 = 0.0, 0.0
        coop_count = 0

        for r in range(1, rounds + 1):
            a1 = s1(h1, h2)
            a2 = s2(h2, h1)
            # Apply noise
            if noise > 0:
                if random.random() < noise:
                    a1 = "D" if a1 == "C" else "C"
                if random.random() < noise:
                    a2 = "D" if a2 == "C" else "C"

            p1, p2 = PAYOFF_MATRIX[(a1, a2)]
            total_p1 += p1
            total_p2 += p2
            if a1 == "C":
                coop_count += 1
            if a2 == "C":
                coop_count += 1

            h1.append(a1)
            h2.append(a2)
            round_data.append(RoundData(
                round_num=r, actions=[a1, a2], payoffs=[p1, p2],
                state={"cumulative": [total_p1, total_p2],
                       "coop_rate": coop_count / (2 * r)},
            ))

        return SimulationResult(
            game_id="prisoners_dilemma",
            config=config,
            rounds=round_data,
            equilibria=[
                Equilibrium(
                    name="Nash Equilibrium (one-shot)",
                    strategies=["D", "D"],
                    payoffs=[1.0, 1.0],
                    description="Mutual defection is the dominant strategy equilibrium.",
                )
            ],
            summary={
                "total_payoff_p1": total_p1,
                "total_payoff_p2": total_p2,
                "avg_payoff_p1": total_p1 / rounds,
                "avg_payoff_p2": total_p2 / rounds,
                "cooperation_rate": coop_count / (2 * rounds),
                "strategy_p1": s1_name,
                "strategy_p2": s2_name,
            },
            metadata={"compute_time_ms": round((time.time() - t0) * 1000, 2), "engine": "server"},
        )
