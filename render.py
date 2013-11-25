import pyglet
from pyglet.gl import *

from graphics import create_projection, create_translation, create_scaling, create_identity,\
    create_rotation, create_cube, project, load_dae, PALETTE_BLUE

DIMENSIONS = 3

LINE_WIDTH = 2.0

CAPTION = "4D"
X_SIZE, Y_SIZE = 640, 480
INTERVAL = 1.0 / 60.0


class Renderer(object):
    def __init__(self):
        self.x_size = X_SIZE
        self.y_size = Y_SIZE
        self.window = pyglet.window.Window(self.x_size, self.y_size,
                                           caption=CAPTION, vsync=False)
        self.projection = create_projection()
        self.projection = (
            create_translation((100., 100., 0.))).dot(
                self.projection).dot(
                    create_scaling((100., 100., 1.)))
        self.camera = create_identity().dot(create_translation([0., 0., 0.]))

        self.create_bounding_cube()
        self.duck = load_dae("Toy N060512.dae")

        pyglet.clock.schedule_interval(self.update, INTERVAL)
        self.fps_counter = pyglet.clock.ClockDisplay()
        self.window.event(self.on_draw)

    def create_bounding_cube(self):
        bounding_vertices, bounding_triangles = create_cube(DIMENSIONS)
        bounding_vertices *= .96
        bounding_vertices += .2
        self.bounding_cube = (bounding_vertices, bounding_triangles)
        print self.bounding_cube[1]

    def on_draw(self):
        """Automatically called upon every clock tick, renders the board"""
        self.window.clear()
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        glClearDepth(1.0)
        glDepthFunc(GL_LESS)
        glEnable(GL_DEPTH_TEST)

        glDisable(GL_TEXTURE_2D)
        self.render(*self.bounding_cube)
        self.render(*self.duck)
        glEnable(GL_TEXTURE_2D)

        self.fps_counter.draw()

    CAMERA_ROTATION = (
        create_translation([.5, .5, .5]).dot(
            create_rotation(.009, 0, 1)).dot(
#            create_rotation(.009, 0, 2)).dot(
                create_translation([-.5, -.5, -.5]))
    )

    def update(self, dt):
        self.camera = self.camera.dot(self.CAMERA_ROTATION)

    def render(self, vertices, triangles, palette=PALETTE_BLUE):
        glLineWidth(LINE_WIDTH)
        vertices = project(self.projection, self.camera, vertices)
        i = 0
        for a, b, c in triangles:
            x1, y1, c1 = vertices[:, a]
            x2, y2, c2 = vertices[:, b]
            x3, y3, c3 = vertices[:, c]
            if c1 < 0 or c2 < 0 or c3 < 0:
                continue
            c1 = min(1., c1)
            c2 = min(1., c2)
            c3 = min(1., c3)
            pyglet.graphics.draw(3, GL_TRIANGLES,
                                 ('v3f', (x1, y1, -c1, x2, y2, -c2, x3, y3, -c3)),
                                 ('c3B', palette.color(c1) + palette.color(c2) + palette.color(c3)))


if __name__ == '__main__':
    renderer = Renderer()
    pyglet.app.run()
