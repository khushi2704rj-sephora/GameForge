"""Bayesian Signaling Game — costly signals under information asymmetry."""
from __future__ import annotations
import random, time
from app.models.schemas import GameInfo, ParameterSpec, SimulationResult, RoundData, Equilibrium
from app.simulations.base import BaseGame

class BayesianSignaling(BaseGame):
    def info(self) -> GameInfo:
        return GameInfo(
            id="bayesian_signaling", name="Bayesian Signaling Game", category="underrated", tier=2,
            short_description="Costly signals under information asymmetry.",
            long_description="A sender has private type (High or Low quality). They choose a costly signal level. A receiver observes the signal and decides whether to accept. High types benefit more from signaling. Models education as signaling (Spence 1973).",
            parameters=[
                ParameterSpec(name="simulations", type="int", default=500, min=10, max=5000, description="Number of interactions"),
                ParameterSpec(name="high_type_prob", type="float", default=0.4, min=0.05, max=0.95, description="Probability sender is High type"),
                ParameterSpec(name="signal_cost_low", type="float", default=2.0, min=0.1, max=10, description="Cost per unit of signal for Low type"),
                ParameterSpec(name="signal_cost_high", type="float", default=0.5, min=0.1, max=10, description="Cost per unit of signal for High type"),
                ParameterSpec(name="acceptance_threshold", type="float", default=3.0, min=0, max=20, description="Signal level above which receiver accepts"),
            ],
            available=True, engine="server", tags=["information", "signaling"],
            theory_card="## Spence Signaling Model (1973)\nMichael Spence showed that **education** can serve as a signal of ability even if it has no productive value — because high-ability workers find it **cheaper** to acquire.\n\n## Separating vs Pooling\n- **Separating equilibrium**: High types signal, Low types don't\n- **Pooling equilibrium**: Both types choose the same signal\n\n## Key Insight\nSignals are valuable precisely because they are **costly** — cheap talk is not credible.",
        )

    def compute(self, config: dict) -> SimulationResult:
        t0 = time.time()
        sims = config.get("simulations", 500)
        p_high = config.get("high_type_prob", 0.4)
        cost_low = config.get("signal_cost_low", 2.0)
        cost_high = config.get("signal_cost_high", 0.5)
        threshold = config.get("acceptance_threshold", 3.0)
        prize = 10.0  # value of acceptance
        rd = []
        results = {"tp": 0, "fp": 0, "tn": 0, "fn": 0}
        payoffs_sum = 0.0
        for sim in range(1, sims + 1):
            is_high = random.random() < p_high
            # Sender chooses signal level
            cost = cost_high if is_high else cost_low
            # Optimal signal: send if prize - cost * threshold > 0
            if prize - cost * threshold > 0:
                signal = threshold + random.uniform(0, 2)  # signal above threshold
            else:
                signal = random.uniform(0, threshold * 0.5)  # low signal
            accepted = signal >= threshold
            if is_high and accepted: results["tp"] += 1
            elif not is_high and accepted: results["fp"] += 1
            elif is_high and not accepted: results["fn"] += 1
            else: results["tn"] += 1
            sender_payoff = (prize if accepted else 0) - cost * signal
            payoffs_sum += sender_payoff
            rd.append(RoundData(round_num=sim, actions=[round(signal, 2), accepted], payoffs=[round(sender_payoff, 2), 0],
                state={"is_high": is_high, "signal": round(signal, 2), "accepted": accepted,
                       "accuracy": (results["tp"] + results["tn"]) / sim,
                       "separation_rate": 1 - (results["fp"] + results["fn"]) / sim}))
        total = sims
        accuracy = (results["tp"] + results["tn"]) / total
        high_signal_rate = (results["tp"] + results["fn"]) / max(1, results["tp"] + results["fn"] + results["fp"] + results["tn"])
        return SimulationResult(game_id="bayesian_signaling", config=config, rounds=rd,
            equilibria=[Equilibrium(name="Separating Equilibrium", strategies=["High signals, Low doesn't"], payoffs=[], description=f"When cost_low ({cost_low}) > cost_high ({cost_high}), high types can credibly separate.")],
            summary={"accuracy": accuracy, "true_positive_rate": results["tp"]/max(1, results["tp"]+results["fn"]),
                     "false_positive_rate": results["fp"]/max(1, results["fp"]+results["tn"]),
                     "avg_sender_payoff": payoffs_sum/sims, "high_type_ratio": (results["tp"]+results["fn"])/total},
            metadata={"compute_time_ms": round((time.time()-t0)*1000, 2), "engine": "server"})
