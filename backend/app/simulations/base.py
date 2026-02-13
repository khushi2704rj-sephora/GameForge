"""Base class for all game simulation modules."""
from __future__ import annotations
from abc import ABC, abstractmethod
from app.models.schemas import GameInfo, SimulationResult


class BaseGame(ABC):
    """Every simulation module must subclass this and implement compute() and info()."""

    @abstractmethod
    def info(self) -> GameInfo:
        """Return the game's metadata, parameter spec, and theory card."""
        ...

    @abstractmethod
    def compute(self, config: dict) -> SimulationResult:
        """Run the simulation with the given configuration and return results."""
        ...
