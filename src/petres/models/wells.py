from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, Sequence

from .._validation import _validate_finite_float, _validate_nonempty_string


@dataclass
class VerticalWell:
    """Store a vertical well with tops and property samples.

    A well holds horizon tops and arbitrary property samples. Property samples
    are tracked per property name in one of two mutually exclusive modes:
    scalar mode (depth is ``None``) or depth-indexed mode (depth provided).
    Mixing these modes for the same property is not allowed.

    Parameters
    ----------
    name : str
        Well identifier.
    x : float
        Well-head x coordinate.
    y : float
        Well-head y coordinate.
    tops : dict[str, float], optional
        Mapping of horizon name to measured top depth.
    samples : dict[str, dict[float | None, float]], optional
        Property samples; keys are property names, values are depth→value maps.
    _sample_modes : dict[str, Literal['scalar', 'depth']], optional
        Internal map tracking whether samples for a property are scalar or
        depth-indexed.
    """

    name: str
    x: float
    y: float
    tops: dict[str, float] = field(default_factory=dict)
    samples: dict[str, dict[float | None, float]] = field(default_factory=dict)
    _sample_modes: dict[str, Literal['scalar', 'depth']] = field(default_factory=dict)

    # check value types and validity in __post_init__
    def __post_init__(self) -> None:
        """Validate and normalize the initialized well state."""
        self.name = _validate_nonempty_string(self.name, "name")
        self.x = _validate_finite_float(self.x, "x")
        self.y = _validate_finite_float(self.y, "y")

        for name, depth in self.tops.items():
            name, depth = self._validate_tops_sample(name, depth)
            self.tops[name] = depth

    def _validate_tops_sample(self, name: str, value: float) -> tuple[str, float]:
        """Validate and normalize one top entry.

        Parameters
        ----------
        name : str
            Horizon name.
        value : float
            Top depth value.

        Returns
        -------
        tuple[str, float]
            Normalized ``(name, value)`` pair.
        """
        try:
            name = _validate_nonempty_string(name, "name")
        except Exception as e:
            raise ValueError(f"Invalid horizon name in tops: {name!r}. Must be a non-empty string.") from e
        
        try:
            value = _validate_finite_float(value, f"value")
        except Exception as e:
            raise ValueError(f"Invalid depth value for horizon '{name}': {value!r}. Must be a number.") from e
        return name, value



    @property
    def xy(self) -> tuple[float, float]:
        """Return well-head coordinates.

        Returns
        -------
        tuple[float, float]
            Two-element tuple ``(x, y)``.
        """
        return (self.x, self.y)
    
    def add_top(self, horizon: str, depth: float) -> None:
        """Add a new horizon top depth.

        Parameters
        ----------
        horizon : str
            Horizon name to add.
        depth : float
            Measured top depth.

        Raises
        ------
        ValueError
            If the horizon name/depth is invalid or the horizon already exists.
        """
        horizon, depth = self._validate_tops_sample(horizon, depth)
        if horizon in self.tops:
            raise ValueError(f"Top '{horizon}' already exists in well '{self.name}'.")
        self.tops[horizon] = depth

    def get_top(self, horizon: str) -> float:
        """Return the top depth for a horizon.

        Parameters
        ----------
        horizon : str
            Horizon name to query.

        Returns
        -------
        float
            Stored depth for ``horizon``.

        Raises
        ------
        KeyError
            If ``horizon`` is not present in this well.
        """
        if horizon not in self.tops:
            raise KeyError(f"Top '{horizon}' not found in well '{self.name}'. Existing tops: {list(self.tops.keys())}")
        return self.tops[horizon]

    def remove_top(self, horizon: str) -> None:
        """Remove an existing horizon top depth.

        Parameters
        ----------
        horizon : str
            Horizon name to remove.

        Raises
        ------
        KeyError
            If ``horizon`` is not present.
        """
        if horizon not in self.tops:
            raise KeyError(f"Top '{horizon}' not found in well '{self.name}'. Cannot remove non-existent top.")
        del self.tops[horizon]


    # ----------------------------
    # Property samples
    # ----------------------------
    def add_sample(
        self,
        name: str,
        value: float,
        depth: float | None = None,
    ) -> None:
        """Add a property sample in scalar or depth-indexed mode.

        For one property name, all samples must use the same storage mode:
        scalar (``depth=None``) or depth-indexed (``depth`` provided).

        Parameters
        ----------
        name : str
            Property name.
        value : float
            Sample value.
        depth : float or None, default=None
            Depth for depth-indexed mode. Use ``None`` for scalar mode.

        Raises
        ------
        ValueError
            If values are invalid, a mode conflict occurs, or a duplicate
            sample key exists.

        Examples
        --------
        >>> well = VerticalWell(name="W1", x=100.0, y=200.0)
        >>> well.add_sample(name="poro", value=0.18)
        >>> well.add_sample(name="perm", value=120.0, depth=2500.0)
        """
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

    def get_sampling_mode(self, name: str) -> Literal['scalar', 'depth']:
        """Return the storage mode for samples of a property.

        Parameters
        ----------
        name : str
            Property name.

        Returns
        -------
        'scalar' or 'depth'
            Storage mode for samples of this property.

        Raises
        ------
        ValueError
            If ``name`` is not a non-empty string.
        KeyError
            If no samples exist for ``name``.
        """
        name = _validate_nonempty_string(name, "name")
        if name not in self._sample_modes:
            raise KeyError(f"No samples found for property '{name}' in well '{self.name}'.")
        return self._sample_modes[name]

    def get_sample(
        self,
        name: str,
        depth: float | None = None,
    ) -> dict[float, float] | float:
        """Return one sample or all samples for a property.

        Parameters
        ----------
        name : str
            Property name.
        depth : float or None, default=None
            For depth-indexed properties, provide a depth to return one value.
            If ``None``, returns all depth-indexed samples as a shallow copy.
            Scalar properties always return their scalar value.

        Returns
        -------
        dict[float, float] or float
            For depth-indexed properties:
            - ``depth`` provided: sample value at that depth.
            - ``depth`` omitted: shallow copy of depth→value mapping.
            For scalar properties: scalar sample value.

        Raises
        ------
        ValueError
            If ``name`` is not a non-empty string, ``depth`` is non-finite,
            or a depth is provided for a scalar property.
        KeyError
            If no samples exist for ``name`` or no sample exists at ``depth``.
        """
        name = _validate_nonempty_string(name, "name")
        depth = _validate_finite_float(depth, "depth") if depth is not None else None

        try:
            samples = self.samples[name]
        except KeyError:
            raise KeyError(f"No samples found for property '{name}' in well '{self.name}'.")

        sampling_mode = self.get_sampling_mode(name)

        if sampling_mode == 'scalar':
            if depth is not None:
                raise ValueError(
                    f"Cannot query sample for '{name}' at depth={depth} because "
                    f"this property is stored in scalar mode."
                )
            return samples[None]

        if depth is not None:
            if depth not in samples:
                raise KeyError(
                    f"Sample for property '{name}' at depth={depth} "
                    f"not found in well '{self.name}'."
                )
            return samples[depth]

        return dict(samples)

    def remove_sample(
        self,
        name: str,
        depth: float | None = None,
    ) -> None:
        """Remove a stored sample and clean empty internal state.

        Parameters
        ----------
        name : str
            Property name.
        depth : float or None, default=None
            Depth key used for removal. Use ``None`` for scalar samples.

        Raises
        ------
        ValueError
            If ``name`` is not a non-empty string or ``depth`` is non-finite
            when provided.
        KeyError
            If no sample exists for ``(name, depth)``.
        """
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





def _validate_well_sequence(
    wells: VerticalWell | list[VerticalWell] | tuple[VerticalWell, ...]
) -> tuple[VerticalWell, ...]:
    """Validate that the input is a VerticalWell or a sequence of VerticalWells."""

    if isinstance(wells, VerticalWell):
        wells = (wells,)
    elif isinstance(wells, (list, tuple)):
        if not all(isinstance(w, VerticalWell) for w in wells):
            raise TypeError("All items in `wells` must be instances of `VerticalWell`.")
        wells = tuple(wells)
    else:
        raise TypeError("`wells` must be a VerticalWell or a sequence of VerticalWells.")

    return wells