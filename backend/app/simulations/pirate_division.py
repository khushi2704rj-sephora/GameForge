"""Pirate Division — sequential bargaining with elimination."""
from __future__ import annotations
import random, time
from app.models.schemas import GameInfo, ParameterSpec, SimulationResult, RoundData, Equilibrium
from app.simulations.base import BaseGame


class PirateDivision(BaseGame):
    def info(self) -> GameInfo:
        return GameInfo(
            id="pirate_division", name="Pirate Division", category="innovation", tier=3,
            short_description="How do rational pirates divide their treasure?",
            long_description=(
                "N pirates must divide gold coins by sequential proposals. The most senior pirate "
                "proposes a division; if a majority accepts, it stands. Otherwise, the proposer "
                "walks the plank and the next pirate proposes. Uses backward induction to find "
                "the subgame-perfect equilibrium — the result is shockingly unfair."
            ),
            parameters=[
                ParameterSpec(name="n_pirates", type="int", default=5, min=3, max=10, description="Number of pirates"),
                ParameterSpec(name="treasure", type="int", default=100, min=10, max=10000, description="Gold coins to divide"),
                ParameterSpec(name="simulations", type="int", default=500, min=10, max=5000, description="Simulations to run"),
                ParameterSpec(name="rationality", type="float", default=0.8, min=0.0, max=1.0, description="Probability of rational voting (vs emotional rejection)"),
            ],
            available=True, engine="server", tags=["backward-induction", "bargaining", "sequential"],
            theory_card=(
                "## The Pirate Puzzle\n"
                "This classic puzzle tests understanding of **backward induction** and **subgame perfection**.\n\n"
                "## SPNE Solution (5 pirates)\n"
                "Pirate 1 (most senior) proposes: **98, 0, 1, 0, 1** and it passes!\n"
                "Pirates 3 and 5 accept because they'd get nothing if Pirate 1 is eliminated.\n\n"
                "## Key Insight\n"
                "The proposer exploits others' **outside options** — each cheaply-bought vote costs only 1 coin."
            ),
        )

    def compute(self, config: dict) -> SimulationResult:
        t0 = time.time()
        n = config.get("n_pirates", 5)
        treasure = config.get("treasure", 100)
        sims = config.get("simulations", 500)
        rationality = config.get("rationality", 0.8)
        
        # Compute SPNE division using backward induction
        spne = self._backward_induction(n, treasure)
        
        rd = []
        acceptance_count = 0
        proposer_avg = 0
        plank_count = 0
        
        for sim in range(1, sims + 1):
            current_pirates = list(range(n))
            proposal = None
            accepted = False
            proposer_idx = 0
            
            while not accepted and len(current_pirates) > 1:
                proposer = current_pirates[0]
                # Propose: give self most, buy cheapest votes
                division = [0] * len(current_pirates)
                needed_votes = len(current_pirates) // 2  # need majority including self
                
                # Proposer takes lion's share
                bought = 0
                for i in range(len(current_pirates) - 1, 0, -1):
                    if bought < needed_votes and random.random() < 0.5:
                        division[i] = 1
                        bought += 1
                division[0] = treasure - sum(division)
                
                # Voting
                votes_for = 1  # proposer votes for self
                for i in range(1, len(current_pirates)):
                    if random.random() < rationality:
                        # Rational: accept if getting >= what they'd get next round
                        votes_for += 1 if division[i] > 0 else 0
                    else:
                        # Emotional: reject unfair proposals
                        fair_share = treasure / len(current_pirates)
                        votes_for += 1 if division[i] >= fair_share * 0.3 else 0
                
                if votes_for > len(current_pirates) / 2:
                    accepted = True
                    proposal = division
                    proposer_avg += division[0]
                    acceptance_count += 1
                else:
                    plank_count += 1
                    current_pirates.pop(0)
                    proposer_idx += 1
            
            if not accepted and len(current_pirates) == 1:
                proposal = [treasure]
                proposer_avg += treasure
                acceptance_count += 1
            
            rd.append(RoundData(
                round_num=sim, actions=proposal or [treasure],
                payoffs=[float(proposal[0]) if proposal else float(treasure)],
                state={
                    "proposer": proposer_idx, "n_remaining": len(current_pirates),
                    "accepted_first": proposer_idx == 0,
                    "acceptance_rate": round(acceptance_count / sim, 3),
                }
            ))
        
        return SimulationResult(
            game_id="pirate_division", config=config, rounds=rd,
            equilibria=[Equilibrium(
                name="SPNE Division", strategies=[str(s) for s in spne],
                description=f"Backward induction yields: {spne}. Proposer keeps {spne[0]} of {treasure} coins."
            )],
            summary={
                "spne_division": spne, "avg_proposer_share": round(proposer_avg / sims, 2),
                "first_proposal_acceptance": round(acceptance_count / sims, 3),
                "avg_planks": round(plank_count / sims, 2),
                "proposer_share_ratio": round(proposer_avg / (sims * treasure), 3),
            },
            metadata={"compute_time_ms": round((time.time() - t0) * 1000, 2), "engine": "server"})
    
    def _backward_induction(self, n: int, treasure: int) -> list[int]:
        """Compute SPNE via backward induction."""
        if n == 1:
            return [treasure]
        if n == 2:
            return [treasure, 0]
        # For n pirates, proposer buys every other pirate starting from the end
        division = [0] * n
        votes_needed = n // 2  # excluding self, need this many
        bought = 0
        for i in range(n - 1, 0, -2):
            if bought < votes_needed:
                division[i] = 1
                bought += 1
        division[0] = treasure - sum(division)
        return division
