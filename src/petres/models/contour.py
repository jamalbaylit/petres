from __future__ import annotations

from collections.abc import Iterable, Iterator
from dataclasses import dataclass, field
from typing import Literal
import numpy as np

from petres.models import wells


def _sample_indices(
    xy: np.ndarray,
    sampling_distance: float | None,
    max_points: int | None,
) -> np.ndarray:
    n = xy.shape[0]
    idx = np.arange(n)

    if sampling_distance is not None and n > 2:
        diffs = np.diff(xy, axis=0)
        seg_len = np.hypot(diffs[:, 0], diffs[:, 1])
        cum_len = np.concatenate(([0.0], np.cumsum(seg_len)))
        buckets = (cum_len / sampling_distance).astype(np.int64)

        keep = np.empty(n, dtype=bool)
        keep[0] = True
        keep[1:] = buckets[1:] != buckets[:-1]
        idx = idx[keep]

    if max_points is not None and idx.size > max_points:
        pos = np.unique(np.linspace(0, idx.size - 1, max_points).astype(np.int64))
        idx = idx[pos]

    return idx



@dataclass(frozen=True, slots=True)
class Contour:
    """A single geological contour line."""

    xy: np.ndarray
    z: float

    def __post_init__(self) -> None:
        xy = np.asarray(self.xy, dtype=float)

        if xy.ndim != 2 or xy.shape[1] != 2:
            raise ValueError(
                f"`xy` must have shape (n, 2), got {xy.shape}"
            )

        if xy.shape[0] < 2:
            raise ValueError(
                "`xy` must contain at least two points."
            )

        if not np.all(np.isfinite(xy)):
            raise ValueError(
                "`xy` contains NaN or infinite values."
            )

        z = float(self.z)

        if not np.isfinite(z):
            raise ValueError("`z` must be finite.")

        xy = np.ascontiguousarray(xy)
        xy.setflags(write=False)

        object.__setattr__(self, "xy", xy)
        object.__setattr__(self, "z", z)

    @property
    def is_closed(self) -> bool:
        """Whether the contour is closed."""
        return self.xy.shape[0] >= 4 and np.allclose(self.xy[0], self.xy[-1])

    @property
    def is_open(self) -> bool:
        """Whether the contour is open."""
        return not self.is_closed
    
    @property
    def n_points(self) -> int:
        "Number of points in the contour."
        return self.xy.shape[0]

    @property
    def x(self) -> np.ndarray:
        "X coordinates of the contour points."
        return self.xy[:, 0]

    @property
    def y(self) -> np.ndarray:
        "Y coordinates of the contour points."
        return self.xy[:, 1]

    @property
    def xyz(self) -> np.ndarray:
        "XYZ coordinates of the contour points."
        z = np.full((self.n_points, 1), self.z)
        return np.hstack((self.xy, z))

    @property
    def bounds(self) -> tuple[float, float, float, float]:
        "Returns the bounding box of the contour as (xmin, ymin, xmax, ymax)."
        xmin, ymin = self.xy.min(axis=0)
        xmax, ymax = self.xy.max(axis=0)
        return xmin, ymin, xmax, ymax

    @property
    def length(self) -> float:
        "Returns the total length of the contour."
        return np.linalg.norm(
            np.diff(self.xy, axis=0),
            axis=1,
        ).sum()

    @property
    def centroid(self) -> np.ndarray:
        "Returns the centroid of the contour as (x, y)."
        return self.xy.mean(axis=0)

    @classmethod
    def from_xyz(cls, xyz: np.ndarray) -> "Contour":
        """Create a contour from XYZ coordinates.
        
        Parameters
        ----------
        xyz : np.ndarray, shape (n, 3)
            Coordinates of the contour vertices. Each row must contain
            ``[x, y, z]`` values, and all points must have the same
            ``z`` value.

            For example::

                np.array([
                    [100.0, 200.0, -1800.0],
                    [110.0, 205.0, -1800.0],
                    [120.0, 210.0, -1800.0],
                ])

        Returns
        -------
        Contour
            A contour whose ``xy`` coordinates are taken from the first
            two columns of ``xyz`` and whose ``z`` value is taken from
            the third column.

        Raises
        ------
        ValueError
            If ``xyz`` does not have shape ``(n, 3)``, contains NaN or
            infinite values, or contains points with different ``z``
            values.
        """
        
        xyz = np.asarray(xyz, dtype=float)

        if xyz.ndim != 2 or xyz.shape[1] != 3:
            raise ValueError(
                f"`xyz` must have shape (n, 3), got {xyz.shape}"
            )

        if not np.all(np.isfinite(xyz)):
            raise ValueError(
                "`xyz` contains NaN or infinite values."
            )

        if not np.all(xyz[:, 2] == xyz[0, 2]):
            raise ValueError(
                "`xyz` must contain points with the same z value."
            )

        return cls(
            xy=xyz[:, :2],
            z=xyz[0, 2],
        )

    def resample(
        self,
        *,
        sampling_distance: float | None = None,
        max_points: int | None = None,
    ) -> "Contour":
        """Return a new Contour with a reduced set of points.

        Parameters
        ----------
        sampling_distance : float or None
            Minimum distance between kept points along the contour.
        max_points : int or None
            Maximum number of points to keep, evenly subsampled afterward.
        """
        if self.n_points < 2:
            raise ValueError(f"Contour at z={self.z} has fewer than 2 points.")

        idx = _sample_indices(self.xy, sampling_distance, max_points)
        return Contour(xy=self.xy[idx], z=self.z)





