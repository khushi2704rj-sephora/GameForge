"""Tragedy of the Commons — shared resource depletion game."""
from __future__ import annotations
import random, time
from app.models.schemas import GameInfo, ParameterSpec, SimulationResult, RoundData, Equilibrium
from app.simulations.base import BaseGame

STRATEGIES = {
    "sustainable": lambda _h, cap: max(1, int(cap * 0.3)),
    "greedy": lambda _h, cap: max(1, int(cap * 0.7)),
    "moderate": lambda _h, cap: max(1, int(cap * 0.5)),
    "adaptive": lambda h, cap: max(1, int(cap * 0.5 * (1 - len([x for x in h[-5:] if x > 0.6]) / 5))) if h else max(1, int(cap * 0.4)),
    "random": lambda _h, cap: max(1, int(random.uniform(0.1, 0.8) * cap)),
    "tit_for_tat": lambda h, cap: max(1, int(cap * (h[-1] if h else 0.4))),
}

class TragedyOfCommons(BaseGame):
    def info(self) -> GameInfo:
        return GameInfo(
            id="tragedy_of_commons", name="Tragedy of the Commons", category="underrated", tier=2,
            short_description="Can rational agents sustain a shared resource?",
            long_description=(
                "N agents share a common resource pool that regenerates each round. Each agent "
                "chooses how much to harvest. If total harvest exceeds regeneration, the resource "
                "depletes. The tragedy: individually rational overuse leads to collective ruin. "
                "Explores sustainability, regulation, and cooperation in shared resource management."
            ),
            parameters=[
                ParameterSpec(name="n_agents", type="int", default=6, min=2, max=20, description="Number of agents"),
                ParameterSpec(name="resource_capacity", type="float", default=1000.0, min=100, max=10000, description="Resource pool capacity"),
                ParameterSpec(name="regeneration_rate", type="float", default=0.2, min=0.05, max=0.5, description="Regeneration rate per round"),
                ParameterSpec(name="rounds", type="int", default=100, min=10, max=500, description="Rounds to simulate"),
                ParameterSpec(name="strategy", type="select", default="moderate", options=list(STRATEGIES), description="Agent strategy"),
            ],
            available=True, engine="server", tags=["commons", "sustainability", "cooperation", "environmental"],
            theory_card=(
                "## Hardin's Tragedy (1968)\n"
                "Garrett Hardin showed that rational self-interest in shared resources leads to "
                "**overexploitation** — each agent benefits by taking more, but collectively they destroy the resource.\n\n"
                "## The Nash Equilibrium\n"
                "Without binding agreements, the NE involves **overconsumption** relative to the social optimum.\n\n"
                "## Ostrom's Solution\n"
                "Elinor Ostrom (Nobel 2009) demonstrated that communities can self-govern commons through "
                "**rules, monitoring, and graduated sanctions** — without privatization or state control."
            ),
        )

    def compute(self, config: dict) -> SimulationResult:
        t0 = time.time()
        n = config.get("n_agents", 6)
        capacity = config.get("resource_capacity", 1000.0)
        regen = config.get("regeneration_rate", 0.2)
        rounds = config.get("rounds", 100)
        strat_name = config.get("strategy", "moderate")
        strat_fn = STRATEGIES.get(strat_name, STRATEGIES["moderate"])
        
        pool = capacity
        rd, history = [], []
        total_harvested = 0
        depleted_round = None
        
        for r in range(1, rounds + 1):
            per_agent_cap = pool / n if pool > 0 else 0
            harvests = [strat_fn(history, per_agent_cap) for _ in range(n)]
            total_harvest = sum(harvests)
            actual = min(total_harvest, pool)
            scale = actual / total_harvest if total_harvest > 0 else 0
            actual_harvests = [h * scale for h in harvests]
            
            pool -= actual
            pool = min(capacity, pool + pool * regen)
            total_harvested += actual
            
            if pool < 1 and depleted_round is None:
                depleted_round = r
            
            usage_ratio = actual / capacity if capacity > 0 else 0
            history.append(usage_ratio)
            
            rd.append(RoundData(
                round_num=r, actions=actual_harvests, payoffs=[actual / n],
                state={"pool": round(pool, 2), "total_harvest": round(actual, 2), "usage_ratio": round(usage_ratio, 4)}
            ))
        
        return SimulationResult(
            game_id="tragedy_of_commons", config=config, rounds=rd,
            equilibria=[Equilibrium(
                name="Overexploitation NE", strategies=[strat_name] * n,
                description=f"Pool {'depleted at round ' + str(depleted_round) if depleted_round else 'survived'} with {n} agents using '{strat_name}' strategy."
            )],
            summary={"final_pool": round(pool, 2), "total_harvested": round(total_harvested, 2),
                      "depleted": depleted_round is not None, "depleted_round": depleted_round,
                      "avg_harvest_per_agent": round(total_harvested / (n * rounds), 2),
                      "sustainability_score": round(pool / capacity, 3)},
            metadata={"compute_time_ms": round((time.time() - t0) * 1000, 2), "engine": "server"})
