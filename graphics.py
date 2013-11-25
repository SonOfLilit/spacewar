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


def create_cube(dimensions):
    """
    Returns a `dimensions`-dimensional cube, e.g. a square (2D) or a hypercube (4D).
    The cube spans from [0, ..., 0] to [1, ..., 1].
    
    The shape is returned as a tuple (vertices, triangles) where
    vertices is a KxD table (each column is a point in D dimensions,
    and there are K points) and triangles is a list of triplets of indices of
    rows in vertices.
    
    e.g., a 1D cube (a line) would be
    ([[0],
      [1]],
     [(0, 1, 0)]),
    and a 2D cube (a square) would be
    ([[0, 1, 0, 1],
      [0, 0, 1, 1]],
     [(0, 1, 2), (2, 1, 0), (0, 3, 2), (2, 3, 0)]),
    which describes the points: {A: (0, 0), B: (1, 0), C: (0, 1), D: (1, 1)}
    and triangles (A, B, C) and (C, D, A) CW and CCW.
    """
    if dimensions == 1:
        return numpy.array([[0, 1]]), numpy.array([(0, 1, 0)])
    vertices, faces = _create_cube_faces(dimensions)
    triangles = []
    for face in faces:
        for t in face_to_triangles(face):
            triangles.append(t)
    return vertices, numpy.array(triangles)

def _create_cube_faces(dimensions):
    if dimensions == 1:
        return numpy.array([[0., 1.]]), numpy.array([])
    if dimensions == 2:
        return numpy.array([[0., 1., 0., 1.],
                            [0., 0., 1., 1.]]), numpy.array([(0, 1, 3, 2)])
    v, f = _create_cube_faces(dimensions - 1)
    nv = v.shape[1]
    nf = f.shape[0]
    # extrude all vertices in new axis
    vertices = numpy.zeros((v.shape[0] + 1, v.shape[1] * 2))
    for i in xrange(nv):
        vertices[:-1, 2 * i] = v[:, i]
        vertices[:-1, 2 * i + 1] = v[:, i]
        vertices[-1, 2 * i + 1] = 1.
    # all the originals, all their mirrors, and a connection from each
    # old vertex with its right and the parallels on top
    faces = []
    for face in f:
        faces.append(face)
        opposite = [x + nv for x in face]
        faces.append(tuple(opposite))
        for i in xrange(4):
            ii = (i + 1) % 4
            faces.append((face[i], face[ii], face[ii] + nv, face[i] + nv))
    return vertices, faces

print _create_cube_faces(3)
def face_to_triangles((a, b, c, d)):
    return [(a, b, c), (c, b, a), (a, d, c), (c, d, a)]

assert numpy.allclose(
    create_cube(2)[0],
    [[0, 1, 0, 1],
     [0, 0, 1, 1]])
assert numpy.allclose(
    create_cube(2)[1],
    [(0, 1, 3), (3, 1, 0), (0, 2, 3), (3, 2, 0)])
assert create_cube(3)[0].shape[1] == 8
assert create_cube(3)[1].shape[0] == 2 * 12

def project(projection, camera, source):
    """Apply camera matrix, then projection matrix, to source, which
    has 3D points as columns.
    """
    # add a row of 1 values to the bottom, to convert 3D coordinates
    # to 3D homogenous coordinates
    homogenous = numpy.vstack((source,
                               numpy.ones((1, source.shape[1]),
                                          dtype=source.dtype)))
    # apply camera, then projection
    nonhomogenous = projection.dot(camera).dot(homogenous)
    # translate homogenous to 2D points: divide x, y by w
    vertices = nonhomogenous[:-1, :]
    vertices[:2] /= nonhomogenous[-1, :]
    assert vertices.shape == (SCREEN_DIMENSIONS + 1, source.shape[1])
    return vertices


def load_dae(filename):
    mesh = collada.Collada(filename)
    vertex_dict = {}
    vertices = []
    triangles = []
    def point(p):
        t = tuple(p)
        if t not in vertex_dict:
            vertex_dict[t] = len(vertex_dict)
            vertices.append(t)
        return vertex_dict[t]
    for triangle in mesh.geometries[0].primitives[0].triangleset():
        points = map(point, triangle.vertices)
        assert len(points) == 3
        triangles.append(points)
    return numpy.array(vertices).transpose(), triangles

