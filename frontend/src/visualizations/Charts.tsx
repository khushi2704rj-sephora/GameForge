/* Visualization components for all 22 simulation types using Plotly */
import Plot from "react-plotly.js";
import type { SimulationResult } from "../types";

/* ── Shared Plotly Config ──────────────────────────────────────────────── */
const darkAxis: Partial<Plotly.LayoutAxis> = {
    color: "#94a3b8",
    gridcolor: "rgba(255,255,255,0.06)",
    zerolinecolor: "rgba(255,255,255,0.1)",
    tickfont: { family: "JetBrains Mono, monospace", size: 11, color: "#64748b" },
    titlefont: { family: "Inter, sans-serif", size: 12, color: "#94a3b8" },
};

const darkLayout: Partial<Plotly.Layout> = {
    paper_bgcolor: "transparent",
    plot_bgcolor: "transparent",
    font: { family: "Inter, sans-serif", color: "#94a3b8" },
    margin: { l: 50, r: 20, t: 10, b: 40 },
    legend: { font: { size: 11, color: "#94a3b8" }, bgcolor: "transparent" },
};

const plotConfig: Partial<Plotly.Config> = { displayModeBar: false, responsive: true };

/* ── Generic Time Series Chart — fallback for games without specific charts */
function GenericTimeChart({ result }: { result: SimulationResult }) {
    const rounds = result.rounds.map((r) => r.round_num);
    const stateKeys = result.rounds.length > 0
        ? Object.keys(result.rounds[0].state).filter((k) => typeof result.rounds[0].state[k] === "number")
        : [];
    const colors = ["#d4a853", "#c78f6d", "#e8c47a", "#8fbc8f", "#cd7f6e", "#b8a080", "#d4a853"];

    return (
        <Plot
            data={stateKeys.slice(0, 4).map((key, i) => ({
                x: rounds,
                y: result.rounds.map((r) => r.state[key]),
                type: "scatter" as const,
                mode: "lines" as const,
                name: key.replace(/_/g, " "),
                line: { color: colors[i % colors.length], width: 2 },
            }))}
            layout={{ ...darkLayout, xaxis: { ...darkAxis, title: "Round" }, yaxis: { ...darkAxis }, height: 350, showlegend: true }}
            config={plotConfig}
            style={{ width: "100%" }}
        />
    );
}

/* ── Prisoner's Dilemma ────────────────────────────────────────────────── */
function PDChart({ result }: { result: SimulationResult }) {
    const rounds = result.rounds.map((r) => r.round_num);
    return (
        <>
            <Plot
                data={[{
                    x: rounds, y: result.rounds.map((r) => r.state.coop_rate),
                    type: "scatter", mode: "lines", name: "Cooperation Rate",
                    line: { color: "#06b6d4", width: 2 }, fill: "tozeroy", fillcolor: "rgba(6,182,212,0.1)",
                }]}
                layout={{ ...darkLayout, xaxis: { ...darkAxis, title: "Round" }, yaxis: { ...darkAxis, title: "Rate", range: [0, 1] }, height: 300 }}
                config={plotConfig} style={{ width: "100%" }}
            />
            <div style={{ marginTop: 16 }}>
                <Plot
                    data={[
                        { x: rounds, y: result.rounds.map((r) => r.state.cumulative[0]), type: "scatter", mode: "lines", name: "P1", line: { color: "#06b6d4", width: 2 } },
                        { x: rounds, y: result.rounds.map((r) => r.state.cumulative[1]), type: "scatter", mode: "lines", name: "P2", line: { color: "#d946ef", width: 2 } },
                    ]}
                    layout={{ ...darkLayout, xaxis: { ...darkAxis, title: "Round" }, yaxis: { ...darkAxis, title: "Cumulative Payoff" }, height: 300 }}
                    config={plotConfig} style={{ width: "100%" }}
                />
            </div>
        </>
    );
}

