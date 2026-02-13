import { useEffect, useState, useMemo } from "react";
import { useParams, Link } from "react-router-dom";
import { fetchGames, runSimulation } from "../services/api";
import { CHART_MAP } from "../visualizations/Charts";

/* ── Types ────────────────────────────────────────────────────────────────── */
interface ParamSpec {
    name: string;
    type: string;
    default: number | string;
    min?: number;
    max?: number;
    options?: string[];
    description: string;
}

interface GameInfo {
    id: string;
    name: string;
    short_description: string;
    long_description: string;
    parameters: ParamSpec[];
    theory_card?: string;
    tags?: string[];
    category?: string;
    tier?: number;
}

interface RoundData {
    round_num: number;
    actions: any[];
    payoffs: number[];
    state: Record<string, any>;
}

interface Equilibrium {
    name: string;
    strategies: string[];
    payoffs?: number[];
    description?: string;
}

interface SimulationResult {
    game_id: string;
    config: Record<string, any>;
    rounds: RoundData[];
    equilibria: Equilibrium[];
    summary: Record<string, any>;
    metadata: Record<string, any>;
}

/* ── Markdown-lite Parser ─────────────────────────────────────────────────── */
function renderTheoryMarkdown(text: string): string {
    return text
        .replace(/## (.+)/g, '<h2>$1</h2>')
        .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
        .replace(/- (.+)/g, '<li>$1</li>')
        .replace(/\n/g, '<br/>');
}

/* ── Stat Formatter ───────────────────────────────────────────────────────── */
function formatStatValue(key: string, value: any): string {
    if (typeof value === "boolean") return value ? "Yes" : "No";
    if (typeof value === "string") return value;
    if (typeof value === "number") {
        if (key.includes("rate") || key.includes("ratio") || key.includes("efficiency")) {
            return (value * 100).toFixed(1) + "%";
        }
        if (Number.isInteger(value)) return value.toLocaleString();
        return value.toFixed(2);
    }
    return String(value);
}

function prettyKey(key: string): string {
    return key
        .replace(/_/g, " ")
        .replace(/\b\w/g, (c) => c.toUpperCase());
}

/* ── Component ────────────────────────────────────────────────────────────── */
export default function Simulator() {
    const { gameId } = useParams<{ gameId: string }>();
    const [game, setGame] = useState<GameInfo | null>(null);
    const [params, setParams] = useState<Record<string, any>>({});
    const [result, setResult] = useState<SimulationResult | null>(null);
    const [running, setRunning] = useState(false);
    const [error, setError] = useState<string | null>(null);

    // Load game info
    useEffect(() => {
        fetchGames().then((games) => {
            const g = games.find((x: any) => x.id === gameId);
            if (g) {
                setGame(g);
                const defaults: Record<string, any> = {};
                g.parameters.forEach((p: ParamSpec) => { defaults[p.name] = p.default; });
                setParams(defaults);
            }
        });
    }, [gameId]);

    const handleRun = async () => {
        if (!gameId) return;
        setRunning(true);
        setError(null);
        try {
            const res = await runSimulation({ game_id: gameId, config: params });
            setResult(res);
        } catch (e: any) {
            setError(e.message || "Simulation failed");
        } finally {
            setRunning(false);
        }
    };

    const ChartComponent = useMemo(() => gameId ? CHART_MAP[gameId] : null, [gameId]);

    if (!game) {
        return (
            <div className="simulator-page container page-enter">
                <div className="loading-dots">
                    <span /><span /><span /><span />
                </div>
            </div>
        );
    }

    return (
        <div className="simulator-page container page-enter">
            <Link to="/catalog" className="back-link">← Back to Catalog</Link>

            <div className="simulator-layout">
                {/* Config Panel */}
                <div className="config-panel glass-card">
                    <h2>{game.name}</h2>
                    <p className="game-desc">{game.long_description}</p>

                    {game.parameters.map((param) => (
                        <div key={param.name} className="param-group">
                            <label>{prettyKey(param.name)}</label>
                            {param.type === "select" && param.options ? (
                                <select
                                    value={params[param.name] ?? param.default}
                                    onChange={(e) => setParams((p) => ({ ...p, [param.name]: e.target.value }))}
                                >
                                    {param.options.map((opt) => (
                                        <option key={opt} value={opt}>{opt.replace(/_/g, " ")}</option>
                                    ))}
                                </select>
                            ) : param.type === "int" || param.type === "float" ? (
                                <div className="param-range">
                                    <input
                                        type="range"
                                        min={param.min}
                                        max={param.max}
                                        step={param.type === "float" ? 0.01 : 1}
                                        value={params[param.name] ?? param.default}
                                        onChange={(e) => setParams((p) => ({
                                            ...p,
                                            [param.name]: param.type === "int" ? parseInt(e.target.value) : parseFloat(e.target.value),
                                        }))}
                                    />
                                    <span className="param-value">{params[param.name] ?? param.default}</span>
                                </div>
                            ) : (
                                <input
                                    type="text"
                                    value={params[param.name] ?? ""}
                                    onChange={(e) => setParams((p) => ({ ...p, [param.name]: e.target.value }))}
                                />
                            )}
                            <small style={{ color: "var(--text-muted)", fontSize: "0.72rem", marginTop: 2, display: "block" }}>
                                {param.description}
                            </small>
                        </div>
                    ))}

                    <button className="btn btn-run" onClick={handleRun} disabled={running}>
                        {running ? (
                            <><span className="spinner" style={{ display: "inline-block" }} /> Running...</>
                        ) : (
                            "▶ Run Simulation"
                        )}
                    </button>

                    {/* Theory Card */}
                    {game.theory_card && (
                        <div className="theory-card">
                            <h3>📖 Theory Card</h3>
                            <div className="theory-content" dangerouslySetInnerHTML={{ __html: renderTheoryMarkdown(game.theory_card) }} />
                        </div>
                    )}
                </div>

                {/* Results Panel */}
                <div className="results-panel">
                    {error && (
                        <div className="glass-card" style={{ borderColor: "var(--accent-red)", marginBottom: "var(--space-lg)" }}>
                            <p style={{ color: "var(--accent-red)" }}>⚠ {error}</p>
                        </div>
                    )}

                    {!result && !running && (
                        <div className="results-empty glass-card">
                            <div className="empty-icon">🔬</div>
                            <h3>Configure & Run</h3>
                            <p>Set your parameters and hit Run to see simulation results.</p>
                        </div>
                    )}

                    {running && !result && (
                        <div className="glass-card" style={{ textAlign: "center", padding: "var(--space-3xl)" }}>
                            <div className="loading-dots">
                                <span /><span /><span /><span />
                            </div>
                            <p style={{ color: "var(--text-secondary)", marginTop: "var(--space-md)" }}>Computing simulation...</p>
                        </div>
                    )}

                    {result && (
                        <div className="results-enter">
                            {/* Summary Stats */}
                            <div className="results-summary">
                                {Object.entries(result.summary)
                                    .filter(([, v]) => typeof v !== "object")
                                    .map(([key, value]) => (
                                        <div key={key} className="stat-card">
                                            <div className="stat-value">{formatStatValue(key, value)}</div>
                                            <div className="stat-label">{prettyKey(key)}</div>
                                        </div>
                                    ))}
                            </div>

                            {/* Chart */}
                            {ChartComponent && (
                                <div className="chart-container">
                                    <h3>Visualization</h3>
                                    <ChartComponent result={result} />
                                </div>
                            )}

                            {/* Equilibria */}
                            {result.equilibria.length > 0 && (
                                <div className="glass-card equilibria-card" style={{ marginBottom: "var(--space-lg)" }}>
                                    <h3 style={{ fontFamily: "var(--font-display)", marginBottom: "var(--space-md)" }}>⚖️ Equilibria</h3>
                                    {result.equilibria.map((eq, i) => (
                                        <div key={i} style={{ marginBottom: "var(--space-md)", paddingBottom: "var(--space-md)", borderBottom: i < result.equilibria.length - 1 ? "1px solid var(--border-glass)" : "none" }}>
                                            <div style={{ fontWeight: 600, color: "var(--accent-amber)", marginBottom: 4 }}>{eq.name}</div>
                                            {eq.strategies.length > 0 && (
                                                <div style={{ fontSize: "0.82rem", color: "var(--text-secondary)", fontFamily: "var(--font-mono)" }}>
                                                    Strategies: {eq.strategies.join(", ")}
                                                </div>
                                            )}
                                            {eq.description && (
                                                <div style={{ fontSize: "0.82rem", color: "var(--text-muted)", marginTop: 4 }}>{eq.description}</div>
                                            )}
                                        </div>
                                    ))}
                                </div>
                            )}

                            {/* Metadata */}
                            <div style={{ textAlign: "right", fontSize: "0.72rem", color: "var(--text-muted)" }}>
                                Computed in {result.metadata.compute_time_ms}ms · {result.rounds.length} rounds · Engine: {result.metadata.engine}
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
