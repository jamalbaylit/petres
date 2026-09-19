import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from slides import CodeSnippet, MainPage, SlideDeck, Outro

deck = SlideDeck(width=1350, height=1080)
deck.add(
    MainPage(
        title="Zone Modeling",
        description="Create zones from horizons and divide them into layers.",
        theme="dark",
        logo=True,
        footer_left="petres.io",
        footer_right="Swipe →",
    )
)


# Each CodeSnippet is highlighted in isolation (its own jedi.Script), so a
# later step referencing names an earlier step defined (horizon, zone,
# np) can't resolve them on its own -- pass the earlier steps' code as
# context= so jedi can still infer types, without it being rendered.
step1_code = """
from petres.interpolators import IDWInterpolator
from petres.models import Horizon

horizon = Horizon(
    name="Top Layer",
    xy=[[20, 78], [70, 80], [32, 55]],
    depth=[100, 110, 90],
    interpolator=IDWInterpolator(power = 2)
)
        """
deck.add(
    CodeSnippet(
        header_left="STEP 01",
        header_right_first="Tutorials",
        header_right_second="Zone Modeling",
        title="Define a Horizon",
        description="Start with a few depth measurements and turn them into a continuous horizon.",
        code=step1_code,
        footer_right="1 / 3",
        theme="light",
    )
)


step2_code = """
import numpy as np

zone = horizon.to_zone(
    name="Reservoir",
    depth=20
)

zone.show(
    x=np.linspace(0, 100, 50),
    y=np.linspace(0, 100, 50)
)
        """
deck.add(
    CodeSnippet(
        header_left="STEP 02",
        header_right_first="Tutorials",
        header_right_second="Zone Modeling",
        title="Create a Zone",
        description="Turn the horizon into a zone by defining its thickness.",
        code=step2_code,
        context=step1_code,
        code_preview=r"C:\Users\Tayfun\Desktop\GitHub\Personal\petres\slides\examples\zone_modeling\assets\zone.png",
        footer_right="2 / 3",
        theme="light",
    )
)

deck.add(
    CodeSnippet(
        header_left="STEP 03",
        header_right_first="Tutorials",
        header_right_second="Zone Modeling",
        title="Subdivide the Zone",
        description="Divide the zone into three layers with the specified relative thicknesses.",
        code="""
zone.divide(fractions=[0.3, 0.5, 0.2])

zone.show(
    x=np.linspace(0, 100, 50),
    y=np.linspace(0, 100, 50)
)
        """,
        context=step1_code + step2_code,
        code_preview=r"C:\Users\Tayfun\Desktop\GitHub\Personal\petres\slides\examples\zone_modeling\assets\layering.png",
        footer_right="3 / 3",
        theme="light",
    )
)
deck.add(
    Outro(
        title="Explore Further",
        theme="dark",
        logo=True,
        footer_left="petres.io",

        footer_left_title="TUTORIALS & DOCUMENTATION",
        footer_right_title="SOURCE CODE",
        footer_right="github.com/jamalbaylit/petres",
    )
)
deck.to_pdf("Petres Tutorials — Zone Modeling.pdf")