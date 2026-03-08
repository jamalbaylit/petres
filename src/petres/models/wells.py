from __future__ import annotations

from dataclasses import dataclass, field

@dataclass
class VerticalWell:
    name: str
    x: float
    y: float
    tops: dict[str, float] = field(default_factory=dict)
    
    @property
    def xy(self) -> tuple[float, float]:
        return (self.x, self.y)
    
    def add_top(self, horizon: str, depth: float) -> None:
        if not isinstance(horizon, str) or not horizon:
            raise ValueError("`horizon` name must be a non-empty string.")
        if not isinstance(depth, (int, float)):
            raise TypeError("`depth` must be a number.")
        if horizon in self.tops:
            raise ValueError(f"Top '{horizon}' already exists in well '{self.name}'.")
        self.tops[horizon] = float(depth)

    def get_top(self, horizon: str) -> float:
        if horizon not in self.tops:
            raise KeyError(f"Top '{horizon}' not found in well '{self.name}'. Existing tops: {list(self.tops.keys())}")
        return self.tops[horizon]

    def remove_top(self, horizon: str) -> None:
        if horizon not in self.tops:
            raise KeyError(f"Top '{horizon}' not found in well '{self.name}'. Cannot remove non-existent top.")
        del self.tops[horizon]