import graphics
import shapes
import objects
import render

s1 = objects.Sun(graphics.create_identity(), shapes.create_cube(3))
s1.model.transform(graphics.create_translation([0.1, 0.1, 4.6]))
s1.model.transform(graphics.create_scaling([0.1, 0.1, 0.1]))

location_2 = graphics.create_identity()
location_2[0, -1] = 2

#s2 = objects.Sun(location_2, shapes.create_cube(3))

w = objects.World([s1])

r = render.Renderer(w)
r.run()