@dataclass
class ContourMap:
    """Collection of geological contour lines.

    Parameters
    ----------
    contours : iterable of Contour
        Contour lines belonging to the same contour map.
    """

    contours: list[Contour] = field(default_factory=list)
    
    def __post_init__(self) -> None:
        self.contours = list(self.contours)

        if not all(isinstance(contour, Contour) for contour in self.contours):
            raise TypeError("All items in `contours` must be `Contour` objects.")



    @property
    def n_contours(self) -> int:
        """Number of contours in the map."""
        return len(self.contours)

    @property
    def n_points(self) -> int:
        """Total number of vertices across all contours."""
        return sum(contour.n_points for contour in self.contours)

    @property
    def bounds(self) -> tuple[float, float, float, float]:
        """Return map bounds as ``(xmin, ymin, xmax, ymax)``."""
        if not self.contours:
            raise ValueError("Cannot calculate bounds of an empty contour map.")

        bounds = np.array([contour.bounds for contour in self.contours])

        return (
            bounds[:, 0].min(),
            bounds[:, 1].min(),
            bounds[:, 2].max(),
            bounds[:, 3].max(),
        )

    def resample(
        self,
        *,
        sampling_distance: float | None = None,
        max_points_per_contour: int | None = None,
    ) -> "ContourMap":
        """Return a new ContourMap with each contour decimated."""
        return ContourMap([
            contour.resample(
                sampling_distance=sampling_distance,
                max_points=max_points_per_contour,
            )
            for contour in self
        ])
    
    def to_xyz(self) -> np.ndarray:
        """Return all contour vertices as an ``(n, 3)`` array.

        The contour boundaries are not preserved in the returned array.
        """
        if not self.contours:
            return np.empty((0, 3), dtype=float)

        return np.vstack([
            contour.xyz
            for contour in self.contours
        ])

    def append(self, contour: Contour) -> None:
        """Add a contour to the map."""
        if not isinstance(contour, Contour):
            raise TypeError("`contour` must be a `Contour` object.")

        self.contours.append(contour)

    def extend(self, contours: Iterable[Contour]) -> None:
        """Add multiple contours to the map."""
        for contour in contours:
            self.append(contour)


    def show(
        self,
        *,
        view: Literal["3d", "2d"] = "3d",
    ) -> None:
        """
        Render the zone in 3D or 2D.

        Dispatches to `show3d` or `show2d` depending on `view`, passing through
        any grid specification arguments.

        Parameters
        ----------
        view : {'3d', '2d'}, default '3d'
            Target visualization backend.

        Raises
        ------
        ValueError
            If `view` is not one of {'3d', '2d'}.

        Examples
        --------
        >>> zone.show()
        >>> zone.show(view="2d", xlim=(0, 500), ylim=(0, 500), ni=100, nj=100)
        """
        view = view.strip().lower()
        if view == "3d":
            self.show3d()
        elif view == "2d":
            self.show2d()
        else:
            raise ValueError(f"Invalid view: {view!r}. Must be '3d' or '2d'.")

    def show2d(self) -> None:
        """Render the contour map in 2D."""
        from ..viewers.viewer2d.matplotlib.viewer import Matplotlib2DViewer

        viewer = Matplotlib2DViewer()
        viewer.add_contour_map(self)
        viewer.show()


    def __len__(self) -> int:
        return self.n_contours

    def __iter__(self) -> Iterator[Contour]:
        return iter(self.contours)

    def __getitem__(self, index: int | slice) -> Contour | list[Contour]:
        return self.contours[index]