/* ── Public Goods ──────────────────────────────────────────────────────── */
function PublicGoodsChart({ result }: { result: SimulationResult }) {
    const rounds = result.rounds.map((r) => r.round_num);
    return (
        <>
            <Plot
                data={[{
                    x: rounds, y: result.rounds.map((r) => r.state.avg_contribution),
                    type: "scatter", mode: "lines", name: "Avg Contribution",
                    line: { color: "#10b981", width: 2 }, fill: "tozeroy", fillcolor: "rgba(16,185,129,0.1)",
                }]}
                layout={{ ...darkLayout, xaxis: { ...darkAxis, title: "Round" }, yaxis: { ...darkAxis, title: "Contribution" }, height: 300 }}
                config={plotConfig} style={{ width: "100%" }}
            />
            <div style={{ marginTop: 16 }}>
                <Plot
                    data={[{
                        x: rounds, y: result.rounds.map((r) => r.state.free_rider_ratio),
                        type: "scatter", mode: "lines", name: "Free-Rider Ratio",
                        line: { color: "#ef4444", width: 2 }, fill: "tozeroy", fillcolor: "rgba(239,68,68,0.1)",
                    }]}
                    layout={{ ...darkLayout, xaxis: { ...darkAxis, title: "Round" }, yaxis: { ...darkAxis, title: "Ratio", range: [0, 1] }, height: 300 }}
                    config={plotConfig} style={{ width: "100%" }}
                />
            </div>
        </>
    );
}

/* ── Tragedy of the Commons ─────────────────────────────────────────────── */
function TragedyChart({ result }: { result: SimulationResult }) {
    const rounds = result.rounds.map((r) => r.round_num);
    return (
        <>
            <Plot
                data={[
                    { x: rounds, y: result.rounds.map((r) => r.state.pool), type: "scatter", mode: "lines", name: "Resource Pool", line: { color: "#8fbc8f", width: 2.5 }, fill: "tozeroy", fillcolor: "rgba(143,188,143,0.1)" },
                    { x: rounds, y: result.rounds.map((r) => r.state.total_harvest), type: "scatter", mode: "lines", name: "Total Harvest", line: { color: "#d4a853", width: 2 } },
                ]}
                layout={{ ...darkLayout, xaxis: { ...darkAxis, title: "Round" }, yaxis: { ...darkAxis, title: "Value" }, height: 300 }}
                config={plotConfig} style={{ width: "100%" }}
            />
        </>
    );
}

/* ── Auction ───────────────────────────────────────────────────────────── */
function AuctionChart({ result }: { result: SimulationResult }) {
    const rounds = result.rounds.map((r) => r.round_num);
    return (
        <Plot
            data={[
                { x: rounds, y: result.rounds.map((r) => r.state.revenue), type: "scatter", mode: "lines", name: "Revenue", line: { color: "#d4a853", width: 2 } },
                { x: rounds, y: result.rounds.map((r) => r.state.winner_surplus), type: "scatter", mode: "lines", name: "Winner Surplus", line: { color: "#8fbc8f", width: 2 } },
            ]}
            layout={{ ...darkLayout, xaxis: { ...darkAxis, title: "Round" }, yaxis: { ...darkAxis, title: "Value" }, height: 300 }}
            config={plotConfig} style={{ width: "100%" }}
        />
    );
}

/* ── Stag Hunt ─────────────────────────────────────────────────────────── */
function StagHuntChart({ result }: { result: SimulationResult }) {
    const rounds = result.rounds.map((r) => r.round_num);
    return (
        <Plot
            data={[
                { x: rounds, y: result.rounds.map((r) => r.state.stag_rate), type: "scatter", mode: "lines", name: "Stag Rate", line: { color: "#06b6d4", width: 2 }, fill: "tozeroy", fillcolor: "rgba(6,182,212,0.1)" },
            ]}
            layout={{ ...darkLayout, xaxis: { ...darkAxis, title: "Round" }, yaxis: { ...darkAxis, title: "Stag Hunting Rate", range: [0, 1] }, height: 300 }}
            config={plotConfig} style={{ width: "100%" }}
        />
    );
}

/* ── Battle of Sexes ───────────────────────────────────────────────────── */
function BOSChart({ result }: { result: SimulationResult }) {
    const rounds = result.rounds.map((r) => r.round_num);
    return (
        <Plot
            data={[
                { x: rounds, y: result.rounds.map((r) => r.state.coordination_rate), type: "scatter", mode: "lines", name: "Coordination Rate", line: { color: "#d946ef", width: 2 }, fill: "tozeroy", fillcolor: "rgba(217,70,239,0.1)" },
            ]}
            layout={{ ...darkLayout, xaxis: { ...darkAxis, title: "Round" }, yaxis: { ...darkAxis, title: "Coordination Rate", range: [0, 1] }, height: 300 }}
            config={plotConfig} style={{ width: "100%" }}
        />
    );
}

