import { useState, useEffect } from "react";
import { Link, useLocation } from "react-router-dom";

export default function Nav() {
    const location = useLocation();
    const [scrolled, setScrolled] = useState(false);

    useEffect(() => {
        const onScroll = () => setScrolled(window.scrollY > 20);
        window.addEventListener("scroll", onScroll, { passive: true });
        return () => window.removeEventListener("scroll", onScroll);
    }, []);

    return (
        <nav className={`nav ${scrolled ? "scrolled" : ""}`}>
            <div className="nav-inner">
                <Link to="/" className="nav-logo">
                    <svg viewBox="0 0 24 24" fill="none" stroke="url(#grad)" strokeWidth="2.5" strokeLinecap="round">
                        <defs>
                            <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
                                <stop offset="0%" stopColor="#d4a853" />
                                <stop offset="100%" stopColor="#c78f6d" />
                            </linearGradient>
                        </defs>
                        <polygon points="12,2 22,20 2,20" />
                        <line x1="12" y1="8" x2="12" y2="14" />
                        <circle cx="12" cy="17" r="1" fill="url(#grad)" />
                    </svg>
                    GameForge
                </Link>
                <ul className="nav-links">
                    <li><Link to="/" className={location.pathname === "/" ? "active" : ""}>Home</Link></li>
                    <li><Link to="/catalog" className={location.pathname === "/catalog" ? "active" : ""}>Simulations</Link></li>
                    <li><a href="https://github.com" target="_blank" rel="noopener">GitHub</a></li>
                </ul>
            </div>
        </nav>
    );
}
