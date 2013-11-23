import graphics
import objects
import render

s1 = objects.Sun(graphics.create_identity(), graphics.create_cube(3))

location_2 = graphics.create_identity()
location_2[0, -1] = 2

#s2 = objects.Sun(location_2, graphics.create_cube(3))

w = objects.World([s1])

r = render.Renderer(w)
r.run()