/* ── Matching Pennies ──────────────────────────────────────────────────── */
function MatchingPenniesChart({ result }: { result: SimulationResult }) {
    const rounds = result.rounds.map((r) => r.round_num);
    return (
        <Plot
            data={[
                { x: rounds, y: result.rounds.map((r) => r.state.p1_heads_rate), type: "scatter", mode: "lines", name: "P1 Heads Rate", line: { color: "#06b6d4", width: 2 } },
                { x: rounds, y: result.rounds.map((r) => r.state.p1_win_rate), type: "scatter", mode: "lines", name: "P1 Win Rate", line: { color: "#f59e0b", width: 2, dash: "dot" } },
            ]}
            layout={{ ...darkLayout, xaxis: { ...darkAxis, title: "Round" }, yaxis: { ...darkAxis, title: "Rate", range: [0, 1] }, height: 300 }}
            config={plotConfig} style={{ width: "100%" }}
        />
    );
}

/* ── Rock-Paper-Scissors ───────────────────────────────────────────────── */
function RPSChart({ result }: { result: SimulationResult }) {
    const rounds = result.rounds.map((r) => r.round_num);
    return (
        <Plot
            data={[
                { x: rounds, y: result.rounds.map((r) => r.state.p1_win_rate), type: "scatter", mode: "lines", name: "P1 Win Rate", line: { color: "#06b6d4", width: 2 } },
                { x: rounds, y: result.rounds.map((r) => r.state.draw_rate), type: "scatter", mode: "lines", name: "Draw Rate", line: { color: "#f59e0b", width: 2 } },
            ]}
            layout={{ ...darkLayout, xaxis: { ...darkAxis, title: "Round" }, yaxis: { ...darkAxis, title: "Rate", range: [0, 1] }, height: 300 }}
            config={plotConfig} style={{ width: "100%" }}
        />
    );
}

/* ── Ultimatum ─────────────────────────────────────────────────────────── */
function UltimatumChart({ result }: { result: SimulationResult }) {
    const offers = result.rounds.map((r) => r.state.offer);
    return (
        <Plot
            data={[{
                x: offers, type: "histogram", marker: { color: "rgba(6,182,212,0.6)" },
                nbinsx: 20, name: "Offer Distribution",
            }]}
            layout={{ ...darkLayout, xaxis: { ...darkAxis, title: "Offer Amount" }, yaxis: { ...darkAxis, title: "Frequency" }, height: 300, showlegend: false, bargap: 0.05 }}
            config={plotConfig} style={{ width: "100%" }}
        />
    );
}

/* ── Centipede ─────────────────────────────────────────────────────────── */
function CentipedeChart({ result }: { result: SimulationResult }) {
    const rounds = result.rounds.map((r) => r.round_num);
    return (
        <Plot
            data={[{
                x: rounds, y: result.rounds.map((r) => r.state.avg_stop_round),
                type: "scatter", mode: "lines", name: "Avg Stop Round",
                line: { color: "#8b5cf6", width: 2 }, fill: "tozeroy", fillcolor: "rgba(139,92,246,0.1)",
            }]}
            layout={{ ...darkLayout, xaxis: { ...darkAxis, title: "Game" }, yaxis: { ...darkAxis, title: "Avg Stop Round" }, height: 300 }}
            config={plotConfig} style={{ width: "100%" }}
        />
    );
}

