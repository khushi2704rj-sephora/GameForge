"""Cournot vs Bertrand — quantity vs price competition in oligopoly."""
from __future__ import annotations
import random, time
from app.models.schemas import GameInfo, ParameterSpec, SimulationResult, RoundData, Equilibrium
from app.simulations.base import BaseGame

class CournotBertrand(BaseGame):
    def info(self) -> GameInfo:
        return GameInfo(
            id="cournot_bertrand", name="Cournot vs. Bertrand", category="underrated", tier=2,
            short_description="Compete on quantity or price? The answer changes everything.",
            long_description="Compare Cournot (quantity) and Bertrand (price) competition. With identical products, Bertrand drives price to marginal cost while Cournot allows positive profits. Adding product differentiation changes the dynamics.",
            parameters=[
                ParameterSpec(name="simulations", type="int", default=200, min=10, max=5000, description="Market periods"),
                ParameterSpec(name="mode", type="select", default="cournot", options=["cournot", "bertrand", "both"], description="Competition mode"),
                ParameterSpec(name="n_firms", type="int", default=3, min=2, max=10, description="Number of competing firms"),
                ParameterSpec(name="demand_intercept", type="float", default=100.0, min=20, max=500, description="Demand intercept"),
                ParameterSpec(name="marginal_cost", type="float", default=20.0, min=0, max=200, description="Marginal cost"),
                ParameterSpec(name="differentiation", type="float", default=0.0, min=0, max=1, description="Product differentiation (0=identical, 1=monopoly)"),
            ],
            available=True, engine="server", tags=["oligopoly", "IO"],
            theory_card="## The Bertrand Paradox\nWith 2+ firms selling identical products, Bertrand competition drives price to **marginal cost** — yielding zero profit! Cournot allows positive profit.\n\n## Resolution\nProduct **differentiation** alleviates the paradox. With differentiated products, both modes yield interior equilibria with positive profits.\n\n## Key Insight\nThe **strategic variable** (price vs quantity) fundamentally changes competitive outcomes.",
        )

    def compute(self, config: dict) -> SimulationResult:
        t0 = time.time()
        sims = config.get("simulations", 200)
        mode = config.get("mode", "cournot")
        n_firms = config.get("n_firms", 3)
        a = config.get("demand_intercept", 100.0)
        c = config.get("marginal_cost", 20.0)
        diff = config.get("differentiation", 0.0)
        rd = []
        profits_accum = [0.0] * n_firms
        for sim in range(1, sims + 1):
            if mode in ("cournot", "both"):
                # Cournot: each firm chooses quantity
                q_cournot = (a - c) / (n_firms + 1)
                quantities = [max(0, q_cournot + random.gauss(0, q_cournot*0.1)) for _ in range(n_firms)]
                Q = sum(quantities)
                price_c = max(0, a - Q)
                profits_c = [(price_c - c) * q for q in quantities]
            if mode in ("bertrand", "both"):
                # Bertrand: each firm chooses price
                p_bertrand = c + (a - c) * diff / (n_firms - diff * (n_firms - 1)) if diff > 0 else c + 0.01
                prices = [max(c, p_bertrand + random.gauss(0, (a-c)*0.05)) for _ in range(n_firms)]
                min_price = min(prices)
                winners = [i for i, p in enumerate(prices) if abs(p - min_price) < 0.5]
                demand_each = (a - min_price) / len(winners) if winners else 0
                profits_b = [((prices[i] - c) * demand_each if i in winners else 0) for i in range(n_firms)]
            if mode == "cournot":
                profits = profits_c
                mkt_price = price_c
                actions = [round(q, 1) for q in quantities]
            elif mode == "bertrand":
                profits = profits_b
                mkt_price = min_price
                actions = [round(p, 1) for p in prices]
            else:
                profits = profits_c  # show Cournot in main
                mkt_price = price_c
                actions = [round(q, 1) for q in quantities]
            for i in range(n_firms):
                profits_accum[i] += profits[i]
            rd.append(RoundData(round_num=sim, actions=actions, payoffs=[round(p, 1) for p in profits],
                state={"price": round(mkt_price, 1), "total_profit": round(sum(profits), 1),
                       "avg_firm_profit": round(sum(profits)/n_firms, 1),
                       "hhi": round(sum((q/sum(quantities)*100)**2 for q in quantities), 0) if mode=="cournot" and sum(quantities)>0 else 0}))
        # Theoretical equilibria
        q_star = (a - c) / (n_firms + 1)
        p_cournot = a - n_firms * q_star
        return SimulationResult(game_id="cournot_bertrand", config=config, rounds=rd,
            equilibria=[
                Equilibrium(name="Cournot NE", strategies=[f"q={q_star:.0f}"]*n_firms, payoffs=[round((p_cournot-c)*q_star, 1)]*n_firms, description=f"Each firm produces {q_star:.0f}, price = {p_cournot:.0f}"),
                Equilibrium(name="Bertrand NE", strategies=[f"p={c:.0f}"], payoffs=[0], description=f"Price = marginal cost ({c:.0f}), zero profit (undifferentiated)"),
            ],
            summary={"avg_market_price": sum(r.state["price"] for r in rd)/sims,
                     "avg_firm_profit": sum(profits_accum)/n_firms/sims,
                     "total_market_profit": sum(profits_accum)/sims, "mode": mode,
                     "theoretical_cournot_profit": round((p_cournot-c)*q_star, 1)},
            metadata={"compute_time_ms": round((time.time()-t0)*1000, 2), "engine": "server"})
