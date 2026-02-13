"""API routes for simulation execution and game catalog."""
from __future__ import annotations
from fastapi import APIRouter, HTTPException
from app.models.schemas import SimulationRequest, SimulationResult, GameInfo
from app.simulations.registry import get_game, get_all_game_info, get_game_info

router = APIRouter(prefix="/api")


@router.get("/games", response_model=list[GameInfo])
def list_games():
    """Return the full catalog of available and coming-soon games."""
    return get_all_game_info()


@router.get("/games/{game_id}", response_model=GameInfo)
def game_detail(game_id: str):
    """Return metadata for a specific game."""
    info = get_game_info(game_id)
    if info is None:
        raise HTTPException(status_code=404, detail=f"Game '{game_id}' not found.")
    return info


@router.post("/simulate", response_model=SimulationResult)
def run_simulation(req: SimulationRequest):
    """Execute a simulation and return the results."""
    game = get_game(req.game_id)
    if game is None:
        info = get_game_info(req.game_id)
        if info and not info.available:
            raise HTTPException(status_code=501, detail=f"Game '{req.game_id}' is coming soon.")
        raise HTTPException(status_code=404, detail=f"Game '{req.game_id}' not found.")
    try:
        result = game.compute(req.config)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Simulation error: {str(e)}")
    return result
