"""Dynamic Coalition Formation — agents form and break alliances."""
from __future__ import annotations
import random, time
from collections import defaultdict
from app.models.schemas import GameInfo, ParameterSpec, SimulationResult, RoundData, Equilibrium
from app.simulations.base import BaseGame


class CoalitionFormation(BaseGame):
    def info(self) -> GameInfo:
        return GameInfo(
            id="coalition_formation", name="Dynamic Coalition Formation", category="innovation", tier=3,
            short_description="Agents form and break alliances — who ends up with whom?",
            long_description="N agents with different capabilities form coalitions to maximize joint value. Coalitions can merge or split each round. Payoffs are divided using the Shapley value. Explores stability, fairness, and strategic alliance formation.",
            parameters=[
                ParameterSpec(name="rounds", type="int", default=100, min=10, max=1000, description="Number of rounds"),
                ParameterSpec(name="n_agents", type="int", default=8, min=3, max=20, description="Number of agents"),
                ParameterSpec(name="synergy_factor", type="float", default=1.5, min=1.0, max=5.0, description="Value multiplier for larger coalitions"),
                ParameterSpec(name="stability", type="float", default=0.7, min=0, max=1, description="Probability of staying in current coalition"),
            ],
            available=True, engine="server", tags=["coalition", "Shapley", "cooperative"],
            theory_card="## Cooperative Game Theory\nUnlike non-cooperative games, players can form **binding agreements** and share payoffs.\n\n## The Shapley Value\nA fair division of coalition value based on each player's **marginal contribution** — it's the unique division satisfying efficiency, symmetry, and additivity.\n\n## Core Stability\nA coalition structure is **stable** (in the core) if no subgroup can do better by breaking away.\n\n## Key Insight\nLarger coalitions generate more value through **synergy**, but smaller groups may resist joining if their share is too small.",
        )

    def compute(self, config: dict) -> SimulationResult:
        t0 = time.time()
        rounds = config.get("rounds", 100)
        n = config.get("n_agents", 8)
        synergy = config.get("synergy_factor", 1.5)
        stability = config.get("stability", 0.7)

        # Agent capabilities
        capabilities = [random.uniform(1, 10) for _ in range(n)]

        # Start: each agent alone
        coalitions = [[i] for i in range(n)]
        rd = []
        payoff_history = [0.0] * n

        for r in range(1, rounds + 1):
            # Calculate coalition values
            def coal_value(members):
                base = sum(capabilities[m] for m in members)
                return base * (synergy ** (len(members) - 1)) if len(members) > 1 else base

            # Attempt merges and splits
            new_coalitions = []
            used = set()
            random.shuffle(coalitions)

            for coal in coalitions:
                if any(m in used for m in coal):
                    continue

                if random.random() < stability:
                    # Stay
                    new_coalitions.append(coal)
                    used.update(coal)
                else:
                    if len(coal) > 1 and random.random() < 0.4:
                        # Split
                        split_point = random.randint(1, len(coal) - 1)
                        random.shuffle(coal)
                        new_coalitions.append(coal[:split_point])
                        new_coalitions.append(coal[split_point:])
                        used.update(coal)
                    else:
                        # Try to merge with another
                        candidates = [c for c in coalitions if c != coal and not any(m in used for m in c)]
                        if candidates:
                            partner = random.choice(candidates)
                            merged = coal + partner
                            if coal_value(merged) > coal_value(coal) + coal_value(partner):
                                new_coalitions.append(merged)
                                used.update(merged)
                            else:
                                new_coalitions.append(coal)
                                used.update(coal)
                        else:
                            new_coalitions.append(coal)
                            used.update(coal)

            # Add any remaining unassigned agents
            for i in range(n):
                if i not in used:
                    new_coalitions.append([i])

            coalitions = new_coalitions

            # Calculate payoffs (simplified Shapley: proportional to capability)
            round_payoffs = [0.0] * n
            for coal in coalitions:
                val = coal_value(coal)
                total_cap = sum(capabilities[m] for m in coal)
                for m in coal:
                    share = val * capabilities[m] / total_cap if total_cap > 0 else 0
                    round_payoffs[m] = share
                    payoff_history[m] += share

            avg_size = n / len(coalitions) if coalitions else 1
            largest = max(len(c) for c in coalitions) if coalitions else 0
            rd.append(RoundData(round_num=r, actions=[len(c) for c in coalitions],
                payoffs=[round(p, 2) for p in round_payoffs],
                state={"n_coalitions": len(coalitions), "avg_size": round(avg_size, 2),
                       "largest_coalition": largest, "total_value": round(sum(round_payoffs), 2),
                       "coalition_sizes": sorted([len(c) for c in coalitions], reverse=True)}))

        return SimulationResult(game_id="coalition_formation", config=config, rounds=rd,
            equilibria=[Equilibrium(name="Grand Coalition", strategies=["All join"],
                payoffs=[round(sum(capabilities) * synergy ** (n - 1) / n, 1)] * min(n, 3),
                description=f"Maximum value if all {n} agents cooperate — synergy = {synergy}^{n-1}")],
            summary={"final_n_coalitions": len(coalitions),
                     "final_avg_size": round(n / len(coalitions), 2) if coalitions else 0,
                     "final_largest": max(len(c) for c in coalitions) if coalitions else 0,
                     "avg_payoff": round(sum(payoff_history) / (n * rounds), 2),
                     "value_captured_ratio": round(sum(payoff_history) / (sum(capabilities) * rounds), 3)},
            metadata={"compute_time_ms": round((time.time() - t0) * 1000, 2), "engine": "server"})
