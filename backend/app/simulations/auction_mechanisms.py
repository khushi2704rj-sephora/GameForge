"""Auction Mechanisms — Vickrey (2nd-price), English (ascending), Dutch (descending)."""
from __future__ import annotations
import random
import time
from app.models.schemas import (
    GameInfo, ParameterSpec, SimulationResult, RoundData, Equilibrium,
)
from app.simulations.base import BaseGame


class AuctionMechanisms(BaseGame):
    def info(self) -> GameInfo:
        return GameInfo(
            id="auction_mechanisms",
            name="Auction Mechanisms",
            category="underrated",
            tier=2,
            short_description="Compare Vickrey, English, and Dutch auction formats.",
            long_description=(
                "Simulate auctions with N bidders who have independent private values drawn "
                "from a configurable distribution. Compare the Revenue Equivalence Theorem "
                "across three major auction formats: second-price sealed-bid (Vickrey), "
                "ascending open-cry (English), and descending clock (Dutch). Each mechanism "
                "induces different strategic behavior despite theoretical revenue equivalence."
            ),
            parameters=[
                ParameterSpec(name="auction_type", type="select", default="vickrey",
                              options=["vickrey", "english", "dutch"],
                              description="Auction format"),
                ParameterSpec(name="n_bidders", type="int", default=5, min=2, max=50,
                              description="Number of bidders"),
                ParameterSpec(name="value_mean", type="float", default=100.0, min=10, max=1000,
                              description="Mean of private values distribution"),
                ParameterSpec(name="value_std", type="float", default=20.0, min=1, max=200,
                              description="Std deviation of private values"),
                ParameterSpec(name="n_auctions", type="int", default=500, min=50, max=5000,
                              description="Number of auctions to simulate"),
            ],
            available=True,
            engine="server",
            tags=["auction", "mechanism-design", "revenue-equivalence"],
            theory_card=(
                "## Vickrey Auction (1961)\n"
                "In a second-price sealed-bid auction, the dominant strategy is to bid "
                "your true value. The winner pays the second-highest bid.\n\n"
                "## Revenue Equivalence Theorem\n"
                "Under risk-neutral bidders with IPV (independent private values), all "
                "standard auction formats yield the same expected revenue.\n\n"
                "## Strategic Differences\n"
                "- **Vickrey**: truthful bidding is dominant\n"
                "- **English**: strategically equivalent to Vickrey\n"
                "- **Dutch**: strategically equivalent to first-price sealed-bid (shade bids)"
            ),
        )

    def compute(self, config: dict) -> SimulationResult:
        t0 = time.time()
        atype = config.get("auction_type", "vickrey")
        n_bidders = config.get("n_bidders", 5)
        v_mean = config.get("value_mean", 100.0)
        v_std = config.get("value_std", 20.0)
        n_auctions = config.get("n_auctions", 500)

        round_data: list[RoundData] = []
        revenues: list[float] = []
        winner_surpluses: list[float] = []

        sample_indices = set(sorted(random.sample(range(n_auctions), min(200, n_auctions))))

        for a in range(n_auctions):
            values = [max(0, random.gauss(v_mean, v_std)) for _ in range(n_bidders)]

            if atype == "vickrey":
                bids = list(values)  # truthful bidding is dominant
                winner_idx = max(range(n_bidders), key=lambda i: bids[i])
                sorted_bids = sorted(bids, reverse=True)
                price = sorted_bids[1]  # second-highest bid
            elif atype == "english":
                # Simulate ascending: drops out just below value, winner pays 2nd-highest value
                bids = list(values)
                winner_idx = max(range(n_bidders), key=lambda i: values[i])
                price = sorted(values, reverse=True)[1]  # 2nd highest value
            else:  # dutch
                # First-price: bid-shading equilibrium b(v) = v * (n-1)/n
                bids = [v * (n_bidders - 1) / n_bidders for v in values]
                winner_idx = max(range(n_bidders), key=lambda i: bids[i])
                price = bids[winner_idx]  # winner pays their own bid

            revenue = price
            surplus = values[winner_idx] - price
            revenues.append(revenue)
            winner_surpluses.append(surplus)

            if a in sample_indices:
                round_data.append(RoundData(
                    round_num=a + 1,
                    actions=[round(b, 2) for b in bids],
                    payoffs=[round(values[i] - price, 2) if i == winner_idx else 0.0
                             for i in range(n_bidders)],
                    state={
                        "values": [round(v, 2) for v in values],
                        "winner": winner_idx,
                        "price": round(price, 2),
                        "revenue": round(revenue, 2),
                    },
                ))

        avg_rev = sum(revenues) / len(revenues)
        avg_surplus = sum(winner_surpluses) / len(winner_surpluses)

        return SimulationResult(
            game_id="auction_mechanisms",
            config=config,
            rounds=round_data,
            equilibria=[
                Equilibrium(
                    name="Dominant Strategy (Vickrey)",
                    strategies=["bid = true value"],
                    description="In Vickrey auctions, truthful bidding is weakly dominant.",
                ),
                Equilibrium(
                    name="Bayesian NE (Dutch/First-price)",
                    strategies=[f"bid = value × {(n_bidders-1)/n_bidders:.2f}"],
                    description=f"Optimal bid-shading: b(v) = v × (n-1)/n = v × {(n_bidders-1)/n_bidders:.2f}",
                ),
            ],
            summary={
                "avg_revenue": round(avg_rev, 2),
                "avg_winner_surplus": round(avg_surplus, 2),
                "revenue_std": round((sum((r - avg_rev) ** 2 for r in revenues) / len(revenues)) ** 0.5, 2),
                "auction_type": atype,
                "efficiency": round(
                    sum(1 for rd in round_data if rd.state.get("winner") ==
                        max(range(n_bidders), key=lambda i: rd.state["values"][i]))
                    / len(round_data), 3
                ) if round_data else 1.0,
            },
            metadata={"compute_time_ms": round((time.time() - t0) * 1000, 2), "engine": "server"},
        )
