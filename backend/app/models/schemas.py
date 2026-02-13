"""Pydantic models for simulation requests, results, and game catalog."""
from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Any


class SimulationRequest(BaseModel):
    game_id: str = Field(..., description="Identifier for the game module")
    config: dict[str, Any] = Field(default_factory=dict, description="Game-specific parameters")


class RoundData(BaseModel):
    round_num: int
    actions: list[Any]
    payoffs: list[float]
    state: dict[str, Any] = Field(default_factory=dict)


class Equilibrium(BaseModel):
    name: str
    strategies: list[Any]
    payoffs: list[float] | None = None
    description: str = ""


class SimulationResult(BaseModel):
    game_id: str
    config: dict[str, Any]
    rounds: list[RoundData]
    equilibria: list[Equilibrium]
    summary: dict[str, Any]
    metadata: dict[str, Any] = Field(default_factory=dict)


class ParameterSpec(BaseModel):
    name: str
    type: str  # "int" | "float" | "select" | "strategy_pair"
    default: Any
    min: float | None = None
    max: float | None = None
    options: list[str] | None = None
    description: str = ""


class GameInfo(BaseModel):
    id: str
    name: str
    category: str  # "classical" | "underrated" | "innovation"
    tier: int  # 1, 2, or 3
    short_description: str
    long_description: str
    parameters: list[ParameterSpec]
    available: bool = True
    engine: str = "server"  # "browser" | "server"
    tags: list[str] = Field(default_factory=list)
    theory_card: str = ""  # Markdown educational content
