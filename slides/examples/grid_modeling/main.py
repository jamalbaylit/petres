import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from slides import CodeSnippet, MainPage, SlideDeck, Outro

deck = SlideDeck(width=1350, height=1080)

deck.add(
    MainPage(
        title="Grid Modeling",
        description="Build a Corner-Point grid from horizons, zones, and pillars.",
        theme="dark",
        logo=True,
        footer_left="petres.io",
        footer_right="Swipe →",
    )
)


step1_code = """
from petres.models import Zone

zone = Zone(
    name="Reservoir",
    top=h1,
    base=h2,
)

zone.divide(nk=4)
"""

deck.add(
    CodeSnippet(
        header_left="STEP 01",
        header_right_first="Tutorials",
        header_right_second="Grid Modeling",
        title="Define the Zones",
        description="Define the vertical intervals and their layer discretization.",
        code=step1_code,
        footer_right="1 / 4",
        theme="light",
    )
)


step2_code = """
from petres.grids import PillarGrid

pillars = PillarGrid.from_regular(
    xlim=(0, 100),
    ylim=(0, 100),
    ni=50,
    nj=50,
)
"""

deck.add(
    CodeSnippet(
        header_left="STEP 02",
        header_right_first="Tutorials",
        header_right_second="Grid Modeling",
        title="Create the Pillars",
        description="Define the lateral grid geometry.",
        code=step2_code,
        footer_right="2 / 4",
        theme="light",
    )
)


step3_code = """
grid = CornerPointGrid.from_zones(
    pillars=pillars,
    zones=[zone],
)

grid.show()
"""

deck.add(
    CodeSnippet(
        header_left="STEP 03",
        header_right_first="Tutorials",
        header_right_second="Grid Modeling",
        title="Build the Grid",
        description="Combine the pillars and zones into a Corner-Point grid.",
        code=step3_code,
        footer_right="3 / 4",
        theme="light",
    )
)


step4_code = """
grid.to_grdecl(
    "reservoir.GRDECL"
)
"""

deck.add(
    CodeSnippet(
        header_left="STEP 04",
        header_right_first="Tutorials",
        header_right_second="Grid Modeling",
        title="Export the Grid",
        description="Export the grid to Eclipse GRDECL format.",
        code=step4_code,
        footer_right="4 / 4",
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

deck.to_pdf("Petres Tutorials — Grid Modeling.pdf")