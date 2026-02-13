"""Supply Chain Coordination — bullwhip effect simulation."""
from __future__ import annotations
import random, time
from app.models.schemas import GameInfo, ParameterSpec, SimulationResult, RoundData, Equilibrium
from app.simulations.base import BaseGame

class SupplyChain(BaseGame):
    def info(self) -> GameInfo:
        return GameInfo(
            id="supply_chain", name="Supply Chain Coordination", category="underrated", tier=2,
            short_description="Can firms tame the bullwhip effect through strategic sharing?",
            long_description="A multi-tier supply chain where demand variance amplifies upstream (the bullwhip effect). Firms choose inventory levels and can share demand information. Explores the tension between local optimization and system efficiency.",
            parameters=[
                ParameterSpec(name="rounds", type="int", default=100, min=10, max=1000, description="Number of periods"),
                ParameterSpec(name="n_tiers", type="int", default=4, min=2, max=8, description="Number of supply chain tiers"),
                ParameterSpec(name="base_demand", type="float", default=100.0, min=10, max=1000, description="Average customer demand"),
                ParameterSpec(name="demand_variance", type="float", default=15.0, min=1, max=100, description="Demand standard deviation"),
                ParameterSpec(name="info_sharing", type="select", default="none", options=["none", "partial", "full"], description="Information sharing level"),
            ],
            available=True, engine="server", tags=["operations", "coordination"],
            theory_card="## The Bullwhip Effect\nSmall demand fluctuations at retail get **amplified** upstream — each tier over-orders as a buffer, creating wild swings at the manufacturer level.\n\n## Causes\n- **Demand signal processing**: each tier forecasts from its own orders\n- **Order batching**: periodic ordering amplifies variance\n- **Shortage gaming**: over-ordering when supply is scarce\n\n## Key Insight\n**Information sharing** (sharing actual POS data) dramatically reduces the bullwhip effect, but requires trust and coordination.",
        )

    def compute(self, config: dict) -> SimulationResult:
        t0 = time.time()
        rounds = config.get("rounds", 100)
        n_tiers = config.get("n_tiers", 4)
        base = config.get("base_demand", 100.0)
        variance = config.get("demand_variance", 15.0)
        sharing = config.get("info_sharing", "none")
        tier_names = ["Retailer", "Wholesaler", "Distributor", "Manufacturer", "Raw Material", "Tier 6", "Tier 7", "Tier 8"][:n_tiers]
        inventories = [base * 2] * n_tiers
        orders_history = [[] for _ in range(n_tiers)]
        rd = []
        total_cost = [0.0] * n_tiers
        holding_cost = 0.5
        shortage_cost = 2.0
        for r in range(1, rounds + 1):
            actual_demand = max(0, random.gauss(base, variance))
            orders = [0.0] * n_tiers
            for tier in range(n_tiers):
                if tier == 0:
                    incoming_demand = actual_demand
                else:
                    incoming_demand = orders[tier - 1]
                if sharing == "full":
                    forecast = actual_demand
                elif sharing == "partial" and tier > 0:
                    forecast = (incoming_demand + actual_demand) / 2
                else:
                    forecast = incoming_demand
                # Order decision: moving average + safety stock
                recent_orders = orders_history[tier][-5:] if orders_history[tier] else [base]
                avg_recent = sum(recent_orders) / len(recent_orders)
                safety_factor = 1.0 + 0.15 * (tier + 1) if sharing != "full" else 1.05
                order = forecast * safety_factor + (forecast - avg_recent) * 0.3
                orders[tier] = max(0, order)
                orders_history[tier].append(orders[tier])
                # Inventory update
                fulfillment = min(inventories[tier], incoming_demand)
                inventories[tier] -= fulfillment
                inventories[tier] += orders[tier]  # simplified: instant delivery
                excess = max(0, inventories[tier] - base * 2)
                shortage = max(0, incoming_demand - fulfillment)
                total_cost[tier] += excess * holding_cost + shortage * shortage_cost
            # Calculate order variance ratio (bullwhip measure)
            tier_variances = []
            for tier in range(n_tiers):
                if len(orders_history[tier]) >= 5:
                    recent = orders_history[tier][-20:]
                    mean_o = sum(recent) / len(recent)
                    var_o = sum((x - mean_o) ** 2 for x in recent) / len(recent)
                    tier_variances.append(var_o)
                else:
                    tier_variances.append(0)
            bullwhip_ratio = (tier_variances[-1] / max(0.01, tier_variances[0])) if tier_variances[0] > 0 else 1.0
            rd.append(RoundData(round_num=r, actions=[round(o, 1) for o in orders], payoffs=[0] * n_tiers,
                state={"demand": round(actual_demand, 1), "orders": [round(o, 1) for o in orders],
                       "inventories": [round(i, 1) for i in inventories], "bullwhip_ratio": round(bullwhip_ratio, 2)}))
        avg_costs = [round(c / rounds, 2) for c in total_cost]
        final_bullwhip = rd[-1].state["bullwhip_ratio"] if rd else 1.0
        return SimulationResult(game_id="supply_chain", config=config, rounds=rd,
            equilibria=[Equilibrium(name="Coordinated Optimum", strategies=["Full info sharing"], description=f"Info sharing = '{sharing}' → bullwhip ratio ≈ {final_bullwhip:.1f}")],
            summary={"bullwhip_ratio": final_bullwhip, "avg_cost_per_tier": sum(avg_costs)/n_tiers,
                     **{f"cost_{tier_names[i].lower()}": avg_costs[i] for i in range(n_tiers)},
                     "info_sharing": sharing},
            metadata={"compute_time_ms": round((time.time()-t0)*1000, 2), "engine": "server"})