/* ── ESS ───────────────────────────────────────────────────────────────── */
function ESSChart({ result }: { result: SimulationResult }) {
    const rounds = result.rounds.map((r) => r.round_num);
    const firstRound = result.rounds[0];
    if (!firstRound || !firstRound.state.frequencies) return <GenericTimeChart result={result} />;
    const numStrategies = firstRound.state.frequencies.length;
    const colors = ["#06b6d4", "#d946ef", "#f59e0b", "#10b981", "#ef4444"];
    return (
        <Plot
            data={Array.from({ length: numStrategies }, (_, i) => ({
                x: rounds,
                y: result.rounds.map((r) => r.state.frequencies[i]),
                type: "scatter" as const, mode: "lines" as const,
                name: `Strategy ${i + 1}`, line: { color: colors[i % colors.length], width: 2 },
                stackgroup: "one",
            }))}
            layout={{ ...darkLayout, xaxis: { ...darkAxis, title: "Generation" }, yaxis: { ...darkAxis, title: "Frequency", range: [0, 1] }, height: 350 }}
            config={plotConfig} style={{ width: "100%" }}
        />
    );
}

/* ── Voting Game ────────────────────────────────────────────────────────── */
function VotingChart({ result }: { result: SimulationResult }) {
    const rounds = result.rounds.map((r) => r.round_num);
    return (
        <Plot
            data={[
                { x: rounds, y: result.rounds.map((r) => r.state.agreement_rate), type: "scatter", mode: "lines", name: "System Agreement Rate", line: { color: "#d4a853", width: 2.5 }, fill: "tozeroy", fillcolor: "rgba(212,168,83,0.1)" },
            ]}
            layout={{ ...darkLayout, xaxis: { ...darkAxis, title: "Election" }, yaxis: { ...darkAxis, title: "Agreement Rate", range: [0, 1] }, height: 300 }}
            config={plotConfig} style={{ width: "100%" }}
        />
    );
}

/* ── Bayesian Signaling ────────────────────────────────────────────────── */
function BayesianChart({ result }: { result: SimulationResult }) {
    const rounds = result.rounds.map((r) => r.round_num);
    return (
        <Plot
            data={[
                { x: rounds, y: result.rounds.map((r) => r.state.accuracy), type: "scatter", mode: "lines", name: "Accuracy", line: { color: "#10b981", width: 2 } },
                { x: rounds, y: result.rounds.map((r) => r.state.separation_rate), type: "scatter", mode: "lines", name: "Separation Rate", line: { color: "#8b5cf6", width: 2 } },
            ]}
            layout={{ ...darkLayout, xaxis: { ...darkAxis, title: "Interaction" }, yaxis: { ...darkAxis, title: "Rate", range: [0, 1] }, height: 300 }}
            config={plotConfig} style={{ width: "100%" }}
        />
    );
}

/* ── Supply Chain ──────────────────────────────────────────────────────── */
function SupplyChainChart({ result }: { result: SimulationResult }) {
    const rounds = result.rounds.map((r) => r.round_num);
    return (
        <Plot
            data={[
                { x: rounds, y: result.rounds.map((r) => r.state.bullwhip_ratio), type: "scatter", mode: "lines", name: "Bullwhip Ratio", line: { color: "#ef4444", width: 2 } },
                { x: rounds, y: result.rounds.map((r) => r.state.demand), type: "scatter", mode: "lines", name: "Customer Demand", line: { color: "#06b6d4", width: 1, dash: "dot" } },
            ]}
            layout={{ ...darkLayout, xaxis: { ...darkAxis, title: "Period" }, yaxis: { ...darkAxis, title: "Value" }, height: 300 }}
            config={plotConfig} style={{ width: "100%" }}
        />
    );
}

/* ── Stackelberg ───────────────────────────────────────────────────────── */
function StackelbergChart({ result }: { result: SimulationResult }) {
    const rounds = result.rounds.map((r) => r.round_num);
    return (
        <Plot
            data={[
                { x: rounds, y: result.rounds.map((r) => r.payoffs[0]), type: "scatter", mode: "lines", name: "Leader Profit", line: { color: "#06b6d4", width: 2 } },
                { x: rounds, y: result.rounds.map((r) => r.payoffs[1]), type: "scatter", mode: "lines", name: "Follower Profit", line: { color: "#d946ef", width: 2 } },
                { x: rounds, y: result.rounds.map((r) => r.state.price), type: "scatter", mode: "lines", name: "Market Price", line: { color: "#f59e0b", width: 1, dash: "dot" } },
            ]}
            layout={{ ...darkLayout, xaxis: { ...darkAxis, title: "Period" }, yaxis: { ...darkAxis, title: "Value" }, height: 300 }}
            config={plotConfig} style={{ width: "100%" }}
        />
    );
}

