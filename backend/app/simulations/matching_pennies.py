"""Matching Pennies — zero-sum game with only mixed-strategy equilibrium."""
from __future__ import annotations
import random, time
from app.models.schemas import GameInfo, ParameterSpec, SimulationResult, RoundData, Equilibrium
from app.simulations.base import BaseGame

# Matcher wins if same, Mismatcher wins if different
PAYOFF = {("H","H"):(1,-1),("H","T"):(-1,1),("T","H"):(-1,1),("T","T"):(1,-1)}
STRATEGIES = {
    "always_heads": lambda _h, _o: "H",
    "always_tails": lambda _h, _o: "T",
    "random_50": lambda _h, _o: random.choice(["H", "T"]),
    "biased_70h": lambda _h, _o: "H" if random.random() < 0.7 else "T",
    "anti_pattern": lambda _h, o: ("T" if o[-1] == "H" else "H") if o else random.choice(["H","T"]),
    "win_stay_lose_shift": lambda h, o: (h[-1] if PAYOFF.get((h[-1], o[-1]), (0,0))[0] > 0 else ("T" if h[-1]=="H" else "H")) if h else "H",
}

class MatchingPennies(BaseGame):
    def info(self) -> GameInfo:
        return GameInfo(
            id="matching_pennies", name="Matching Pennies", category="classical", tier=1,
            short_description="A zero-sum game with only mixed-strategy equilibrium.",
            long_description="One player (Matcher) wins if both coins show the same side; the other (Mismatcher) wins if they differ. No pure-strategy NE exists — the only equilibrium is randomizing 50/50.",
            parameters=[
                ParameterSpec(name="rounds", type="int", default=200, min=1, max=10000, description="Number of rounds"),
                ParameterSpec(name="strategy_matcher", type="select", default="random_50", options=list(STRATEGIES), description="Matcher strategy"),
                ParameterSpec(name="strategy_mismatcher", type="select", default="anti_pattern", options=list(STRATEGIES), description="Mismatcher strategy"),
            ],
            available=True, engine="server", tags=["zero-sum", "mixed-NE"],
            theory_card="## No Pure-Strategy NE\nAny deterministic strategy can be exploited. The **unique NE** is for both players to randomize 50/50.\n\n## Key Insight\nMatching Pennies is the simplest example of why **randomization** (mixed strategies) is essential in game theory.",
        )

    def compute(self, config: dict) -> SimulationResult:
        t0 = time.time()
        rounds = config.get("rounds", 200)
        s1 = STRATEGIES.get(config.get("strategy_matcher", "random_50"), STRATEGIES["random_50"])
        s2 = STRATEGIES.get(config.get("strategy_mismatcher", "anti_pattern"), STRATEGIES["random_50"])
        h1, h2, rd = [], [], []
        tot1 = tot2 = match_count = 0
        for r in range(1, rounds + 1):
            a1, a2 = s1(h1, h2), s2(h2, h1)
            p1, p2 = PAYOFF[(a1, a2)]
            tot1 += p1; tot2 += p2
            if a1 == a2: match_count += 1
            h1.append(a1); h2.append(a2)
            rd.append(RoundData(round_num=r, actions=[a1, a2], payoffs=[p1, p2],
                state={"cumulative": [tot1, tot2], "match_rate": match_count / r}))
        return SimulationResult(game_id="matching_pennies", config=config, rounds=rd,
            equilibria=[Equilibrium(name="Mixed-Strategy NE", strategies=["50% H","50% H"], payoffs=[0,0], description="Both randomize 50/50; expected payoff is 0.")],
            summary={"total_payoff_matcher": tot1, "total_payoff_mismatcher": tot2, "avg_payoff_matcher": tot1/rounds, "match_rate": match_count/rounds},
            metadata={"compute_time_ms": round((time.time()-t0)*1000, 2), "engine": "server"})
