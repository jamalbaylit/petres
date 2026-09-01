import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from slides import CodeSnippet, MainPage, SlideDeck

deck = SlideDeck(width=1350, height=1080)

deck.add(
    MainPage(
        title="Zone Modeling",
        description="Create zones from defined horizon and Transform horizons into volumetric zones and subdivide them into meaningful geological layers.",
        theme="dark",
        logo=True,
        footer_left="petres.io",
        footer_right="Swipe →",
    )
)




deck.add(
    CodeSnippet(
        header_left="Step 01",
        header_right_first="Tutorials",
        header_right_second="Hello World",
        title="Define a Horizon",
        description="Start with a set of scattered depth measurements and interpolate them into a continuous horizon.",
        code="""
from petres.interpolators import IDWInterpolator
from petres.models import Horizon

horizon = Horizon(
    name="Top Layer",
    xy=[[20, 78], [70, 80], [32, 55]],
    depth=[100, 110, 90],
    interpolator=IDWInterpolator(power = 2)
)
        """,
        code_preview="path/to/hello_world_preview.png",
        footer_right="1 / 4",
        theme="light",
    )
)

deck.add(
    CodeSnippet(
        header_left="Step 02",
        header_right_first="Tutorials",
        header_right_second="Hello World",
        title="Hello World Example",
        description="This is a simple code snippet.",
        code="print('Hello, World!')",
        footer_right="2 / 4",
        theme="light",
    )
)

deck.to_pdf("presentation.pdf")