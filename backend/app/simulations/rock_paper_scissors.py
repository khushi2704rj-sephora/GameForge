"""Rock-Paper-Scissors — cyclic dominance and mixed-strategy dynamics."""
from __future__ import annotations
import random, time
from app.models.schemas import GameInfo, ParameterSpec, SimulationResult, RoundData, Equilibrium
from app.simulations.base import BaseGame

BEATS = {"R": "S", "S": "P", "P": "R"}
def _payoff(a, b):
    if a == b: return (0, 0)
    return (1, -1) if BEATS[a] == b else (-1, 1)

STRATEGIES = {
    "random": lambda _h, _o: random.choice(["R", "P", "S"]),
    "always_rock": lambda _h, _o: "R",
    "always_paper": lambda _h, _o: "P",
    "always_scissors": lambda _h, _o: "S",
    "beat_last": lambda _h, o: {"R":"P","P":"S","S":"R"}.get(o[-1], "R") if o else random.choice(["R","P","S"]),
    "cycle": lambda h, _o: ["R","P","S"][len(h) % 3],
    "frequency_counter": lambda _h, o: (
        {"R":"P","P":"S","S":"R"}[max(set(o), key=o.count)] if o else random.choice(["R","P","S"])
    ),
}

class RockPaperScissors(BaseGame):
    def info(self) -> GameInfo:
        return GameInfo(
            id="rock_paper_scissors", name="Rock-Paper-Scissors", category="classical", tier=1,
            short_description="Cyclic dominance and mixed-strategy dynamics.",
            long_description="The classic three-action game where Rock beats Scissors, Scissors beats Paper, Paper beats Rock. Demonstrates cyclic dominance with no pure-strategy equilibrium.",
            parameters=[
                ParameterSpec(name="rounds", type="int", default=200, min=1, max=10000, description="Number of rounds"),
                ParameterSpec(name="strategy_p1", type="select", default="beat_last", options=list(STRATEGIES), description="Player 1 strategy"),
                ParameterSpec(name="strategy_p2", type="select", default="frequency_counter", options=list(STRATEGIES), description="Player 2 strategy"),
            ],
            available=True, engine="server", tags=["zero-sum", "cyclic"],
            theory_card="## Cyclic Dominance\nNo action is universally best: R→S→P→R. This creates a **cycle** with no pure-strategy NE.\n\n## Mixed-Strategy NE\nThe unique equilibrium is to play each action with probability **1/3**.\n\n## Key Insight\nPatterns in play can be exploited. The best strategy against an exploitable opponent is **not** to randomize uniformly.",
        )

    def compute(self, config: dict) -> SimulationResult:
        t0 = time.time()
        rounds = config.get("rounds", 200)
        s1 = STRATEGIES.get(config.get("strategy_p1", "beat_last"), STRATEGIES["random"])
        s2 = STRATEGIES.get(config.get("strategy_p2", "frequency_counter"), STRATEGIES["random"])
        h1, h2, rd = [], [], []
        tot1 = tot2 = 0
        counts = {"R": 0, "P": 0, "S": 0}
        for r in range(1, rounds + 1):
            a1, a2 = s1(h1, h2), s2(h2, h1)
            p1, p2 = _payoff(a1, a2)
            tot1 += p1; tot2 += p2
            counts[a1] += 1
            h1.append(a1); h2.append(a2)
            rd.append(RoundData(round_num=r, actions=[a1, a2], payoffs=[p1, p2],
                state={"cumulative": [tot1, tot2], "p1_rock_rate": counts["R"]/r, "p1_paper_rate": counts["P"]/r, "p1_scissors_rate": counts["S"]/r}))
        wins1 = sum(1 for i in range(len(h1)) if _payoff(h1[i], h2[i])[0] > 0)
        wins2 = sum(1 for i in range(len(h1)) if _payoff(h1[i], h2[i])[0] < 0)
        draws = rounds - wins1 - wins2
        return SimulationResult(game_id="rock_paper_scissors", config=config, rounds=rd,
            equilibria=[Equilibrium(name="Mixed-Strategy NE", strategies=["1/3 each","1/3 each"], payoffs=[0,0], description="Uniform random over R, P, S.")],
            summary={"p1_wins": wins1, "p2_wins": wins2, "draws": draws, "p1_win_rate": wins1/rounds, "avg_payoff_p1": tot1/rounds, "avg_payoff_p2": tot2/rounds},
            metadata={"compute_time_ms": round((time.time()-t0)*1000, 2), "engine": "server"})