/* ── Cournot vs Bertrand ───────────────────────────────────────────────── */
function CournotBertrandChart({ result }: { result: SimulationResult }) {
    const rounds = result.rounds.map((r) => r.round_num);
    return (
        <Plot
            data={[
                { x: rounds, y: result.rounds.map((r) => r.state.price), type: "scatter", mode: "lines", name: "Market Price", line: { color: "#f59e0b", width: 2 } },
                { x: rounds, y: result.rounds.map((r) => r.state.avg_firm_profit), type: "scatter", mode: "lines", name: "Avg Firm Profit", line: { color: "#06b6d4", width: 2 } },
            ]}
            layout={{ ...darkLayout, xaxis: { ...darkAxis, title: "Period" }, yaxis: { ...darkAxis, title: "Value" }, height: 300 }}
            config={plotConfig} style={{ width: "100%" }}
        />
    );
}

/* ── Reputation & Trust ────────────────────────────────────────────────── */
function ReputationChart({ result }: { result: SimulationResult }) {
    const rounds = result.rounds.map((r) => r.round_num);
    return (
        <Plot
            data={[
                { x: rounds, y: result.rounds.map((r) => r.state.reputation), type: "scatter", mode: "lines", name: "Reputation", line: { color: "#10b981", width: 2.5 }, fill: "tozeroy", fillcolor: "rgba(16,185,129,0.08)" },
                { x: rounds, y: result.rounds.map((r) => r.state.trust_rate), type: "scatter", mode: "lines", name: "Trust Rate", line: { color: "#06b6d4", width: 1.5, dash: "dot" } },
                { x: rounds, y: result.rounds.map((r) => r.state.betrayal_rate), type: "scatter", mode: "lines", name: "Betrayal Rate", line: { color: "#ef4444", width: 1.5, dash: "dot" } },
            ]}
            layout={{ ...darkLayout, xaxis: { ...darkAxis, title: "Round" }, yaxis: { ...darkAxis, title: "Rate", range: [0, 1] }, height: 300 }}
            config={plotConfig} style={{ width: "100%" }}
        />
    );
}

/* ── Trust Game ─────────────────────────────────────────────────────────── */
function TrustChart({ result }: { result: SimulationResult }) {
    const rounds = result.rounds.map((r) => r.round_num);
    return (
        <Plot
            data={[
                { x: rounds, y: result.rounds.map((r) => r.state.avg_trust), type: "scatter", mode: "lines", name: "Avg Trust", line: { color: "#d4a853", width: 2.5 }, fill: "tozeroy", fillcolor: "rgba(212,168,83,0.08)" },
                { x: rounds, y: result.rounds.map((r) => r.payoffs[0]), type: "scatter", mode: "lines", name: "Investor Payoff", line: { color: "#8fbc8f", width: 1.5, dash: "dot" } },
                { x: rounds, y: result.rounds.map((r) => r.payoffs[1]), type: "scatter", mode: "lines", name: "Trustee Payoff", line: { color: "#c78f6d", width: 1.5, dash: "dot" } },
            ]}
            layout={{ ...darkLayout, xaxis: { ...darkAxis, title: "Round" }, yaxis: { ...darkAxis, title: "Value" }, height: 300 }}
            config={plotConfig} style={{ width: "100%" }}
        />
    );
}

/* ── Generalized Coordination ──────────────────────────────────────────── */
function CoordinationChart({ result }: { result: SimulationResult }) {
    const rounds = result.rounds.map((r) => r.round_num);
    return (
        <Plot
            data={[
                { x: rounds, y: result.rounds.map((r) => r.state.coordination_rate), type: "scatter", mode: "lines", name: "Coordination Rate", line: { color: "#10b981", width: 2.5 }, fill: "tozeroy", fillcolor: "rgba(16,185,129,0.08)" },
                { x: rounds, y: result.rounds.map((r) => r.state.entropy), type: "scatter", mode: "lines", name: "Entropy", line: { color: "#f59e0b", width: 1.5, dash: "dot" } },
            ]}
            layout={{ ...darkLayout, xaxis: { ...darkAxis, title: "Round" }, yaxis: { ...darkAxis, title: "Value" }, height: 300 }}
            config={plotConfig} style={{ width: "100%" }}
        />
    );
}

