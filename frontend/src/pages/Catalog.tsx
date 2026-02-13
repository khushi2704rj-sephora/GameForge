import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { fetchGames } from "../services/api";

interface GameInfo {
    id: string;
    name: string;
    category: string;
    tier: number;
    short_description: string;
    tags?: string[];
    available: boolean;
}

const TIER_META: Record<number, { label: string; cssClass: string; tierClass: string }> = {
    1: { label: "Classical", cssClass: "tier-classical", tierClass: "tier-1" },
    2: { label: "Underrated", cssClass: "tier-underrated", tierClass: "tier-2" },
    3: { label: "Innovation", cssClass: "tier-innovation", tierClass: "tier-3" },
};

const FILTERS = ["All", "Classical", "Underrated", "Innovation"];

export default function Catalog() {
    const [games, setGames] = useState<GameInfo[]>([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState("All");
    const navigate = useNavigate();

    useEffect(() => {
        fetchGames().then((g) => { setGames(g); setLoading(false); });
    }, []);

    // Scroll-reveal
    useEffect(() => {
        if (loading) return;
        const observer = new IntersectionObserver(
            (entries) => entries.forEach((e) => { if (e.isIntersecting) e.target.classList.add("visible"); }),
            { threshold: 0.05, rootMargin: "0px 0px -40px 0px" }
        );
        document.querySelectorAll(".reveal").forEach((el) => observer.observe(el));
        return () => observer.disconnect();
    }, [loading, filter]);

    const filtered = filter === "All"
        ? games
        : games.filter((g) => TIER_META[g.tier]?.label === filter);

    const grouped = [1, 2, 3].map((tier) => ({
        tier,
        games: filtered.filter((g) => g.tier === tier),
    })).filter((g) => g.games.length > 0);

    return (
        <div className="catalog-page container page-enter">
            <header className="catalog-header">
                <h1>Simulation Catalog</h1>
                <p>
                    {games.length} simulations spanning classical game theory, underrated gems, and cutting-edge innovations.
                </p>
            </header>

            {/* Filter bar */}
            <div className="filter-bar">
                {FILTERS.map((f) => (
                    <button key={f} className={`filter-btn ${filter === f ? "active" : ""}`} onClick={() => setFilter(f)}>
                        {f}
                        {f !== "All" && (
                            <span className="game-count">
                                {games.filter((g) => TIER_META[g.tier]?.label === f).length}
                            </span>
                        )}
                    </button>
                ))}
            </div>

            {/* Loading skeletons */}
            {loading && (
                <div className="sim-grid">
                    {Array.from({ length: 6 }).map((_, i) => (
                        <div key={i} className="glass-card skeleton skeleton-card" />
                    ))}
                </div>
            )}

            {/* Game groups */}
            {grouped.map(({ tier, games: tierGames }) => {
                const meta = TIER_META[tier];
                return (
                    <section key={tier} className={`tier-section ${meta.tierClass}`}>
                        <div className="tier-label">
                            <span className="tier-dot" />
                            {meta.label} — {tierGames.length} simulation{tierGames.length > 1 ? "s" : ""}
                        </div>
                        <div className="sim-grid stagger-children">
                            {tierGames.map((game) => (
                                <div
                                    key={game.id}
                                    className="glass-card sim-card reveal"
                                    onClick={() => game.available && navigate(`/simulate/${game.id}`)}
                                    style={{ cursor: game.available ? "pointer" : "default", opacity: game.available ? 1 : 0.5 }}
                                >
                                    <span className={`sim-card-tier ${meta.cssClass}`}>{meta.label}</span>
                                    <h3>{game.name}</h3>
                                    <p>{game.short_description}</p>
                                    {game.tags && (
                                        <div className="tags">
                                            {game.tags.map((t) => <span key={t} className="tag">{t}</span>)}
                                        </div>
                                    )}
                                    {!game.available && <span className="unavailable-badge">Coming Soon</span>}
                                </div>
                            ))}
                        </div>
                    </section>
                );
            })}
        </div>
    );
}
