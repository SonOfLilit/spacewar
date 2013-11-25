import numpy
import collada

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


def apply_matrix(matrix, vertices):
    # add a row of 1 values to the bottom, to convert 3D coordinates
    # to 3D homogenous coordinates
    homogenous = numpy.vstack((vertices,
                               numpy.ones((1, vertices.shape[1]),
                                          dtype=vertices.dtype)))
    return matrix.dot(homogenous)[:-1, :]
_v = numpy.random.random((DIMENSIONS, 10))
assert numpy.allclose(
    apply_matrix(create_identity(), _v),
    _v
)
assert numpy.allclose(
    apply_matrix(numpy.zeros([DIMENSIONS + 1] * 2), _v),
    0 * _v
)
assert numpy.allclose(
    apply_matrix(create_scaling([2.] * DIMENSIONS), _v),
    2 * _v
)

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
