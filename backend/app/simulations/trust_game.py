"""Trust Game — sequential investment with reciprocity."""
from __future__ import annotations
import random, time
from app.models.schemas import GameInfo, ParameterSpec, SimulationResult, RoundData, Equilibrium
from app.simulations.base import BaseGame

INVESTOR_STRATEGIES = {
    "trusting": lambda _h: 0.8,
    "cautious": lambda _h: 0.3,
    "adaptive": lambda h: 0.5 if not h else min(1.0, max(0.1, sum(h[-5:]) / len(h[-5:]))),
    "random": lambda _h: random.uniform(0.1, 0.9),
    "tit_for_tat": lambda h: h[-1] if h else 0.5,
}

TRUSTEE_STRATEGIES = {
    "reciprocal": lambda sent: min(1.0, sent * 1.2),
    "selfish": lambda _sent: 0.1,
    "fair": lambda _sent: 0.5,
    "generous": lambda sent: min(1.0, sent + 0.2),
    "random": lambda _sent: random.uniform(0.0, 0.8),
}


class TrustGame(BaseGame):
    def info(self) -> GameInfo:
        return GameInfo(
            id="trust_game", name="Trust Game", category="underrated", tier=2,
            short_description="Send money to a stranger. Will they return it?",
            long_description=(
                "The Investor receives an endowment and decides how much to send to the Trustee. "
                "The amount is tripled by an external mechanism. The Trustee then decides how much "
                "to return. Subgame-perfect equilibrium predicts zero trust, but experiments show "
                "substantial investment — revealing the role of trust, reciprocity, and social norms."
            ),
            parameters=[
                ParameterSpec(name="rounds", type="int", default=200, min=10, max=2000, description="Rounds to play"),
                ParameterSpec(name="endowment", type="float", default=10.0, min=1, max=100, description="Investor endowment per round"),
                ParameterSpec(name="multiplier", type="float", default=3.0, min=1.5, max=5, description="Trust multiplier"),
                ParameterSpec(name="investor_strategy", type="select", default="adaptive", options=list(INVESTOR_STRATEGIES), description="Investor strategy"),
                ParameterSpec(name="trustee_strategy", type="select", default="reciprocal", options=list(TRUSTEE_STRATEGIES), description="Trustee strategy"),
            ],
            available=True, engine="server", tags=["trust", "reciprocity", "sequential", "behavioral"],
            theory_card=(
                "## Berg, Dickhaut & McCabe (1995)\n"
                "The Trust Game demonstrates that **backward induction predicts zero investment**, "
                "but real humans consistently send ~50% of their endowment.\n\n"
                "## Reciprocity\n"
                "Trustees return roughly proportional amounts — supporting theories of "
                "**strong reciprocity** and **inequity aversion**.\n\n"
                "## Applications\n"
                "- Contract enforcement without courts\n"
                "- International trade trust\n"
                "- Online marketplace reputation systems"
            ),
        )

    def compute(self, config: dict) -> SimulationResult:
        t0 = time.time()
        rounds = config.get("rounds", 200)
        endowment = config.get("endowment", 10.0)
        mult = config.get("multiplier", 3.0)
        inv_fn = INVESTOR_STRATEGIES.get(config.get("investor_strategy", "adaptive"), INVESTOR_STRATEGIES["adaptive"])
        tru_fn = TRUSTEE_STRATEGIES.get(config.get("trustee_strategy", "reciprocal"), TRUSTEE_STRATEGIES["reciprocal"])
        
        rd = []
        return_history = []
        tot_inv = tot_tru = 0
        
        for r in range(1, rounds + 1):
            send_frac = inv_fn(return_history)
            sent = endowment * send_frac
            tripled = sent * mult
            return_frac = tru_fn(send_frac)
            returned = tripled * return_frac
            
            inv_payoff = (endowment - sent) + returned
            tru_payoff = tripled - returned
            tot_inv += inv_payoff
            tot_tru += tru_payoff
            return_history.append(return_frac)
            
            rd.append(RoundData(
                round_num=r, actions=[round(send_frac, 3), round(return_frac, 3)],
                payoffs=[round(inv_payoff, 2), round(tru_payoff, 2)],
                state={
                    "sent": round(sent, 2), "tripled": round(tripled, 2), "returned": round(returned, 2),
                    "avg_trust": round(sum(return_history) / r, 3),
                    "cumulative_inv": round(tot_inv, 2), "cumulative_tru": round(tot_tru, 2)
                }
            ))
        
        avg_trust = sum(return_history) / rounds
        return SimulationResult(
            game_id="trust_game", config=config, rounds=rd,
            equilibria=[Equilibrium(
                name="SPNE vs Observed", strategies=["send 0%", "return 0%"],
                description=f"SPNE: zero trust. Observed: {avg_trust:.1%} average reciprocity rate."
            )],
            summary={
                "avg_investor_payoff": round(tot_inv / rounds, 2),
                "avg_trustee_payoff": round(tot_tru / rounds, 2),
                "avg_trust_level": round(avg_trust, 3),
                "total_surplus_created": round((tot_inv + tot_tru) / rounds, 2),
                "efficiency": round((tot_inv + tot_tru) / (rounds * endowment * mult), 3),
            },
            metadata={"compute_time_ms": round((time.time() - t0) * 1000, 2), "engine": "server"})
