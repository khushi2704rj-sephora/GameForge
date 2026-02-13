"""Stag Hunt — coordination game: risky high payoff vs safe low payoff."""
from __future__ import annotations
import random, time
from app.models.schemas import GameInfo, ParameterSpec, SimulationResult, RoundData, Equilibrium
from app.simulations.base import BaseGame

PAYOFF = {("S","S"):(4,4),("S","H"):(0,3),("H","S"):(3,0),("H","H"):(3,3)}
STRATEGIES = {
    "always_stag": lambda _h, _o: "S",
    "always_hare": lambda _h, _o: "H",
    "tit_for_tat": lambda _h, o: "S" if not o else o[-1],
    "random": lambda _h, _o: random.choice(["S", "H"]),
    "cautious": lambda _h, o: "S" if not o else ("S" if o[-3:].count("S") >= 2 else "H"),
    "pavlov": lambda h, o: "S" if not h else ("S" if h[-1] == o[-1] else "H"),
}

class StagHunt(BaseGame):
    def info(self) -> GameInfo:
        return GameInfo(
            id="stag_hunt", name="Stag Hunt", category="classical", tier=1,
            short_description="Coordinate on the risky high-payoff option or play it safe?",
            long_description="Two hunters choose to hunt Stag (high payoff but requires coordination) or Hare (safe, lower payoff). Unlike PD, mutual cooperation is a Nash equilibrium — but so is mutual defection.",
            parameters=[
                ParameterSpec(name="rounds", type="int", default=100, min=1, max=5000, description="Number of rounds"),
                ParameterSpec(name="strategy_p1", type="select", default="tit_for_tat", options=list(STRATEGIES), description="Player 1 strategy"),
                ParameterSpec(name="strategy_p2", type="select", default="cautious", options=list(STRATEGIES), description="Player 2 strategy"),
            ],
            available=True, engine="server", tags=["coordination", "trust"],
            theory_card="## Two Nash Equilibria\nUnlike PD, Stag Hunt has **two** pure-strategy NE: (Stag, Stag) is *payoff-dominant* and (Hare, Hare) is *risk-dominant*.\n\n## Key Insight\nThe tension between **payoff dominance** and **risk dominance** captures real-world coordination problems — from technology adoption to international agreements.",
        )

    def compute(self, config: dict) -> SimulationResult:
        t0 = time.time()
        rounds = config.get("rounds", 100)
        s1 = STRATEGIES.get(config.get("strategy_p1", "tit_for_tat"), STRATEGIES["random"])
        s2 = STRATEGIES.get(config.get("strategy_p2", "cautious"), STRATEGIES["random"])
        h1, h2, rd = [], [], []
        tot1 = tot2 = stag_count = 0
        for r in range(1, rounds + 1):
            a1, a2 = s1(h1, h2), s2(h2, h1)
            p1, p2 = PAYOFF[(a1, a2)]
            tot1 += p1; tot2 += p2
            if a1 == "S": stag_count += 1
            if a2 == "S": stag_count += 1
            h1.append(a1); h2.append(a2)
            rd.append(RoundData(round_num=r, actions=[a1, a2], payoffs=[p1, p2],
                state={"cumulative": [tot1, tot2], "stag_rate": stag_count / (2 * r)}))
        return SimulationResult(game_id="stag_hunt", config=config, rounds=rd,
            equilibria=[
                Equilibrium(name="Payoff-Dominant NE", strategies=["S","S"], payoffs=[4,4], description="Both hunt Stag — highest mutual payoff."),
                Equilibrium(name="Risk-Dominant NE", strategies=["H","H"], payoffs=[3,3], description="Both hunt Hare — safe but suboptimal."),
            ],
            summary={"total_payoff_p1": tot1, "total_payoff_p2": tot2, "avg_payoff_p1": tot1/rounds, "avg_payoff_p2": tot2/rounds, "stag_rate": stag_count/(2*rounds)},
            metadata={"compute_time_ms": round((time.time()-t0)*1000, 2), "engine": "server"})
