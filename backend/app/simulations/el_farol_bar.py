"""El Farol Bar Problem — minority game and bounded rationality."""
from __future__ import annotations
import random, time
from app.models.schemas import GameInfo, ParameterSpec, SimulationResult, RoundData, Equilibrium
from app.simulations.base import BaseGame


class ElFarolBar(BaseGame):
    def info(self) -> GameInfo:
        return GameInfo(
            id="el_farol_bar", name="El Farol Bar Problem", category="innovation", tier=3,
            short_description="Should you go to the bar tonight? It depends on what everyone else does.",
            long_description=(
                "100 agents independently decide whether to go to El Farol Bar on Thursday. "
                "If fewer than 60 attend, those who go enjoy themselves; if 60+ attend, "
                "it's overcrowded and staying home was better. No equilibrium in pure strategies — "
                "agents use inductive reasoning with multiple prediction models."
            ),
            parameters=[
                ParameterSpec(name="n_agents", type="int", default=100, min=20, max=500, description="Number of agents"),
                ParameterSpec(name="threshold", type="float", default=0.6, min=0.3, max=0.9, description="Overcrowding threshold (fraction)"),
                ParameterSpec(name="rounds", type="int", default=100, min=10, max=500, description="Weeks to simulate"),
                ParameterSpec(name="n_strategies", type="int", default=5, min=2, max=10, description="Prediction strategies per agent"),
                ParameterSpec(name="memory", type="int", default=5, min=2, max=20, description="Rounds of history to use"),
            ],
            available=True, engine="server", tags=["minority-game", "bounded-rationality", "complexity", "inductive"],
            theory_card=(
                "## Arthur's El Farol (1994)\n"
                "Brian Arthur introduced this problem to show that **deductive reasoning fails** "
                "when agents' predictions affect the outcome they're predicting.\n\n"
                "## Inductive Reasoning\n"
                "Agents maintain multiple prediction models and use whichever has been most accurate "
                "recently — a form of **bounded rationality**.\n\n"
                "## Emergent Equilibrium\n"
                "Attendance self-organizes around the threshold (~60%) — "
                "a remarkable example of **complex adaptive systems**. No agent \"solves\" the game, "
                "but collective behavior is near-optimal."
            ),
        )

    def compute(self, config: dict) -> SimulationResult:
        t0 = time.time()
        n = config.get("n_agents", 100)
        threshold_frac = config.get("threshold", 0.6)
        rounds = config.get("rounds", 100)
        n_strats = config.get("n_strategies", 5)
        memory = config.get("memory", 5)
        threshold = int(n * threshold_frac)
        
        # Each agent has n_strats prediction strategies
        # Strategies are simple functions of recent attendance history
        agent_strategies = []
        for _ in range(n):
            strats = []
            for _ in range(n_strats):
                kind = random.choice(["mean", "last", "trend", "cycle", "contrarian"])
                strats.append(kind)
            agent_strategies.append(strats)
        
        agent_best_strat = [0] * n  # index of best strategy per agent
        strat_scores = [[0.0] * n_strats for _ in range(n)]
        
        attendance_history = [int(n * 0.5)]  # seed with 50%
        rd = []
        
        for r in range(1, rounds + 1):
            decisions = []
            for agent in range(n):
                # Use best-performing strategy to predict attendance
                pred = self._predict(agent_strategies[agent][agent_best_strat[agent]], attendance_history[-memory:], n)
                go = pred < threshold
                decisions.append(1 if go else 0)
            
            attendance = sum(decisions)
            overcrowded = attendance >= threshold
            
            # Score each strategy for each agent
            for agent in range(n):
                for s_idx in range(n_strats):
                    pred = self._predict(agent_strategies[agent][s_idx], attendance_history[-memory:], n)
                    pred_go = pred < threshold
                    if overcrowded:
                        strat_scores[agent][s_idx] += 1.0 if not pred_go else -1.0
                    else:
                        strat_scores[agent][s_idx] += 1.0 if pred_go else -0.5
                agent_best_strat[agent] = max(range(n_strats), key=lambda s: strat_scores[agent][s])
            
            attendance_history.append(attendance)
            
            rd.append(RoundData(
                round_num=r, actions=[attendance],
                payoffs=[1.0 if not overcrowded else -1.0],
                state={
                    "attendance": attendance, "overcrowded": overcrowded,
                    "attendance_rate": round(attendance / n, 3),
                    "distance_from_threshold": attendance - threshold,
                    "avg_attendance": round(sum(attendance_history[1:]) / r, 1),
                }
            ))
        
        avg_att = sum(attendance_history[1:]) / rounds
        overcrowded_weeks = sum(1 for a in attendance_history[1:] if a >= threshold)
        
        return SimulationResult(
            game_id="el_farol_bar", config=config, rounds=rd,
            equilibria=[Equilibrium(
                name="Self-Organized Equilibrium", strategies=[f"~{threshold_frac:.0%} attendance"],
                description=f"Average attendance: {avg_att:.1f}/{n} ({avg_att/n:.1%}). Threshold: {threshold}. Overcrowded {overcrowded_weeks}/{rounds} weeks."
            )],
            summary={
                "avg_attendance": round(avg_att, 1), "avg_attendance_rate": round(avg_att / n, 3),
                "overcrowded_fraction": round(overcrowded_weeks / rounds, 3),
                "threshold": threshold, "std_attendance": round(
                    (sum((a - avg_att)**2 for a in attendance_history[1:]) / rounds) ** 0.5, 2),
                "convergence": abs(avg_att / n - threshold_frac) < 0.1,
            },
            metadata={"compute_time_ms": round((time.time() - t0) * 1000, 2), "engine": "server"})
    
    def _predict(self, strategy: str, history: list[int], n: int) -> int:
        if not history:
            return n // 2
        if strategy == "mean":
            return int(sum(history) / len(history))
        elif strategy == "last":
            return history[-1]
        elif strategy == "trend":
            if len(history) < 2:
                return history[-1]
            delta = history[-1] - history[-2]
            return max(0, min(n, history[-1] + delta))
        elif strategy == "cycle":
            return history[-(min(3, len(history)))]
        elif strategy == "contrarian":
            return n - history[-1]
        return n // 2
