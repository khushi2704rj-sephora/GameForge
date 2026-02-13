/* TypeScript interfaces matching the backend Pydantic models */

export interface ParameterSpec {
    name: string;
    type: "int" | "float" | "select" | "strategy_pair";
    default: any;
    min?: number;
    max?: number;
    options?: string[];
    description: string;
}

export interface GameInfo {
    id: string;
    name: string;
    category: "classical" | "underrated" | "innovation";
    tier: 1 | 2 | 3;
    short_description: string;
    long_description: string;
    parameters: ParameterSpec[];
    available: boolean;
    engine: "browser" | "server";
    tags: string[];
    theory_card: string;
}

export interface RoundData {
    round_num: number;
    actions: any[];
    payoffs: number[];
    state: Record<string, any>;
}

export interface Equilibrium {
    name: string;
    strategies: any[];
    payoffs?: number[];
    description: string;
}

export interface SimulationResult {
    game_id: string;
    config: Record<string, any>;
    rounds: RoundData[];
    equilibria: Equilibrium[];
    summary: Record<string, any>;
    metadata: Record<string, any>;
}

export interface SimulationRequest {
    game_id: string;
    config: Record<string, any>;
}
