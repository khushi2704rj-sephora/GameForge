"""Ultimatum Game — fairness, rejection, and behavioral economics."""
from __future__ import annotations
import random, time
from app.models.schemas import GameInfo, ParameterSpec, SimulationResult, RoundData, Equilibrium
from app.simulations.base import BaseGame

PROPOSER_STRATEGIES = {
    "fair": lambda _h: 0.5,
    "greedy": lambda _h: 0.1,
    "generous": lambda _h: 0.6,
    "random": lambda _h: round(random.uniform(0.05, 0.95), 2),
    "adaptive": lambda h: 0.5 if not h else max(0.05, min(0.95, h[-1]["offer"] + (0.05 if h[-1]["accepted"] else -0.05))),
}
RESPONDER_STRATEGIES = {
    "rational": lambda _offer, _h: True,  # always accept any positive offer
    "fair_minded": lambda offer, _h: offer >= 0.3,
    "spiteful": lambda offer, _h: offer >= 0.5,
    "random": lambda _o, _h: random.random() < 0.7,
    "adaptive": lambda offer, h: offer >= (0.3 if not h else max(0.05, sum(e["offer"] for e in h)/len(h) * 0.8)),
}

class UltimatumGame(BaseGame):
    def info(self) -> GameInfo:
        return GameInfo(
            id="ultimatum", name="Ultimatum Game", category="classical", tier=1,
            short_description="How much will you share when rejection means nothing for either side?",
            long_description="A Proposer offers a split of a pie. The Responder accepts (both get their shares) or rejects (both get nothing). Rationality predicts acceptance of any positive offer, but experiments show people reject 'unfair' offers.",
            parameters=[
                ParameterSpec(name="rounds", type="int", default=100, min=1, max=5000, description="Number of rounds"),
                ParameterSpec(name="pie_size", type="float", default=100.0, min=1, max=10000, description="Total pie to divide"),
                ParameterSpec(name="proposer_strategy", type="select", default="adaptive", options=list(PROPOSER_STRATEGIES), description="Proposer strategy"),
                ParameterSpec(name="responder_strategy", type="select", default="fair_minded", options=list(RESPONDER_STRATEGIES), description="Responder strategy"),
            ],
            available=True, engine="server", tags=["fairness", "behavioral"],
            theory_card="## Subgame-Perfect NE\nThe Proposer offers the smallest possible amount; the Responder accepts. This is the **rational** prediction.\n\n## Behavioral Reality\nIn experiments, modal offers are **40-50%** and offers below **20%** are frequently rejected — showing **fairness concerns** override pure rationality.\n\n## Key Insight\nPeople care about **fairness**, not just payoffs. Spite and inequality aversion are real forces.",
        )

    def compute(self, config: dict) -> SimulationResult:
        t0 = time.time()
        rounds = config.get("rounds", 100)
        pie = config.get("pie_size", 100.0)
        ps = PROPOSER_STRATEGIES.get(config.get("proposer_strategy", "adaptive"), PROPOSER_STRATEGIES["random"])
        rs = RESPONDER_STRATEGIES.get(config.get("responder_strategy", "fair_minded"), RESPONDER_STRATEGIES["rational"])
        history, rd = [], []
        tot_prop = tot_resp = accepts = 0
        for r in range(1, rounds + 1):
            offer_frac = ps(history)
            accepted = rs(offer_frac, history)
            if accepted:
                p_prop = pie * (1 - offer_frac)
                p_resp = pie * offer_frac
                accepts += 1
            else:
                p_prop = p_resp = 0.0
            tot_prop += p_prop; tot_resp += p_resp
            entry = {"offer": offer_frac, "accepted": accepted}
            history.append(entry)
            rd.append(RoundData(round_num=r, actions=[offer_frac, accepted], payoffs=[p_prop, p_resp],
                state={"offer": offer_frac, "accepted": accepted, "acceptance_rate": accepts / r, "avg_offer": sum(e["offer"] for e in history) / r}))
        return SimulationResult(game_id="ultimatum", config=config, rounds=rd,
            equilibria=[Equilibrium(name="Subgame-Perfect NE", strategies=["Offer ε", "Accept"], payoffs=[pie, 0], description="Proposer offers minimum; Responder accepts any positive offer.")],
            summary={"avg_offer": sum(e["offer"] for e in history)/rounds, "acceptance_rate": accepts/rounds, "total_proposer": tot_prop, "total_responder": tot_resp, "avg_payoff_proposer": tot_prop/rounds, "avg_payoff_responder": tot_resp/rounds},
            metadata={"compute_time_ms": round((time.time()-t0)*1000, 2), "engine": "server"})
