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
        code_preview=r"C:\Users\Tayfun\Desktop\GitHub\Personal\petres\slides\examples\grid_modeling\assets\zone.png",
        footer_right="1 / 3",
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
        code_preview=r"C:\Users\Tayfun\Desktop\GitHub\Personal\petres\slides\examples\grid_modeling\assets\pillars.png",
        footer_right="2 / 3",
        theme="light",
    )
)


step3_code = """
from petres.grids import CornerPointGrid

grid = CornerPointGrid.from_zones(
    pillars=pillars,
    zones=[zone],
)

grid.show(z_scale=5)
grid.to_grdecl("model.GRDECL")
"""

deck.add(
    CodeSnippet(
        header_left="STEP 03",
        header_right_first="Tutorials",
        header_right_second="Grid Modeling",
        title="Build and Export the Grid",
        description="Build the Corner-Point grid, visualize it, and export it to Eclipse GRDECL format.",
        code=step3_code,
        context=step1_code + step2_code,
        code_preview=r"C:\Users\Tayfun\Desktop\GitHub\Personal\petres\slides\examples\grid_modeling\assets\grid.png",
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

deck.to_pdf("Petres Tutorials — Grid Modeling.pdf")