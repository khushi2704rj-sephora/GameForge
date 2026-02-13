"""Battle of the Sexes — asymmetric coordination game."""
from __future__ import annotations
import random, time
from app.models.schemas import GameInfo, ParameterSpec, SimulationResult, RoundData, Equilibrium
from app.simulations.base import BaseGame

# A prefers Opera (O), B prefers Football (F)
PAYOFF = {("O","O"):(3,2),("O","F"):(0,0),("F","O"):(0,0),("F","F"):(2,3)}
STRATEGIES = {
    "always_opera": lambda _h, _o: "O",
    "always_football": lambda _h, _o: "F",
    "alternate": lambda h, _o: "O" if len(h) % 2 == 0 else "F",
    "tit_for_tat": lambda _h, o: "O" if not o else o[-1],
    "random": lambda _h, _o: random.choice(["O", "F"]),
    "stubborn_70": lambda _h, _o: "O" if random.random() < 0.7 else "F",
}

class BattleOfSexes(BaseGame):
    def info(self) -> GameInfo:
        return GameInfo(
            id="battle_of_sexes", name="Battle of the Sexes", category="classical", tier=1,
            short_description="Coordinate when preferences diverge.",
            long_description="Two players want to coordinate activities but have different preferences. Both prefer being together over being apart, but they disagree on which activity is best.",
            parameters=[
                ParameterSpec(name="rounds", type="int", default=100, min=1, max=5000, description="Number of rounds"),
                ParameterSpec(name="strategy_p1", type="select", default="stubborn_70", options=list(STRATEGIES), description="Player 1 strategy (prefers Opera)"),
                ParameterSpec(name="strategy_p2", type="select", default="tit_for_tat", options=list(STRATEGIES), description="Player 2 strategy (prefers Football)"),
            ],
            available=True, engine="server", tags=["coordination", "mixed-NE"],
            theory_card="## Multiple Equilibria\nTwo pure-strategy NE: (Opera, Opera) and (Football, Football). There's also a **mixed-strategy NE** where each randomizes.\n\n## Key Insight\nCoordination is harder when players have **asymmetric preferences**. Communication or convention can resolve the dilemma.",
        )

    def compute(self, config: dict) -> SimulationResult:
        t0 = time.time()
        rounds = config.get("rounds", 100)
        s1 = STRATEGIES.get(config.get("strategy_p1", "stubborn_70"), STRATEGIES["random"])
        s2 = STRATEGIES.get(config.get("strategy_p2", "tit_for_tat"), STRATEGIES["random"])
        h1, h2, rd = [], [], []
        tot1 = tot2 = coord = 0
        for r in range(1, rounds + 1):
            a1, a2 = s1(h1, h2), s2(h2, h1)
            p1, p2 = PAYOFF[(a1, a2)]
            tot1 += p1; tot2 += p2
            if a1 == a2: coord += 1
            h1.append(a1); h2.append(a2)
            rd.append(RoundData(round_num=r, actions=[a1, a2], payoffs=[p1, p2],
                state={"cumulative": [tot1, tot2], "coordination_rate": coord / r}))
        return SimulationResult(game_id="battle_of_sexes", config=config, rounds=rd,
            equilibria=[
                Equilibrium(name="NE: Both Opera", strategies=["O","O"], payoffs=[3,2], description="P1's preferred outcome."),
                Equilibrium(name="NE: Both Football", strategies=["F","F"], payoffs=[2,3], description="P2's preferred outcome."),
            ],
            summary={"total_payoff_p1": tot1, "total_payoff_p2": tot2, "avg_payoff_p1": tot1/rounds, "avg_payoff_p2": tot2/rounds, "coordination_rate": coord/rounds},
            metadata={"compute_time_ms": round((time.time()-t0)*1000, 2), "engine": "server"})