/* ── Coalition Formation ───────────────────────────────────────────────── */
function CoalitionChart({ result }: { result: SimulationResult }) {
    const rounds = result.rounds.map((r) => r.round_num);
    return (
        <Plot
            data={[
                { x: rounds, y: result.rounds.map((r) => r.state.n_coalitions), type: "scatter", mode: "lines", name: "# Coalitions", line: { color: "#8b5cf6", width: 2 } },
                { x: rounds, y: result.rounds.map((r) => r.state.largest_coalition), type: "scatter", mode: "lines", name: "Largest Coalition", line: { color: "#06b6d4", width: 2 } },
                { x: rounds, y: result.rounds.map((r) => r.state.total_value), type: "scatter", mode: "lines", name: "Total Value", line: { color: "#10b981", width: 1.5, dash: "dot" }, yaxis: "y2" },
            ]}
            layout={{ ...darkLayout, xaxis: { ...darkAxis, title: "Round" }, yaxis: { ...darkAxis, title: "Count" }, yaxis2: { ...darkAxis, title: "Value", overlaying: "y", side: "right" }, height: 320 }}
            config={plotConfig} style={{ width: "100%" }}
        />
    );
}

/* ── Pirate Division ───────────────────────────────────────────────────── */
function PirateChart({ result }: { result: SimulationResult }) {
    const rounds = result.rounds.map((r) => r.round_num);
    return (
        <Plot
            data={[
                { x: rounds, y: result.rounds.map((r) => r.payoffs[0]), type: "scatter", mode: "lines", name: "Proposer Share", line: { color: "#d4a853", width: 2 } },
                { x: rounds, y: result.rounds.map((r) => r.state.acceptance_rate), type: "scatter", mode: "lines", name: "Acceptance Rate", line: { color: "#8fbc8f", width: 2 } },
            ]}
            layout={{ ...darkLayout, xaxis: { ...darkAxis, title: "Simulation" }, yaxis: { ...darkAxis, title: "Value" }, height: 300 }}
            config={plotConfig} style={{ width: "100%" }}
        />
    );
}

/* ── El Farol Bar ──────────────────────────────────────────────────────── */
function ElFarolChart({ result }: { result: SimulationResult }) {
    const rounds = result.rounds.map((r) => r.round_num);
    return (
        <Plot
            data={[
                { x: rounds, y: result.rounds.map((r) => r.state.attendance), type: "scatter", mode: "lines", name: "Attendance", line: { color: "#d4a853", width: 2 } },
                { x: rounds, y: result.rounds.map((r) => r.state.avg_attendance), type: "scatter", mode: "lines", name: "Avg Attendance", line: { color: "#c78f6d", width: 2, dash: "dot" } },
            ]}
            layout={{ ...darkLayout, xaxis: { ...darkAxis, title: "Week" }, yaxis: { ...darkAxis, title: "People" }, height: 300 }}
            config={plotConfig} style={{ width: "100%" }}
        />
    );
}

/* ══════════════════════════════════════════════════════════════════════════
   CHART_MAP — maps game_id → chart component
   ══════════════════════════════════════════════════════════════════════════ */
export const CHART_MAP: Record<string, React.ComponentType<{ result: SimulationResult }>> = {
    prisoners_dilemma: PDChart,
    public_goods: PublicGoodsChart,
    tragedy_of_commons: TragedyChart,
    auction_mechanisms: AuctionChart,
    trust_game: TrustChart,
    stag_hunt: StagHuntChart,
    battle_of_sexes: BOSChart,
    matching_pennies: MatchingPenniesChart,
    rock_paper_scissors: RPSChart,
    ultimatum: UltimatumChart,
    centipede: CentipedeChart,
    ess_module: ESSChart,
    voting_game: VotingChart,
    bayesian_signaling: BayesianChart,
    supply_chain: SupplyChainChart,
    stackelberg: StackelbergChart,
    cournot_bertrand: CournotBertrandChart,
    reputation_trust: ReputationChart,
    el_farol_bar: ElFarolChart,
    coordination_general: CoordinationChart,
    coalition_formation: CoalitionChart,
    pirate_division: PirateChart,
};
