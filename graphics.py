import numpy
from objects import Model

DIMENSIONS = 3
SCREEN_DIMENSIONS = 2


class Palette(object):
    def __init__(self, zero, one):
        self.zero, self.one = numpy.array(zero), numpy.array(one)

    def color(self, c):
        assert 0. <= c <= 1.
        precise = (1. - c) * self.one + c * self.zero
        integer = numpy.rint((precise * 255)).astype(int)
        return tuple(integer)
PALETTE_BLUE = Palette([0., 0., 1.], [1., 1., 1.])
assert PALETTE_BLUE.color(0) == tuple([255, 255, 255])
assert PALETTE_BLUE.color(1) == tuple([0, 0, 255])
assert PALETTE_BLUE.color(.5) == (128, 128, 255)


def create_identity():
    return numpy.identity(DIMENSIONS + 1)


def create_projection():
    """
    Returns a 4x4 projection matrix that, applied to 3d homogenous
    coordinates [x, y, z, 1] of a point in world-space, would give
    [x'w, y'w, z'w, w] such that x' = x'w/w and y' = y'w/w are the
    point's screen-space coordinates.
    
    @see project()
    """
    m = numpy.identity(DIMENSIONS + 1)
    m[-1][-1] = 0.
    m[-1][-2] = 1.
    return m
assert numpy.allclose(
    create_projection(),
    create_projection().dot(create_projection()))


def create_scaling(axes):
    """
    When called with len(axes) = N, returns a matrix that scales each
    axis in N-dimensional homogenous coordinates by the given amount.
    
    e.g., to zoom in the Y axis in 3D by 2, use create_scale([1, 2, 1]).
    """
    return numpy.diag(list(axes) + [0])
assert numpy.allclose(
    create_scaling([1, 2, 3]).dot([1, 1, 1, 1])[:-1],
    [1, 2, 3])


def create_translation(point):
    """
    When called with len(point) = N, returns a matrix that translates
    N-dimensional homogenous coordinates by the given amount.
    
    e.g., to move in the Y axis in 2D by 2, use create_translation([0, 2]).
    """
    m = numpy.identity(DIMENSIONS + 1)
    m[:, -1] = list(point) + [1.]
    return m

assert numpy.allclose(
    create_translation([1, 2, 3]).dot([1, 1, 1, 1])[:-1],
    [2, 3, 4])


def create_rotation(angle, axis1, axis2):
    """
    Returns a DIMENSIONS-dimensional rotation matrix that rotates points
    by angle on the axis1-axis2 plane.
    
    e.g., to rotate by 90 degrees in the XZ plane ([1, 0, 0] -> [0, 0, 1]),
    use create_rotation(pi/2, 0, 2).
    """
    m = numpy.identity(DIMENSIONS + 1)
    s = numpy.sin(angle)
    c = numpy.cos(angle)
    m[axis1][axis1] = c
    m[axis1][axis2] = -s
    m[axis2][axis1] = s
    m[axis2][axis2] = c
    return m
assert numpy.allclose(
    create_rotation(numpy.pi/2, 0, 1).dot([1, 0, 0, 1])[:-1],
    [0, 1, 0])
assert numpy.allclose(
    create_rotation(numpy.pi/2, 1, 2).dot([1, 0, 0, 1])[:-1],
    [1, 0, 0])
assert numpy.allclose(
    create_rotation(numpy.pi/4, 0, 1).dot([1, 0, 0, 1])[:-1],
    [1/numpy.sqrt(2), 1/numpy.sqrt(2), 0])


def create_cube(dimensions):
    """
    Returns a `dimensions`-dimensional cube, e.g. a square (2D) or a hypercube (4D).
    The cube spans from [0, ..., 0] to [1, ..., 1].
    
    The shape is returned as a tuple (vertices, lines) where vertices is a KxD table
    (each column is a point in D dimensions, and there are K points) and lines is a
    list of pairs of indices of rows in vertices.
    
    e.g., a 1D cube (a line) would be
    ([[0],
      [1]],
     [(0, 1)]),
    and a 2D cube (a square) would be
    ([[0, 1, 0, 1],
      [0, 0, 1, 1]],
     [(0, 1), (1, 2), (2, 3), (3, 0)]),
    which describes the points: {A: (0, 0), B: (1, 0), C: (0, 1), D: (1, 1)}
    and line segments between the points (A, B), (B, C), (C, D) and (D, A),
    or alternatively the "less orderly"
    ([[0, 1, 0, 1],
      [0, 1, 1, 0]],
     [(2, 1), (3, 0), (0, 2), (1, 3)]),
    which describes the points: {A: (0, 0), B: (1, 1), C: (0, 1), D: (1, 0)}
    and line segments between the points (C, B), (D, A), (A, C) and (B, D).
    """
    if dimensions == 1:
        return Model(numpy.array([[0, 1]]), numpy.array([(0, 1)]))
    cube = create_cube(dimensions - 1)
    v, l = cube.vertices, cube.lines
    nv = v.shape[1]
    nl = v.shape[0]
    vertices = numpy.hstack([v, v])
    vertices = numpy.vstack((vertices, numpy.zeros(shape=(1, vertices.shape[1]))))
    vertices[-1, nv:] = 1
    lines = numpy.vstack([l,
                          [(x + nv, y + nv) for x, y in l],
                          [(x, x + nv) for x in xrange(nv)]])
    return Model(vertices, lines)

assert numpy.allclose(
    create_cube(2).vertices,
    [[0, 1, 0, 1],
     [0, 0, 1, 1]])
assert numpy.allclose(
    create_cube(2).lines,
    [(0, 1), (2, 3), (0, 2), (1, 3)])

assert create_cube(DIMENSIONS).vertices.shape == (DIMENSIONS, 2 ** DIMENSIONS)
assert create_cube(DIMENSIONS).lines.shape == (2 ** (DIMENSIONS - 1) * DIMENSIONS, 2)


#TODO
def create_sphere(dimensions):
    raise NotImplementedError


def project(projection, camera, vertices_to_world, raw_vertices):
    """Apply camera matrix, then projection matrix, to source, which
    has 3D points as columns.
    """
    # add a row of 1 values to the bottom, to convert 3D coordinates
    # to 3D homogenous coordinates
    homogenous = numpy.vstack((raw_vertices,
                               numpy.ones((1, raw_vertices.shape[1]),
                                          dtype=raw_vertices.dtype)))
    # apply camera, then projection
    nonhomogenous = projection.dot(camera.dot(vertices_to_world)).dot(homogenous)
    # translate homogenous to 2D points: divide x, y by w
    screen_coordinates = nonhomogenous[:-1, :]
    screen_coordinates[:2] /= nonhomogenous[-1, :]
    assert screen_coordinates.shape == (SCREEN_DIMENSIONS + 1, raw_vertices.shape[1])
    return screen_coordinates
