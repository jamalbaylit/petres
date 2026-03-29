from petres.interpolators import UKInterpolator
from petres.grids import CornerPointGrid
from petres.models import VerticalWell
import numpy as np

grid = CornerPointGrid.from_regular(
    xlim=(0, 100),
    ylim=(0, 100),
    zlim=(0, 20),
    ni=100,
    nj=100,
    nk=10,
)
grid.show()

porosity = grid.properties.create(
    name='porosity',
    eclipse_keyword='PORO',
    description='Porosity'
)


well1 = VerticalWell(name="Well 1", x=20, y=78)
well3 = VerticalWell(name="Well 3", x=32, y=55)

well1.add_sample(name='porosity', value=100, depth=10)
well3.add_sample(name='porosity', value=50, depth=15)
# well1.add_sample(name='porosity', value=50, depth=12)
# well1.add_sample(name='porosity', value=25, depth=20)

porosity.from_wells(
    wells=[well1, well3],
    interpolator=UKInterpolator(),
    mode='xyz'
)
porosity.show()