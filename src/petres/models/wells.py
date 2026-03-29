from __future__ import annotations

from dataclasses import dataclass, field
from typing_extensions import Literal

from .._validation import _validate_finite_float, _validate_nonempty_string


@dataclass(frozen=True)
class WellSample:
    name: str
    value: float
    z: float | None = None


@dataclass
class VerticalWell:
    name: str
    x: float
    y: float
    tops: dict[str, float] = field(default_factory=dict)
    samples: dict[str, dict[float | None, float]] = field(default_factory=dict)
    _sample_modes: dict[str, Literal['scalar', 'depth']] = field(default_factory=dict)
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


    # ----------------------------
    # Property samples
    # ----------------------------
    def add_sample(
        self,
        name: str,
        *,
        value: float,
        depth: float | None = None,
    ) -> None:
        name = _validate_nonempty_string(name, "name")
        value = _validate_finite_float(value, "value")
        if depth is not None:
            mode = 'depth'
            depth = _validate_finite_float(depth, "depth")
        else:
            mode = 'scalar'

        depth_map = self.samples.setdefault(name, {})
        current_mode = self._sample_modes.setdefault(name, mode)
        if current_mode != mode:
            raise ValueError(
                f"Cannot add sample for '{name}' in mode '{mode}' because "
                f"existing samples for this property are in mode '{current_mode}'."
            )
        
        if depth in depth_map:
            raise ValueError(
                f"Sample for '{name}' at depth={depth} already exists in well '{self.name}'."
            )

        depth_map[depth] = value

    def get_sample(
        self,
        name: str,
        depth: float | None = None,
    ) -> float:
        name = _validate_nonempty_string(name, "name")
        if depth is not None:
            depth = _validate_finite_float(depth, "depth")


        if name not in self.samples or depth not in self.samples[name]:
            raise KeyError(
                f"Sample for property '{name}' at depth={depth} "
                f"not found in well '{self.name}'."
            )

        return self.samples[name][depth]

    def get_samples(
        self,
        name: str,
    ) -> dict[float | None, float]:
        name = _validate_nonempty_string(name, "name")
        return dict(self.samples.get(name, {}))

    def remove_sample(
        self,
        name: str,
        depth: float | None = None,
    ) -> None:
        name = _validate_nonempty_string(name, "name")
        if depth is not None:
            depth = _validate_finite_float(depth, "depth")

        if name not in self.samples or depth not in self.samples[name]:
            raise KeyError(
                f"Sample for property '{name}' at depth={depth} "
                f"not found in well '{self.name}'."
            )

        del self.samples[name][depth]

        if not self.samples[name]:
            del self.samples[name]
            del self._sample_modes[name]