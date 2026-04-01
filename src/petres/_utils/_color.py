from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import warnings

import numpy as np
from matplotlib.colors import to_rgba
from matplotlib.pyplot import cm



@dataclass(frozen=True)
class Color:
    """
    Immutable RGBA color representation with flexible parsing.

    This class provides a unified way to construct colors from multiple
    commonly used formats and export them into normalized RGBA form
    (values in the range [0.0, 1.0]).

    The class optionally uses ``matplotlib.colors.to_rgba`` for advanced
    color parsing. If `matplotlib` is not installed, a fallback parser
    is used that supports only hex strings and RGB/RGBA tuples.

    Parameters
    ----------
    value : Any
        Color specification. Supported input formats depend on whether
        `matplotlib` is available.

        If `matplotlib` **is installed**, the following formats are supported:

        - Named colors (e.g., ``"red"``, ``"steelblue"``)
        - Hex strings:
            - ``"#RRGGBB"``
            - ``"#RRGGBBAA"``
        - RGB or RGBA tuples/lists:
            - Floats in [0, 1]
            - Integers in [0, 255]
        - Another ``Color`` instance

        If `matplotlib` **is NOT installed**, the fallback parser supports:

        - Hex strings starting with ``"#"``:
            - ``"#RRGGBB"``
            - ``"#RRGGBBAA"``
        - RGB or RGBA tuple/list:
            - 3 values → interpreted as RGB
            - 4 values → interpreted as RGBA
            - Integers (0–255) are normalized automatically
            - Floats must already be in [0, 1]
        - Another ``Color`` instance

        In fallback mode, named color strings (e.g., ``"red"``) are NOT supported.

    opacity : float, optional
        Optional alpha override in range [0.0, 1.0]. If provided,
        it replaces any alpha value defined in `value`.

    Attributes
    ----------
    r : float
        Red channel in range [0.0, 1.0].
    g : float
        Green channel in range [0.0, 1.0].
    b : float
        Blue channel in range [0.0, 1.0].
    a : float
        Alpha (opacity) channel in range [0.0, 1.0].

    Raises
    ------
    ValueError
        If:
        - Opacity is outside [0, 1]
        - Hex string has invalid length
        - Tuple does not contain 3 or 4 elements
    TypeError
        If input type is unsupported or invalid for the current parsing mode.

    Notes
    -----
    - Internally, all channels are stored as floats in [0, 1].
    - The class is immutable (`frozen=True`).
    - Using `matplotlib` is recommended for full color-name support.

    Examples
    --------
    Using hex strings
    >>> Color("#FF0000")
    >>> Color("#FF000080")  # with alpha

    Using tuples (integers)
    >>> Color((255, 0, 0))
    >>> Color((255, 0, 0, 128))

    Using tuples (floats)
    >>> Color((1.0, 0.0, 0.0))
    >>> Color((1.0, 0.0, 0.0, 0.5))

    Using named colors (requires matplotlib)
    >>> Color("steelblue")

    Overriding opacity
    >>> Color("#FF0000", opacity=0.3)

    Export formats
    >>> c = Color("#336699")
    >>> c.as_rgb()
    (0.2, 0.4, 0.6)
    >>> c.as_rgba()
    (0.2, 0.4, 0.6, 1.0)
    >>> c.as_hex()
    '#336699'
    >>> c.as_hex(include_alpha=True)
    '#336699FF'
    """


    r: float
    g: float
    b: float
    a: float = 1.0


    def __init__(self, value: Any, opacity: float | None = None) -> None:
        """Initialize the Color instance from the given color specification.

        Raises
        ------
        ValueError
            If ``opacity`` is outside [0.0, 1.0], if a hex string has an
            invalid length, or if a tuple does not contain 3 or 4 elements.
        TypeError
            If the input type is unsupported or invalid for the current
            parsing mode.
        """
        r, g, b, a = self.to_rgba(value)
        
        if opacity is not None:
            if not (0.0 <= opacity <= 1.0):
                raise ValueError(f"Opacity must be between 0 and 1. Got: {opacity}")
            a = float(opacity)

        object.__setattr__(self, "r", r)
        object.__setattr__(self, "g", g)
        object.__setattr__(self, "b", b)
        object.__setattr__(self, "a", a)

    def to_rgba(self, value: Any) -> tuple[float, float, float, float]:
        """Parse a color specification into a normalized RGBA tuple.

        Parameters
        ----------
        value : Any
            Color specification acceptable by ``matplotlib.colors.to_rgba``.

        Returns
        -------
        tuple[float, float, float, float]
            Parsed RGBA values in [0, 1].

        Raises
        ------
        ValueError
            If parsing fails.
        """
        try:
            rgba = to_rgba(value)
            return rgba
        except Exception as e:
            raise ValueError(f"Failed to parse color using matplotlib: {value}") from e
        
    def _parse_color(self, value: Any) -> tuple[float, float, float, float]:
        """Parse a color value using the fallback parser (no matplotlib).

        Parameters
        ----------
        value : Any
            Hex string, RGB/RGBA tuple or list, or another ``Color`` instance.

        Returns
        -------
        tuple[float, float, float, float]
            Normalized RGBA values in [0, 1].
        """
        if isinstance(value, Color):
            return value.r, value.g, value.b, value.a

        # HEX
        if isinstance(value, str) and value.startswith("#"):
            s = value[1:]
            if len(s) == 6:
                r = int(s[0:2], 16)
                g = int(s[2:4], 16)
                b = int(s[4:6], 16)
                a = 255
            elif len(s) == 8:
                r = int(s[0:2], 16)
                g = int(s[2:4], 16)
                b = int(s[4:6], 16)
                a = int(s[6:8], 16)
            else:
                raise ValueError("Invalid hex color.")
            return r/255, g/255, b/255, a/255

        # Tuple/list
        if isinstance(value, (tuple, list)):
            vals = list(value)
            if len(vals) not in (3, 4):
                raise ValueError("Color tuple must have 3 or 4 values.")

            if all(isinstance(v, int) for v in vals):
                vals = [v/255 for v in vals]
            else:
                vals = [float(v) for v in vals]

            r = vals[0]
            g = vals[1]
            b = vals[2]
            a = vals[3] if len(vals) == 4 else 1.0
            return r, g, b, a

        # Named strings → let backend handle it
        if isinstance(value, str):
            # Instead of resolving here, store as sentinel
            # We'll detect this later
            raise TypeError(
                f"String input only supports hex format starting with '#'. Got '{value}'."
            )
        raise TypeError(f"Unsupported color type: {type(value)}")

    # -----------------------------
    # Backend exports
    # -----------------------------
    def as_rgb(self) -> tuple[float, float, float]:
        """Return the color as an RGB tuple.

        Returns
        -------
        tuple[float, float, float]
            Red, green, and blue channels, each in [0.0, 1.0].
        """
        return (self.r, self.g, self.b)

    def as_rgba(self) -> tuple[float, float, float, float]:
        """Return the color as an RGBA tuple.

        Returns
        -------
        tuple[float, float, float, float]
            Red, green, blue, and alpha channels, each in [0.0, 1.0].
        """
        return (self.r, self.g, self.b, self.a)

    def as_hex(self, include_alpha: bool = False) -> str:
        """Return the color as a CSS hex string.

        Parameters
        ----------
        include_alpha : bool, optional
            When ``True``, appends the alpha channel as a two-digit hex
            suffix (e.g. ``"#RRGGBBAA"``). Defaults to ``False``.

        Returns
        -------
        str
            Hex color string in ``"#RRGGBB"`` or ``"#RRGGBBAA"`` format.
        """
        r = int(round(self.r * 255))
        g = int(round(self.g * 255))
        b = int(round(self.b * 255))
        a = int(round(self.a * 255))
        if include_alpha:
            return f"#{r:02X}{g:02X}{b:02X}{a:02X}"
        return f"#{r:02X}{g:02X}{b:02X}"
    
    @staticmethod
    def get_discrete_cmap(n: int, cmap: str) -> list[tuple[float, float, float]]:
        """Sample ``n`` discrete RGB colors from a Matplotlib colormap.

        Parameters
        ----------
        n : int
            Number of colors to sample. Must be positive.
        cmap : str
            Name of a valid Matplotlib colormap (e.g. ``"viridis"``).

        Returns
        -------
        list[tuple[float, float, float]]
            List of ``n`` RGB tuples, each with values in [0.0, 1.0].

        Raises
        ------
        ValueError
            If ``n`` is not positive or if ``cmap`` is not a recognized
            Matplotlib colormap name.
        """
        if n <= 0:
            raise ValueError("Number of colors must be positive.")
        try:
            colors = cm.get_cmap(cmap)(np.linspace(0, 1, n))
            return [tuple(c[:3]) for c in colors]  # Convert to RGB tuples
        except Exception as e:
            raise ValueError(f"Failed to get discrete cmap for '{cmap}'. Ensure the colormap name is valid.") from e 
