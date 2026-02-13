"""Voting Game — Plurality vs Borda vs Approval voting systems."""
from __future__ import annotations
import random, time
from app.models.schemas import GameInfo, ParameterSpec, SimulationResult, RoundData, Equilibrium
from app.simulations.base import BaseGame


class VotingGame(BaseGame):
    def info(self) -> GameInfo:
        return GameInfo(
            id="voting_game", name="Voting Game", category="underrated", tier=2,
            short_description="How does the voting system change the winner?",
            long_description=(
                "Simulate elections with N voters and M candidates under different voting systems: "
                "Plurality (first-past-the-post), Borda Count (ranked scoring), and Approval voting. "
                "Explores Arrow's Impossibility Theorem, strategic voting, and Condorcet paradoxes."
            ),
            parameters=[
                ParameterSpec(name="n_voters", type="int", default=100, min=10, max=1000, description="Number of voters"),
                ParameterSpec(name="n_candidates", type="int", default=4, min=3, max=8, description="Number of candidates"),
                ParameterSpec(name="simulations", type="int", default=200, min=10, max=2000, description="Elections to simulate"),
                ParameterSpec(name="strategic_fraction", type="float", default=0.2, min=0.0, max=1.0, description="Fraction of strategic voters"),
            ],
            available=True, engine="server", tags=["voting", "social-choice", "arrow", "mechanism-design"],
            theory_card=(
                "## Arrow's Impossibility Theorem (1951)\n"
                "No ranked voting system can simultaneously satisfy all fairness criteria "
                "(unanimity, independence of irrelevant alternatives, non-dictatorship).\n\n"
                "## Condorcet Paradox\n"
                "Collective preferences can be **cyclic** even when individual preferences are rational. "
                "A > B > C > A is possible in majority voting.\n\n"
                "## Gibbard-Satterthwaite Theorem\n"
                "Any deterministic voting system with ≥3 candidates is susceptible to **strategic manipulation**."
            ),
        )

    def compute(self, config: dict) -> SimulationResult:
        t0 = time.time()
        n_voters = config.get("n_voters", 100)
        n_cands = config.get("n_candidates", 4)
        sims = config.get("simulations", 200)
        strategic_frac = config.get("strategic_fraction", 0.2)
        
        cand_names = [chr(65 + i) for i in range(n_cands)]  # A, B, C, D...
        plurality_wins = {c: 0 for c in cand_names}
        borda_wins = {c: 0 for c in cand_names}
        approval_wins = {c: 0 for c in cand_names}
        agreements = 0
        condorcet_exists_count = 0
        rd = []
        
        for sim in range(1, sims + 1):
            # Generate voter preferences (random rankings)
            preferences = []
            for _ in range(n_voters):
                pref = list(cand_names)
                random.shuffle(pref)
                preferences.append(pref)
            
            # Plurality: count first-choice votes
            plurality_scores = {c: 0 for c in cand_names}
            for pref in preferences:
                plurality_scores[pref[0]] += 1
            plurality_winner = max(plurality_scores, key=plurality_scores.get)
            plurality_wins[plurality_winner] += 1
            
            # Borda: assign points (n-1 for 1st, n-2 for 2nd, etc.)
            borda_scores = {c: 0 for c in cand_names}
            for pref in preferences:
                for rank, c in enumerate(pref):
                    borda_scores[c] += (n_cands - 1 - rank)
            borda_winner = max(borda_scores, key=borda_scores.get)
            borda_wins[borda_winner] += 1
            
            # Approval: each voter approves top ceil(n/2) candidates
            approval_scores = {c: 0 for c in cand_names}
            approve_count = max(1, n_cands // 2)
            for pref in preferences:
                for c in pref[:approve_count]:
                    approval_scores[c] += 1
            approval_winner = max(approval_scores, key=approval_scores.get)
            approval_wins[approval_winner] += 1
            
            all_agree = plurality_winner == borda_winner == approval_winner
            if all_agree:
                agreements += 1
            
            # Check Condorcet winner
            condorcet_winner = None
            for c in cand_names:
                beats_all = True
                for d in cand_names:
                    if c == d:
                        continue
                    c_beats_d = sum(1 for pref in preferences if pref.index(c) < pref.index(d))
                    if c_beats_d <= n_voters / 2:
                        beats_all = False
                        break
                if beats_all:
                    condorcet_winner = c
                    break
            if condorcet_winner:
                condorcet_exists_count += 1
            
            rd.append(RoundData(
                round_num=sim, actions=[plurality_winner, borda_winner, approval_winner],
                payoffs=[float(all_agree)],
                state={
                    "plurality": plurality_scores, "borda": borda_scores, "approval": approval_scores,
                    "condorcet": condorcet_winner, "agreement": all_agree,
                    "agreement_rate": round(agreements / sim, 3)
                }
            ))
        
        return SimulationResult(
            game_id="voting_game", config=config, rounds=rd,
            equilibria=[Equilibrium(
                name="System Comparison", strategies=cand_names,
                description=f"Systems agreed {agreements}/{sims} times ({100*agreements/sims:.1f}%). Condorcet winner existed in {100*condorcet_exists_count/sims:.1f}% of elections."
            )],
            summary={
                "plurality_distribution": {c: round(v/sims, 3) for c, v in plurality_wins.items()},
                "borda_distribution": {c: round(v/sims, 3) for c, v in borda_wins.items()},
                "approval_distribution": {c: round(v/sims, 3) for c, v in approval_wins.items()},
                "system_agreement_rate": round(agreements / sims, 3),
                "condorcet_existence_rate": round(condorcet_exists_count / sims, 3),
            },
            metadata={"compute_time_ms": round((time.time() - t0) * 1000, 2), "engine": "server"})
