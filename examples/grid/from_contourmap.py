from petres.models import Contour, ContourMap, Horizon
from petres.interpolators import RBFInterpolator
import numpy as np


contours = [
    Contour(
        xy=np.array([
            [180, 180],
            [260, 120],
            [380, 90],
            [520, 105],
            [650, 150],
            [760, 230],
            [790, 340],
            [750, 450],
            [650, 530],
            [520, 560],
            [380, 545],
            [260, 490],
            [180, 400],
            [155, 290],
            [180, 180],
        ]),
        z=-1800.0,
    ),

    Contour(
        xy=np.array([
            [250, 210],
            [320, 165],
            [430, 145],
            [550, 160],
            [650, 215],
            [700, 295],
            [690, 380],
            [630, 450],
            [530, 490],
            [420, 485],
            [320, 440],
            [260, 370],
            [230, 285],
            [250, 210],
        ]),
        z=-1900.0,
    ),

    Contour(
        xy=np.array([
            [330, 245],
            [400, 205],
            [490, 200],
            [575, 225],
            [630, 280],
            [640, 345],
            [605, 405],
            [535, 440],
            [450, 445],
            [380, 415],
            [335, 360],
            [315, 295],
            [330, 245],
        ]),
        z=-2000.0,
    ),

    Contour(
        xy=np.array([
            [400, 275],
            [455, 245],
            [520, 250],
            [570, 285],
            [590, 330],
            [570, 375],
            [520, 405],
            [460, 405],
            [410, 380],
            [380, 335],
            [400, 275],
        ]),
        z=-2100.0,
    ),

    Contour(
        xy=np.array([
            [450, 300],
            [490, 285],
            [530, 300],
            [550, 330],
            [535, 365],
            [495, 380],
            [455, 360],
            [440, 330],
            [450, 300],
        ]),
        z=-2200.0,
    ),

    # Open contour representing the deeper structure continuing
    # outside the mapped area.
    Contour(
        xy=np.array([
            [50, 650],
            [150, 610],
            [260, 590],
            [380, 585],
            [500, 600],
            [620, 630],
            [750, 680],
            [900, 730],
        ]),
        z=-2300.0,
    ),
]

cm = ContourMap(
    contours = contours
)


cm.show2d()
h1 = Horizon.from_contour_map(name="Horizon 1", contour_map=cm, interpolator=RBFInterpolator(
    kernel="thin_plate_spline",
    neighbors=50,
))
xmin, ymin, xmax, ymax = cm.bounds
h1.show3d(x=np.linspace(xmin, xmax, 50), y=np.linspace(ymin, ymax, 50))