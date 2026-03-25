from __future__ import annotations

from typing import List, Optional, Tuple
from matplotlib.patches import Rectangle
from dataclasses import dataclass
import matplotlib.pyplot as plt
from enum import Enum
import numpy as np


from petres.grids.cornerpoint import CornerPointGrid


class AquiferDirection(Enum):
    """Aquifer connection directions."""
    I_MINUS = "I-"  # left boundary (scan i increasing)
    I_PLUS = "I+"   # right boundary (scan i decreasing)
    J_MINUS = "J-"  # top boundary (scan j increasing)
    J_PLUS = "J+"   # bottom boundary (scan j decreasing)


@dataclass
class AquanconEntry:
    """Single AQUANCON entry."""
    aquifer_id: int
    i_min: int  # 1-indexed
    i_max: int  # 1-indexed
    j_min: int  # 1-indexed
    j_max: int  # 1-indexed
    k_min: int  # 1-indexed
    k_max: int  # 1-indexed
    face: str   # 'I-', 'I+', 'J-', 'J+'

    def to_eclipse_format(self) -> str:
        return (
            f"   {self.aquifer_id} {self.i_min} {self.i_max} "
            f"{self.j_min} {self.j_max} {self.k_min} {self.k_max} "
            f"'{self.face}' /"
        )


