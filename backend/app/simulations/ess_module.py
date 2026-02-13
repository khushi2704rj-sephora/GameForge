"""Evolutionary Stable Strategies — replicator dynamics simulation."""
from __future__ import annotations
import time, random
import numpy as np
from app.models.schemas import GameInfo, ParameterSpec, SimulationResult, RoundData, Equilibrium
from app.simulations.base import BaseGame

# Hawk-Dove game as default payoff matrix
DEFAULT_MATRIX = [
    [(-1, -1), (2, 0)],  # Hawk vs Hawk, Hawk vs Dove
    [(0, 2), (1, 1)],    # Dove vs Hawk, Dove vs Dove
]

PRESETS = {
    "hawk_dove": {"matrix": [[(-1,-1),(2,0)],[(0,2),(1,1)]], "labels": ["Hawk", "Dove"]},
    "prisoners_dilemma": {"matrix": [[(3,3),(0,5)],[(5,0),(1,1)]], "labels": ["Cooperate", "Defect"]},
    "coordination": {"matrix": [[(2,2),(0,0)],[(0,0),(1,1)]], "labels": ["A", "B"]},
    "rps_extended": {"matrix": [[(0,0),(-1,1),(1,-1)],[(1,-1),(0,0),(-1,1)],[(-1,1),(1,-1),(0,0)]], "labels": ["R","P","S"]},
}

class ESSModule(BaseGame):
    def info(self) -> GameInfo:
        return GameInfo(
            id="ess_module", name="Evolutionary Stable Strategies", category="classical", tier=1,
            short_description="Which strategies survive natural selection?",
            long_description="Simulate replicator dynamics: a population of agents with different strategies evolve based on fitness (payoffs). Track which strategies dominate over generations.",
            parameters=[
                ParameterSpec(name="generations", type="int", default=200, min=10, max=5000, description="Number of generations"),
                ParameterSpec(name="population_size", type="int", default=1000, min=50, max=10000, description="Population size"),
                ParameterSpec(name="preset", type="select", default="hawk_dove", options=list(PRESETS), description="Game preset"),
                ParameterSpec(name="mutation_rate", type="float", default=0.01, min=0, max=0.2, description="Mutation probability per generation"),
            ],
            available=True, engine="server", tags=["evolutionary", "replicator"],
            theory_card="## Replicator Dynamics\nStrategies that earn **above-average** fitness grow; below-average strategies shrink. This models Darwin's natural selection.\n\n## ESS\nAn **Evolutionarily Stable Strategy** cannot be invaded by any mutant strategy when adopted by the entire population.\n\n## Key Insight\nEvolutionary game theory connects biology and economics — explaining phenomena from animal aggression to social norms.",
        )

    def compute(self, config: dict) -> SimulationResult:
        t0 = time.time()
        gens = config.get("generations", 200)
        pop_size = config.get("population_size", 1000)
        preset_name = config.get("preset", "hawk_dove")
        mutation = config.get("mutation_rate", 0.01)
        preset = PRESETS.get(preset_name, PRESETS["hawk_dove"])
        matrix = preset["matrix"]
        labels = preset["labels"]
        n_strats = len(labels)
        # Initialize proportions evenly
        proportions = np.ones(n_strats) / n_strats
        rd = []
        for g in range(1, gens + 1):
            # Compute fitness for each strategy
            fitness = np.zeros(n_strats)
            for i in range(n_strats):
                for j in range(n_strats):
                    fitness[i] += proportions[j] * matrix[i][j][0]
            avg_fitness = np.dot(proportions, fitness)
            # Replicator dynamics
            new_props = proportions * fitness / avg_fitness if avg_fitness != 0 else proportions
            # Mutation
            if mutation > 0:
                new_props = (1 - mutation) * new_props + mutation / n_strats
            new_props = np.clip(new_props, 0, 1)
            new_props /= new_props.sum()
            proportions = new_props
            state = {f"prop_{labels[i].lower()}": float(proportions[i]) for i in range(n_strats)}
            state["avg_fitness"] = float(avg_fitness)
            rd.append(RoundData(round_num=g, actions=proportions.tolist(), payoffs=fitness.tolist(), state=state))
        # Find dominant strategy
        dominant_idx = int(np.argmax(proportions))
        dominant = labels[dominant_idx]
        equil = []
        equil.append(Equilibrium(name=f"Dominant: {dominant}", strategies=[dominant], payoffs=[float(proportions[dominant_idx])],
            description=f"After {gens} generations, {dominant} has proportion {proportions[dominant_idx]:.3f}."))
        summary = {f"final_{labels[i].lower()}_proportion": float(proportions[i]) for i in range(n_strats)}
        summary["dominant_strategy"] = dominant
        summary["final_avg_fitness"] = float(np.dot(proportions, [sum(proportions[j]*matrix[i][j][0] for j in range(n_strats)) for i in range(n_strats)]))
        return SimulationResult(game_id="ess_module", config=config, rounds=rd, equilibria=equil, summary=summary,
            metadata={"compute_time_ms": round((time.time()-t0)*1000, 2), "engine": "server"})
