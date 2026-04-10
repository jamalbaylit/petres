from petres.models import VerticalWell

well1 = VerticalWell(name="Well 1", x=20, y=78)

well1.add_sample(name='porosity', value=100)
# well1.add_sample(name='porosity', value=50, depth=12)
# well1.add_sample(name='porosity', value=25, depth=20)


print(well1.get_sample(name='porosity'))
