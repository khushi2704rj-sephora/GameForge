"""Stackelberg Competition — sequential quantity leadership."""
from __future__ import annotations
import random, time
from app.models.schemas import GameInfo, ParameterSpec, SimulationResult, RoundData, Equilibrium
from app.simulations.base import BaseGame

LEADER_STRATEGIES = {
    "stackelberg_optimal": lambda a, c, _h: (a - c) / 2,
    "cournot_naive": lambda a, c, _h: (a - c) / 3,
    "aggressive": lambda a, c, _h: (a - c) * 0.6,
    "cautious": lambda a, c, _h: (a - c) * 0.3,
    "adaptive": lambda a, c, h: (a - c) / 2 if not h else max(0, h[-1]["q1"] + random.uniform(-5, 5)),
}
FOLLOWER_STRATEGIES = {
    "best_response": lambda a, c, q1: max(0, (a - c - q1) / 2),
    "match_leader": lambda _a, _c, q1: q1,
    "undercut": lambda _a, _c, q1: q1 * 0.8,
    "random": lambda a, c, _q1: random.uniform(0, (a - c) / 2),
}

class Stackelberg(BaseGame):
    def info(self) -> GameInfo:
        return GameInfo(
            id="stackelberg", name="Stackelberg Competition", category="underrated", tier=2,
            short_description="First-mover advantage in sequential oligopoly.",
            long_description="A leader firm sets quantity first; a follower observes and responds. The leader exploits their first-mover advantage through strategic commitment. Compares Stackelberg, Cournot, and collusive outcomes.",
            parameters=[
                ParameterSpec(name="simulations", type="int", default=200, min=10, max=5000, description="Market periods"),
                ParameterSpec(name="demand_intercept", type="float", default=100.0, min=20, max=500, description="Demand intercept (a)"),
                ParameterSpec(name="marginal_cost", type="float", default=20.0, min=0, max=200, description="Marginal cost (same for both)"),
                ParameterSpec(name="leader_strategy", type="select", default="stackelberg_optimal", options=list(LEADER_STRATEGIES), description="Leader's quantity strategy"),
                ParameterSpec(name="follower_strategy", type="select", default="best_response", options=list(FOLLOWER_STRATEGIES), description="Follower's response"),
            ],
            available=True, engine="server", tags=["oligopoly", "sequential"],
            theory_card="## First-Mover Advantage\nThe Stackelberg leader produces **more** than a Cournot duopolist and earns **higher profits** — by committing first, they constrain the follower.\n\n## Stackelberg vs Cournot\n- Stackelberg leader: q₁ = (a-c)/2, Follower: q₂ = (a-c)/4\n- Cournot: each produces (a-c)/3\n\n## Key Insight\n**Commitment power** is valuable — being able to move first and credibly commit gives strategic advantage.",
        )

    def compute(self, config: dict) -> SimulationResult:
        t0 = time.time()
        sims = config.get("simulations", 200)
        a = config.get("demand_intercept", 100.0)
        c = config.get("marginal_cost", 20.0)
        ls = LEADER_STRATEGIES.get(config.get("leader_strategy", "stackelberg_optimal"), LEADER_STRATEGIES["stackelberg_optimal"])
        fs = FOLLOWER_STRATEGIES.get(config.get("follower_strategy", "best_response"), FOLLOWER_STRATEGIES["best_response"])
        rd, history = [], []
        tot_leader = tot_follower = 0
        for sim in range(1, sims + 1):
            q1 = max(0, ls(a, c, history))
            q2 = max(0, fs(a, c, q1))
            Q = q1 + q2
            price = max(0, a - Q)
            profit1 = (price - c) * q1
            profit2 = (price - c) * q2
            tot_leader += profit1; tot_follower += profit2
            entry = {"q1": q1, "q2": q2, "price": price}
            history.append(entry)
            rd.append(RoundData(round_num=sim, actions=[round(q1,1), round(q2,1)], payoffs=[round(profit1,1), round(profit2,1)],
                state={"price": round(price,1), "total_quantity": round(Q,1), "leader_share": round(q1/Q,3) if Q>0 else 0}))
        # Theoretical Stackelberg
        q1_star = (a - c) / 2
        q2_star = (a - c) / 4
        p_star = a - q1_star - q2_star
        return SimulationResult(game_id="stackelberg", config=config, rounds=rd,
            equilibria=[Equilibrium(name="Stackelberg SPE", strategies=[f"q₁={q1_star:.0f}", f"q₂={q2_star:.0f}"], payoffs=[round((p_star-c)*q1_star,1), round((p_star-c)*q2_star,1)], description=f"Leader produces {q1_star:.0f}, Follower responds {q2_star:.0f}.")],
            summary={"avg_leader_profit": tot_leader/sims, "avg_follower_profit": tot_follower/sims, "avg_price": sum(h["price"] for h in history)/sims,
                     "leader_quantity_share": sum(h["q1"]/(h["q1"]+h["q2"]) for h in history if h["q1"]+h["q2"]>0)/sims,
                     "total_market_profit": (tot_leader+tot_follower)/sims},
            metadata={"compute_time_ms": round((time.time()-t0)*1000, 2), "engine": "server"})
