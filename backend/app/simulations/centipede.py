"""Centipede Game — sequential backward induction vs. cooperative behavior."""
from __future__ import annotations
import random, time
from app.models.schemas import GameInfo, ParameterSpec, SimulationResult, RoundData, Equilibrium
from app.simulations.base import BaseGame

STRATEGIES = {
    "always_take": lambda _stage, _max: True,
    "always_pass": lambda _stage, _max: False,
    "backward_induction": lambda stage, max_s: stage >= max_s - 1,
    "random": lambda _s, _m: random.random() < 0.3,
    "pass_until_half": lambda stage, max_s: stage >= max_s // 2,
    "pass_until_80pct": lambda stage, max_s: stage >= int(max_s * 0.8),
    "generous": lambda stage, max_s: stage >= max_s - 2,
}

class CentipedeGame(BaseGame):
    def info(self) -> GameInfo:
        return GameInfo(
            id="centipede", name="Centipede Game", category="classical", tier=1,
            short_description="Pass or take? Backward induction vs. real behavior.",
            long_description="Two players alternate: each can Take (end game, grab larger share) or Pass (continue, pot grows). Backward induction says Take immediately, but experiments show players often pass for several rounds.",
            parameters=[
                ParameterSpec(name="max_stages", type="int", default=10, min=2, max=50, description="Maximum stages in the centipede"),
                ParameterSpec(name="simulations", type="int", default=200, min=1, max=5000, description="Number of game repetitions"),
                ParameterSpec(name="growth_rate", type="float", default=2.0, min=1.1, max=5.0, description="Pot multiplier per stage"),
                ParameterSpec(name="strategy_p1", type="select", default="pass_until_80pct", options=list(STRATEGIES), description="Player 1 strategy"),
                ParameterSpec(name="strategy_p2", type="select", default="pass_until_half", options=list(STRATEGIES), description="Player 2 strategy"),
            ],
            available=True, engine="server", tags=["sequential", "backward-induction"],
            theory_card="## Backward Induction Paradox\nRational players should **Take at stage 1** — but this wastes the pot's exponential growth. Experiments show most players pass for several rounds.\n\n## Key Insight\nThe gap between theory and behavior reveals bounded rationality and other-regarding preferences.",
        )

    def compute(self, config: dict) -> SimulationResult:
        t0 = time.time()
        max_stages = config.get("max_stages", 10)
        sims = config.get("simulations", 200)
        growth = config.get("growth_rate", 2.0)
        s1 = STRATEGIES.get(config.get("strategy_p1", "pass_until_80pct"), STRATEGIES["random"])
        s2 = STRATEGIES.get(config.get("strategy_p2", "pass_until_half"), STRATEGIES["random"])
        rd, stop_stages = [], []
        tot1 = tot2 = 0
        for sim in range(1, sims + 1):
            pot = 1.0
            stop_stage = max_stages
            for stage in range(max_stages):
                pot = 1.0 * (growth ** stage)
                current_player = stage % 2  # 0=P1, 1=P2
                take = s1(stage, max_stages) if current_player == 0 else s2(stage, max_stages)
                if take:
                    stop_stage = stage
                    break
            taker = stop_stage % 2
            final_pot = growth ** stop_stage
            p_taker = final_pot * 0.6
            p_other = final_pot * 0.4
            p1 = p_taker if taker == 0 else p_other
            p2 = p_other if taker == 0 else p_taker
            tot1 += p1; tot2 += p2
            stop_stages.append(stop_stage)
            rd.append(RoundData(round_num=sim, actions=[stop_stage, taker], payoffs=[p1, p2],
                state={"stop_stage": stop_stage, "pot_at_stop": final_pot, "avg_stop": sum(stop_stages)/sim}))
        return SimulationResult(game_id="centipede", config=config, rounds=rd,
            equilibria=[Equilibrium(name="SPNE (Backward Induction)", strategies=["Take at stage 0"], payoffs=[0.6, 0.4], description="Take immediately — the backward-induction prediction.")],
            summary={"avg_stop_stage": sum(stop_stages)/sims, "max_possible_stage": max_stages, "avg_payoff_p1": tot1/sims, "avg_payoff_p2": tot2/sims, "avg_pot_at_stop": sum(growth**s for s in stop_stages)/sims, "reach_end_rate": sum(1 for s in stop_stages if s >= max_stages-1)/sims},
            metadata={"compute_time_ms": round((time.time()-t0)*1000, 2), "engine": "server"})