class AQUANCONGenerator:
    """
    Generator for Eclipse AQUANCON keyword entries.

    Works with CornerPointGrid:
      - grid.active shape: (nk, nj, ni) and indexed as [k, j, i]
      - Lateral indexing is j,i everywhere
    """

    def __init__(self, grid: CornerPointGrid):
        self.grid = grid
        self._entries: List[AquanconEntry] = []

        # enforce CornerPointGrid conventions
        assert self.grid.active.shape == (self.grid.nk, self.grid.nj, self.grid.ni), (
            f"Expected active.shape == (nk, nj, ni) == ({self.grid.nk}, {self.grid.nj}, {self.grid.ni}), "
            f"got {self.grid.active.shape}."
        )

    def clear(self) -> AQUANCONGenerator:
        self._entries.clear()
        return self

    @property
    def entries(self) -> List[AquanconEntry]:
        return self._entries.copy()

    def to_eclipse_format(self) -> List[str]:
        return [e.to_eclipse_format() for e in self._entries]

    def export(self, filename: Optional[str] = None) -> str:
        if not self._entries:
            return ""

        lines = ["AQUANCON"]
        lines.extend(self.to_eclipse_format())
        lines.append("/\n")
        result = "\n".join(lines)

        if filename:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(result)

        return result

    def __str__(self) -> str:
        return self.export()

    def __repr__(self) -> str:
        return f"AquanconGenerator(entries={len(self._entries)})"

    # ----------------------------
    # Public API
    # ----------------------------

    def add_aquifer(
        self,
        aquifer_id: int,
        direction: AquiferDirection,
        k_lower: int = 1,
        k_upper: int = 1,
    ) -> "AquanconGenerator":
        """
        Add aquifer connection to a lateral boundary.

        Notes (CornerPointGrid):
        - Active mask is 3D (nk, nj, ni).
        - AQUANCON is specified using (I1,I2,J1,J2,K1,K2,'FACE').
        - We select boundary cells per (j,i) for each k, then merge to ranges.
        """
        if k_lower < 1 or k_upper < 1:
            raise ValueError("k_lower/k_upper must be 1-indexed and >= 1.")
        if k_lower > k_upper:
            raise ValueError("k_lower must be <= k_upper.")
        if k_upper > self.grid.nk:
            raise ValueError(f"k_upper={k_upper} exceeds grid.nk={self.grid.nk}.")

        k0 = k_lower - 1
        k1 = k_upper - 1

        # 2D boundary mask over (j,i), computed from the union of active cells in [k0:k1]
        boundary_mask_ji = self._get_boundary_mask_ji(direction, k0=k0, k1=k1)

        if not boundary_mask_ji.any():
            return self

        ranges = self._extract_ranges_vectorized_ji(boundary_mask_ji, direction)

        for i_min0, i_max0, j_min0, j_max0 in ranges:
            self._entries.append(
                AquanconEntry(
                    aquifer_id=aquifer_id,
                    i_min=i_min0 + 1,
                    i_max=i_max0 + 1,
                    j_min=j_min0 + 1,
                    j_max=j_max0 + 1,
                    k_min=k_lower,
                    k_max=k_upper,
                    face=direction.value,
                )
            )

        return self

    # ----------------------------
    # Boundary selection (j,i)
    # ----------------------------

    def _get_boundary_mask_ji(
        self,
        direction: AquiferDirection,
        k0: int,
        k1: int,
    ) -> np.ndarray:
        """
        Compute boundary mask in j,i indexing.

        We first reduce 3D active (nk,nj,ni) to 2D active_ji by OR-ing over k in [k0..k1].
        Then we select "first active" along the scan direction.

        Returns
        -------
        mask_ji : np.ndarray
            shape (nj, ni), indexed as mask_ji[j, i]
        """
        # inclusive k range
        active_2d = self.grid.active[k0 : k1 + 1].any(axis=0)  # (nj, ni)
        nj, ni = active_2d.shape

        mask = np.zeros((nj, ni), dtype=bool)

        if direction == AquiferDirection.I_MINUS:
            # for each row j, first active i from left
            has_active = active_2d.any(axis=1)          # (nj,)
            first_i = active_2d.argmax(axis=1)          # (nj,)
            j = np.where(has_active)[0]
            mask[j, first_i[has_active]] = True

        elif direction == AquiferDirection.I_PLUS:
            # for each row j, first active i from right
            has_active = active_2d.any(axis=1)          # (nj,)
            first_i_flipped = active_2d[:, ::-1].argmax(axis=1)
            first_i = (ni - 1) - first_i_flipped
            j = np.where(has_active)[0]
            mask[j, first_i[has_active]] = True

        elif direction == AquiferDirection.J_MINUS:
            # for each column i, first active j from top (small j)
            has_active = active_2d.any(axis=0)          # (ni,)
            first_j = active_2d.argmax(axis=0)          # (ni,)
            i = np.where(has_active)[0]
            mask[first_j[has_active], i] = True

        elif direction == AquiferDirection.J_PLUS:
            # for each column i, first active j from bottom (large j)
            has_active = active_2d.any(axis=0)          # (ni,)
            first_j_flipped = active_2d[::-1, :].argmax(axis=0)
            first_j = (nj - 1) - first_j_flipped
            i = np.where(has_active)[0]
            mask[first_j[has_active], i] = True

        return mask

    # ----------------------------
    # Ranges (j,i -> AQUANCON ranges)
    # ----------------------------

    def _extract_ranges_vectorized_ji(
        self,
        mask_ji: np.ndarray,
        direction: AquiferDirection,
    ) -> List[Tuple[int, int, int, int]]:
        """
        Extract rectangular ranges from a boundary mask (j,i indexing).

        Returns tuples (i_min, i_max, j_min, j_max) in 0-index.
        """
        j_indices, i_indices = np.where(mask_ji)
        if len(i_indices) == 0:
            return []

        ranges: List[Tuple[int, int, int, int]] = []

        if direction in (AquiferDirection.I_MINUS, AquiferDirection.I_PLUS):
            # boundary is on constant i; group by i and merge consecutive j
            sort_order = np.lexsort((j_indices, i_indices))
            i_sorted = i_indices[sort_order]
            j_sorted = j_indices[sort_order]

            i_changes = np.concatenate(([True], i_sorted[1:] != i_sorted[:-1]))
            group_starts = np.where(i_changes)[0]
            group_ends = np.concatenate((group_starts[1:], [len(i_sorted)]))

            for gs, ge in zip(group_starts, group_ends):
                i_val = int(i_sorted[gs])
                j_vals = j_sorted[gs:ge]

                j_diff = np.diff(j_vals, prepend=j_vals[0] - 2, append=j_vals[-1] + 2)
                run_starts = np.where(j_diff != 1)[0]

                for r in range(len(run_starts) - 1):
                    j0 = int(j_vals[run_starts[r]])
                    j1 = int(j_vals[run_starts[r + 1] - 1])
                    ranges.append((i_val, i_val, j0, j1))

        else:
            # boundary is on constant j; group by j and merge consecutive i
            sort_order = np.lexsort((i_indices, j_indices))
            j_sorted = j_indices[sort_order]
            i_sorted = i_indices[sort_order]

            j_changes = np.concatenate(([True], j_sorted[1:] != j_sorted[:-1]))
            group_starts = np.where(j_changes)[0]
            group_ends = np.concatenate((group_starts[1:], [len(j_sorted)]))

            for gs, ge in zip(group_starts, group_ends):
                j_val = int(j_sorted[gs])
                i_vals = i_sorted[gs:ge]

                i_diff = np.diff(i_vals, prepend=i_vals[0] - 2, append=i_vals[-1] + 2)
                run_starts = np.where(i_diff != 1)[0]

                for r in range(len(run_starts) - 1):
                    i0 = int(i_vals[run_starts[r]])
                    i1 = int(i_vals[run_starts[r + 1] - 1])
                    ranges.append((i0, i1, j_val, j_val))

        return ranges

    # ----------------------------
    # Visualization (optional, lateral only)
    # ----------------------------

    def visualize_boundary_mask(
        self,
        direction: AquiferDirection,
        k_lower: int = 1,
        k_upper: int = 1,
        figsize: Tuple[float, float] = (12, 10),
    ) -> plt.Figure:
        """
        Visualize boundary mask in the i-j plane (j,i indexing).

        This uses pillar_top XY geometry (CornerPointGrid.pillars) for plotting.
        Corners are taken from pillars.pillar_top[j, i, 0:2].
        """
        if k_lower < 1 or k_upper < 1 or k_lower > k_upper or k_upper > self.grid.nk:
            raise ValueError("Invalid k_lower/k_upper (must be 1-indexed within grid.nk).")

        k0 = k_lower - 1
        k1 = k_upper - 1

        active_2d = self.grid.active[k0 : k1 + 1].any(axis=0)  # (nj, ni)
        boundary_mask = self._get_boundary_mask_ji(direction, k0=k0, k1=k1)

        nj, ni = active_2d.shape

        # Use pillar-top vertices to get cell rectangles (works for rectilinear pillars too)
        v = self.grid.pillars.pillar_top  # (nj+1, ni+1, 3)

        fig, ax = plt.subplots(figsize=figsize)

        rectangles_inactive = []
        rectangles_active = []
        rectangles_boundary = []

        for j in range(nj):
            for i in range(ni):
                # Cell corners from pillar vertices (top surface)
                x0, y0 = v[j, i, 0], v[j, i, 1]
                x1, y1 = v[j, i + 1, 0], v[j, i + 1, 1]
                x2, y2 = v[j + 1, i, 0], v[j + 1, i, 1]

                # Rectangle assumption: axis-aligned / rectilinear in XY
                # (If your pillars define skewed cells, this is only an approximation.)
                x_min = min(x0, x1, x2)
                x_max = max(x0, x1, x2)
                y_min = min(y0, y1, y2)
                y_max = max(y0, y1, y2)

                rect = Rectangle((x_min, y_min), x_max - x_min, y_max - y_min)

                is_active = bool(active_2d[j, i])
                is_boundary = bool(boundary_mask[j, i])

                if is_boundary:
                    rectangles_boundary.append(rect)
                elif is_active:
                    rectangles_active.append(rect)
                else:
                    rectangles_inactive.append(rect)

        from matplotlib.collections import PatchCollection
        from matplotlib.patches import Patch

        if rectangles_inactive:
            ax.add_collection(
                PatchCollection(
                    rectangles_inactive,
                    facecolors="lightgray",
                    edgecolors="gray",
                    linewidths=0.5,
                    alpha=0.5,
                )
            )
        if rectangles_active:
            ax.add_collection(
                PatchCollection(
                    rectangles_active,
                    facecolors="white",
                    edgecolors="black",
                    linewidths=0.5,
                )
            )
        if rectangles_boundary:
            ax.add_collection(
                PatchCollection(
                    rectangles_boundary,
                    facecolors="red",
                    edgecolors="darkred",
                    linewidths=2,
                    alpha=0.7,
                )
            )

        # bounds from vertices
        xs = v[:, :, 0]
        ys = v[:, :, 1]
        ax.set_xlim(xs.min(), xs.max())
        ax.set_ylim(ys.min(), ys.max())
        ax.set_aspect("equal")
        ax.set_xlabel("X", fontsize=12, fontweight="bold")
        ax.set_ylabel("Y", fontsize=12, fontweight="bold")
        ax.set_title(f"Boundary Mask: {direction.value} (K {k_lower}-{k_upper})", fontsize=14, fontweight="bold")

        legend_elements = [
            Patch(facecolor="red", edgecolor="darkred", label="Boundary cells", alpha=0.7),
            Patch(facecolor="white", edgecolor="black", label="Active cells"),
            Patch(facecolor="lightgray", edgecolor="gray", label="Inactive cells", alpha=0.5),
        ]
        ax.legend(handles=legend_elements, loc="upper left", bbox_to_anchor=(1.02, 1), fontsize=10)

        stats_text = (
            f"Boundary cells: {int(boundary_mask.sum())}\n"
            f"Active (K-range): {int(active_2d.sum())}\n"
            f"Inactive (K-range): {int((~active_2d).sum())}"
        )
        ax.text(
            0.02,
            0.98,
            stats_text,
            transform=ax.transAxes,
            fontsize=10,
            verticalalignment="top",
            bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.8),
        )

        plt.tight_layout()
        return fig
