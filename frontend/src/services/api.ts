/* API client for communicating with the FastAPI backend */
import type { GameInfo, SimulationRequest, SimulationResult } from "../types";

const API_BASE = import.meta.env.DEV
    ? `http://${window.location.hostname}:8000/api`
    : "/api";

export async function fetchGames(): Promise<GameInfo[]> {
    const res = await fetch(`${API_BASE}/games`);
    if (!res.ok) throw new Error(`Failed to fetch games: ${res.statusText}`);
    return res.json();
}

export async function fetchGameDetail(gameId: string): Promise<GameInfo> {
    const res = await fetch(`${API_BASE}/games/${gameId}`);
    if (!res.ok) throw new Error(`Failed to fetch game: ${res.statusText}`);
    return res.json();
}

export async function runSimulation(req: SimulationRequest): Promise<SimulationResult> {
    const res = await fetch(`${API_BASE}/simulate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(req),
    });
    if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: res.statusText }));
        throw new Error(err.detail || "Simulation failed");
    }
    return res.json();
}
