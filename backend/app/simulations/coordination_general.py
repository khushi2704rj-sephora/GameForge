"""Generalized Coordination — N-player coordination with multiple equilibria."""
from __future__ import annotations
import random, time, math
from collections import Counter
from app.models.schemas import GameInfo, ParameterSpec, SimulationResult, RoundData, Equilibrium
from app.simulations.base import BaseGame


def _majority_follow(h, n_act, _id):
    if h and "actions" in h[-1]:
        flat = []
        for a in h[-1]["actions"]:
            if isinstance(a, int):
                flat.append(a)
        if flat:
            return Counter(flat).most_common(1)[0][0]
    return random.randint(0, n_act - 1)


def _best_response(h, n_act, _id):
    if h and "actions" in h[-1]:
        flat = []
        for a in h[-1]["actions"]:
            if isinstance(a, int):
                flat.append(a)
        if flat:
            return max(range(n_act), key=lambda a: sum(1 for x in flat if x == a))
    return random.randint(0, n_act - 1)


STRATEGIES = {
    "random": lambda _h, n_act, _id: random.randint(0, n_act - 1),
    "focal_0": lambda _h, _n, _id: 0,
    "majority_follow": _majority_follow,
    "stubborn": lambda _h, _n, pid: pid % 3,
    "best_response": _best_response,
}


class CoordinationGeneral(BaseGame):
    def info(self) -> GameInfo:
        return GameInfo(
            id="coordination_general", name="Generalized Coordination", category="underrated", tier=2,
            short_description="N-player coordination with multiple equilibria.",
            long_description="N players simultaneously choose from K actions. Payoff increases with the number of players choosing the same action. Multiple equilibria exist — which one emerges depends on history, focal points, and learning.",
            parameters=[
                ParameterSpec(name="rounds", type="int", default=100, min=10, max=2000, description="Number of rounds"),
                ParameterSpec(name="n_players", type="int", default=20, min=3, max=100, description="Number of players"),
                ParameterSpec(name="n_actions", type="int", default=3, min=2, max=10, description="Number of available actions"),
                ParameterSpec(name="strategy", type="select", default="best_response", options=list(STRATEGIES), description="Strategy for all players"),
                ParameterSpec(name="coordination_bonus", type="float", default=2.0, min=0.5, max=10, description="Payoff multiplier for coordination"),
            ],
            available=True, engine="server", tags=["coordination", "multi-equilibria"],
            theory_card="## Multiple Equilibria\nAny unanimous action profile is a Nash equilibrium — K actions means K pure NE.\n\n## Focal Points (Schelling)\nWith no communication, players rely on **focal points** — culturally or contextually salient choices.\n\n## Key Insight\n**History and convention** shape which equilibrium emerges. Once coordination is achieved, it's self-reinforcing.",
        )

    def compute(self, config: dict) -> SimulationResult:
        t0 = time.time()
        rounds = config.get("rounds", 100)
        n_p = config.get("n_players", 20)
        n_a = config.get("n_actions", 3)
        bonus = config.get("coordination_bonus", 2.0)
        strat_name = config.get("strategy", "best_response")
        strat = STRATEGIES.get(strat_name, STRATEGIES["random"])

        rd, history = [], []
        total_welfare = 0.0

        for r in range(1, rounds + 1):
            actions = [strat(history, n_a, i) for i in range(n_p)]
            counts = Counter(actions)

            # Payoff: base + bonus * (fraction of players choosing same action)
            payoffs_list = [1.0 + bonus * (counts[a] - 1) / max(1, n_p - 1) for a in actions]
            avg_payoff = sum(payoffs_list) / n_p
            total_welfare += sum(payoffs_list)

            dominant = counts.most_common(1)[0]
            coordination_rate = dominant[1] / n_p

            # Shannon entropy
            entropy = -sum((c / n_p) * math.log2(c / n_p) for c in counts.values() if c > 0)

            entry = {"actions": actions, "counts": dict(counts)}
            history.append(entry)

            rd.append(RoundData(round_num=r, actions=[dict(counts)], payoffs=[round(avg_payoff, 2)],
                state={"coordination_rate": round(coordination_rate, 3),
                       "dominant_action": dominant[0],
                       "entropy": round(entropy, 3),
                       "avg_payoff": round(avg_payoff, 2),
                       "n_active_actions": len(counts)}))

        # Final coordination state
        final_counts = Counter(history[-1]["actions"]) if history else Counter()
        final_dominant = final_counts.most_common(1)[0] if final_counts else (0, 0)

        convergence_round = rounds
        for rdata in rd:
            if rdata.state["coordination_rate"] > 0.8:
                convergence_round = rdata.round_num
                break

        return SimulationResult(game_id="coordination_general", config=config, rounds=rd,
            equilibria=[Equilibrium(
                name=f"Emergent: Action {final_dominant[0]}",
                strategies=[str(final_dominant[0])] * min(n_p, 3),
                payoffs=[round(1 + bonus, 2)] * min(n_p, 3),
                description=f"Action {final_dominant[0]} attracted {final_dominant[1]}/{n_p} players ({100 * final_dominant[1] / n_p:.0f}%)")],
            summary={"final_coordination_rate": round(final_dominant[1] / n_p, 3),
                     "dominant_action": final_dominant[0],
                     "avg_welfare": round(total_welfare / (rounds * n_p), 2),
                     "convergence_round": convergence_round},
            metadata={"compute_time_ms": round((time.time() - t0) * 1000, 2), "engine": "server"})
