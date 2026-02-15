import { useEffect, useRef, useCallback } from "react";
import { Link } from "react-router-dom";

/* ── Animated Counter Hook ────────────────────────────────────────────── */
function useCounter(end: number, duration = 2000) {
    const ref = useRef<HTMLSpanElement>(null);
    const hasAnimated = useRef(false);

    const animate = useCallback(() => {
        if (!ref.current || hasAnimated.current) return;
        hasAnimated.current = true;
        const start = 0;
        const startTime = performance.now();
        const step = (now: number) => {
            const progress = Math.min((now - startTime) / duration, 1);
            const eased = 1 - Math.pow(1 - progress, 4); // ease-out quartic
            const current = Math.round(start + (end - start) * eased);
            if (ref.current) ref.current.textContent = current.toLocaleString();
            if (progress < 1) requestAnimationFrame(step);
        };
        requestAnimationFrame(step);
    }, [end, duration]);

    return { ref, animate };
}

/* ── Scroll Reveal Hook ───────────────────────────────────────────────── */
function useScrollReveal() {
    useEffect(() => {
        const observer = new IntersectionObserver(
            (entries) => {
                entries.forEach((e) => { if (e.isIntersecting) e.target.classList.add("visible"); });
            },
            { threshold: 0.1, rootMargin: "0px 0px -60px 0px" }
        );
        document.querySelectorAll(".reveal").forEach((el) => observer.observe(el));
        return () => observer.disconnect();
    }, []);
}

export default function Landing() {
    useScrollReveal();

    const counter22 = useCounter(22);
    const counter100k = useCounter(100000);
    const counterRealtime = useCounter(50);
    const counterTheory = useCounter(12);

    // Trigger counters on scroll
    useEffect(() => {
        const observer = new IntersectionObserver(
            (entries) => {
                entries.forEach((e) => {
                    if (e.isIntersecting) {
                        counter22.animate();
                        counter100k.animate();
                        counterRealtime.animate();
                        counterTheory.animate();
                    }
                });
            },
            { threshold: 0.3 }
        );
        const el = document.querySelector(".stats-row");
        if (el) observer.observe(el);
        return () => observer.disconnect();
    }, []);

    return (
        <div className="page-enter">
            {/* Hero */}
            <section className="hero container">
                <div className="hero-bg-grid" />
                <div className="hero-particles">
                    {Array.from({ length: 8 }).map((_, i) => (
                        <div key={i} className="particle" />
                    ))}
                </div>

                <div className="hero-badge">
                    <span className="dot" />
                    22 strategic simulations ready to explore
                </div>

                <h1>
                    <span className="line">Master the art of</span>
                    <span className="line"><span className="gradient-text">strategic thinking</span></span>
                </h1>

                <p className="hero-subtitle">
                    Forge your understanding of game theory through interactive simulations.
                    From classic dilemmas to evolutionary dynamics — analyze equilibria,
                    craft strategies, and uncover hidden patterns.
                </p>

                <div className="hero-actions">
                    <Link to="/catalog" className="btn btn-primary">
                        Enter the Forge →
                    </Link>
                    <a href="#how-it-works" className="btn btn-secondary">
                        How It Works
                    </a>
                </div>
            </section>

            {/* Stats */}
            <section className="stats-row">
                <div className="stat-item reveal">
                    <div className="stat-number"><span ref={counter22.ref}>0</span>+</div>
                    <div className="stat-desc">Game Simulations</div>
                </div>
                <div className="stat-item reveal">
                    <div className="stat-number"><span ref={counter100k.ref}>0</span>+</div>
                    <div className="stat-desc">Rounds per second</div>
                </div>
                <div className="stat-item reveal">
                    <div className="stat-number"><span ref={counterRealtime.ref}>0</span>ms</div>
                    <div className="stat-desc">Avg. compute time</div>
                </div>
                <div className="stat-item reveal">
                    <div className="stat-number"><span ref={counterTheory.ref}>0</span></div>
                    <div className="stat-desc">Theory Cards</div>
                </div>
            </section>

            {/* How It Works */}
            <section id="how-it-works" className="how-it-works container">
                <h2 className="reveal">How It Works</h2>
                <div className="steps-timeline stagger-children">
                    <div className="step-card reveal">
                        <div className="step-number">1</div>
                        <h3>Select a Strategy</h3>
                        <p>Browse 22 simulations spanning classical dilemmas, economic models, and evolutionary dynamics.</p>
                    </div>
                    <div className="step-card reveal">
                        <div className="step-number">2</div>
                        <h3>Configure & Forge</h3>
                        <p>Fine-tune parameters like strategies, rounds, and payoffs. Execute and watch results materialize instantly.</p>
                    </div>
                    <div className="step-card reveal">
                        <div className="step-number">3</div>
                        <h3>Decode the Outcome</h3>
                        <p>Interactive charts and theory cards reveal Nash Equilibria, dominant strategies, and emergent patterns.</p>
                    </div>
                </div>
            </section>

            {/* Features */}
            <section className="container">
                <div className="feature-grid stagger-children">
                    <div className="feature-card reveal">
                        <div className="feature-icon">🔥</div>
                        <h3>High-Performance Engine</h3>
                        <p>Server-side Python engine forges thousands of rounds instantly. From 2×2 matrices to complex multi-agent negotiations.</p>
                    </div>
                    <div className="feature-card reveal">
                        <div className="feature-icon">📊</div>
                        <h3>Rich Visualizations</h3>
                        <p>Plotly-powered charts with real-time data. Cooperation rates, payoff landscapes, strategy evolution — all elegantly rendered.</p>
                    </div>
                    <div className="feature-card reveal">
                        <div className="feature-icon">🧠</div>
                        <h3>Built-in Theory Cards</h3>
                        <p>Each simulation includes Nash Equilibria, key theorems, and strategic insights. Learn game theory through hands-on experimentation.</p>
                    </div>
                </div>
            </section>

            {/* Team */}
            <section className="container team-section reveal">
                <h2>Created By</h2>
                <div className="team-grid">
                    <div className="team-member">Darshan Mehta</div>
                    <div className="team-member">Pranav M Nair</div>
                </div>
            </section>

            {/* Footer */}
            <footer className="container">
                <p>Forged with ⚛️ React + 🐍 FastAPI &nbsp;|&nbsp; <a href="https://github.com">Source Code</a></p>
            </footer>
        </div>
    );
}
