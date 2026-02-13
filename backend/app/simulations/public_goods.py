"""Public Goods Game — N-player contribution game with optional punishment."""
from __future__ import annotations
import random
import time
from app.models.schemas import (
    GameInfo, ParameterSpec, SimulationResult, RoundData, Equilibrium,
)
from app.simulations.base import BaseGame


class PublicGoodsGame(BaseGame):
    def info(self) -> GameInfo:
        return GameInfo(
            id="public_goods",
            name="Public Goods Game",
            category="classical",
            tier=1,
            short_description="Can groups overcome free-riding to fund public goods?",
            long_description=(
                "N players each receive an endowment and decide how much to contribute "
                "to a common pool. The pool is multiplied by a factor (1 < m < N) and "
                "divided equally among all players. The Nash equilibrium is zero contribution, "
                "yet experiments consistently show partial cooperation. Adding peer punishment "
                "can sustain higher contribution levels."
            ),
            parameters=[
                ParameterSpec(name="n_players", type="int", default=5, min=2, max=20,
                              description="Number of players"),
                ParameterSpec(name="endowment", type="float", default=10.0, min=1, max=100,
                              description="Starting endowment per player per round"),
                ParameterSpec(name="multiplier", type="float", default=2.0, min=1.1, max=10,
                              description="Multiplication factor for the common pool"),
                ParameterSpec(name="rounds", type="int", default=50, min=1, max=500,
                              description="Number of rounds"),
                ParameterSpec(name="punishment_cost", type="float", default=0.0, min=0, max=5,
                              description="Cost to punish a free-rider (0 = no punishment)"),
                ParameterSpec(name="strategy", type="select", default="conditional_cooperator",
                              options=["full_cooperator", "free_rider", "conditional_cooperator", "random"],
                              description="Default agent strategy"),
            ],
            available=True,
            engine="browser",
            tags=["cooperation", "public-goods", "n-player", "free-riding"],
            theory_card=(
                "## The Free-Rider Problem\n"
                "Since the public good is non-excludable, each player's dominant strategy "
                "is to contribute nothing — let others pay.\n\n"
                "## Experimental Evidence\n"
                "In lab experiments (Fehr & Gächter, 2000), contributions start around 40-60% "
                "of endowment and decay over rounds — unless **peer punishment** is introduced.\n\n"
                "## Key Parameters\n"
                "- **Multiplier (MPCR)**: if m/N > 1, full cooperation is socially optimal.\n"
                "- **Punishment cost**: even small punishment costs deter free-riding."
            ),
        )

    def compute(self, config: dict) -> SimulationResult:
        t0 = time.time()
        n = config.get("n_players", 5)
        endowment = config.get("endowment", 10.0)
        mult = config.get("multiplier", 2.0)
        rounds = config.get("rounds", 50)
        punish_cost = config.get("punishment_cost", 0.0)
        strategy = config.get("strategy", "conditional_cooperator")

        round_data: list[RoundData] = []
        prev_avg_contrib = endowment * 0.5  # starting guess for conditional

        for r in range(1, rounds + 1):
            contributions: list[float] = []
            for _p in range(n):
                if strategy == "full_cooperator":
                    c = endowment
                elif strategy == "free_rider":
                    c = 0.0
                elif strategy == "conditional_cooperator":
                    c = min(endowment, max(0, prev_avg_contrib + random.gauss(0, 1)))
                else:  # random
                    c = random.uniform(0, endowment)
                contributions.append(round(c, 2))

            pool = sum(contributions) * mult
            share = pool / n
            payoffs = [round(endowment - c + share, 2) for c in contributions]

            # Optional punishment
            if punish_cost > 0:
                avg_c = sum(contributions) / n
                for i in range(n):
                    if contributions[i] < avg_c * 0.5:  # free-rider threshold
                        payoffs[i] -= punish_cost * (n - 1)
                        for j in range(n):
                            if j != i:
                                payoffs[j] -= punish_cost * 0.3  # cost to punishers

            prev_avg_contrib = sum(contributions) / n

            round_data.append(RoundData(
                round_num=r,
                actions=contributions,
                payoffs=payoffs,
                state={
                    "pool": round(pool, 2),
                    "avg_contribution": round(prev_avg_contrib, 2),
                    "free_rider_ratio": round(
                        sum(1 for c in contributions if c < endowment * 0.1) / n, 2
                    ),
                },
            ))

        all_payoffs = [sum(rd.payoffs) / n for rd in round_data]
        all_contribs = [rd.state["avg_contribution"] for rd in round_data]

        return SimulationResult(
            game_id="public_goods",
            config=config,
            rounds=round_data,
            equilibria=[
                Equilibrium(
                    name="Nash Equilibrium",
                    strategies=["contribute 0"] * n,
                    payoffs=[endowment] * n,
                    description="Zero contribution is the dominant strategy in a one-shot game.",
                ),
                Equilibrium(
                    name="Social Optimum",
                    strategies=[f"contribute {endowment}"] * n,
                    payoffs=[round(endowment * mult / n, 2)] * n if mult > 1 else [endowment] * n,
                    description="Full contribution maximizes total welfare when multiplier > 1.",
                ),
            ],
            summary={
                "avg_payoff": round(sum(all_payoffs) / len(all_payoffs), 2),
                "avg_contribution": round(sum(all_contribs) / len(all_contribs), 2),
                "final_free_rider_ratio": round_data[-1].state["free_rider_ratio"],
                "contribution_trend": "declining" if all_contribs[-1] < all_contribs[0] else "stable_or_rising",
            },
            metadata={"compute_time_ms": round((time.time() - t0) * 1000, 2), "engine": "server"},
        )
