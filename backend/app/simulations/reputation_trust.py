"""Reputation & Trust Dynamics — trust building over repeated interactions."""
from __future__ import annotations
import random, time
from app.models.schemas import GameInfo, ParameterSpec, SimulationResult, RoundData, Equilibrium
from app.simulations.base import BaseGame

STRATEGIES = {
    "always_trust": lambda _rep, _h: True,
    "never_trust": lambda _rep, _h: False,
    "threshold_50": lambda rep, _h: rep >= 0.5,
    "threshold_75": lambda rep, _h: rep >= 0.75,
    "gradual": lambda rep, h: rep >= (0.3 + len(h) * 0.005),
    "random": lambda _rep, _h: random.random() < 0.5,
}
TRUSTEE_TYPES = {
    "honest": lambda _h, _t: False,  # never betray
    "dishonest": lambda _h, _t: True,  # always betray
    "strategic": lambda h, t: t < 0.3 and len(h) > 5,  # betray when trust is low AND late
    "opportunist": lambda _h, _t: random.random() < 0.3,  # betray 30% of the time
    "reformed": lambda h, _t: len(h) > 0 and h[-1].get("betrayed", False),  # betray after being tested
    "conditional": lambda _h, t: random.random() < (1 - t) * 0.5,  # more likely to betray when trust is low
}

class ReputationTrust(BaseGame):
    def info(self) -> GameInfo:
        return GameInfo(
            id="reputation_trust", name="Reputation & Trust Dynamics", category="underrated", tier=2,
            short_description="RL agents build and exploit reputation over time.",
            long_description="A trustor decides whether to invest in a trustee based on their reputation. The trustee can honor or betray trust. Reputation updates via Bayesian learning. Explores trust-building, exploitation, and the value of reputation.",
            parameters=[
                ParameterSpec(name="rounds", type="int", default=200, min=10, max=5000, description="Number of interactions"),
                ParameterSpec(name="investment", type="float", default=10.0, min=1, max=100, description="Amount to invest per round"),
                ParameterSpec(name="multiplier", type="float", default=3.0, min=1.5, max=10, description="Investment multiplier"),
                ParameterSpec(name="trust_decay", type="float", default=0.02, min=0, max=0.2, description="Reputation decay per round"),
                ParameterSpec(name="trustor_strategy", type="select", default="threshold_50", options=list(STRATEGIES), description="Trustor strategy"),
                ParameterSpec(name="trustee_type", type="select", default="strategic", options=list(TRUSTEE_TYPES), description="Trustee type"),
            ],
            available=True, engine="server", tags=["RL", "trust", "repeated"],
            theory_card="## Trust Game\nThe trustor can invest (risky) or keep money (safe). Investment is multiplied, then the trustee decides to share or keep everything.\n\n## Reputation Building\nReputation acts as a **commitment device** — a high-reputation trustee earns more investment, creating incentive to be trustworthy.\n\n## Key Insight\n**Reputation is an asset**: the long-run value of maintaining trust often exceeds short-term gains from betrayal.",
        )

    def compute(self, config: dict) -> SimulationResult:
        t0 = time.time()
        rounds = config.get("rounds", 200)
        invest = config.get("investment", 10.0)
        mult = config.get("multiplier", 3.0)
        decay = config.get("trust_decay", 0.02)
        ts = STRATEGIES.get(config.get("trustor_strategy", "threshold_50"), STRATEGIES["threshold_50"])
        tt = TRUSTEE_TYPES.get(config.get("trustee_type", "strategic"), TRUSTEE_TYPES["honest"])
        reputation = 0.5
        rd, history = [], []
        tot_trustor = tot_trustee = invests = betrayals = 0
        for r in range(1, rounds + 1):
            trusted = ts(reputation, history)
            if trusted:
                invests += 1
                betrayed = tt(history, reputation)
                if betrayed:
                    betrayals += 1
                    p_trustor = -invest
                    p_trustee = invest * mult
                    reputation = max(0, reputation * 0.7 - 0.1)
                else:
                    returned = invest * mult / 2
                    p_trustor = returned - invest
                    p_trustee = invest * mult - returned
                    reputation = min(1, reputation + 0.05)
            else:
                betrayed = False
                p_trustor = 0
                p_trustee = 0
                reputation = max(0, reputation - decay)
            tot_trustor += p_trustor; tot_trustee += p_trustee
            entry = {"trusted": trusted, "betrayed": betrayed, "reputation": reputation}
            history.append(entry)
            rd.append(RoundData(round_num=r, actions=[trusted, betrayed], payoffs=[p_trustor, p_trustee],
                state={"reputation": round(reputation, 3), "trust_rate": invests/r, "betrayal_rate": betrayals/max(1, invests)}))
        return SimulationResult(game_id="reputation_trust", config=config, rounds=rd,
            equilibria=[Equilibrium(name="Trust Equilibrium", strategies=["Invest if rep>0.5", "Honor"], description="Trust emerges when reputation cost of betrayal exceeds short-term gain.")],
            summary={"final_reputation": round(reputation, 3), "trust_rate": invests/rounds, "betrayal_rate": betrayals/max(1, invests),
                     "avg_trustor_payoff": tot_trustor/rounds, "avg_trustee_payoff": tot_trustee/rounds, "total_investments": invests},
            metadata={"compute_time_ms": round((time.time()-t0)*1000, 2), "engine": "server"})
