import numpy
from objects import Model


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
        return Model(numpy.array([[0, 1]]), numpy.array([(0, 0, 1)]))
    vertices, faces = _create_cube_faces(dimensions)
    triangles = []
    for face in faces:
        for t in face_to_triangles(face):
            triangles.append(t)
    return Model(vertices, numpy.array(triangles))

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
    return vertices, numpy.array(faces)

def face_to_triangles((a, b, c, d)):
    return [(a, b, c), (c, b, a), (a, d, c), (c, d, a)]

assert numpy.allclose(
    create_cube(2).vertices,
    [[0, 1, 0, 1],
     [0, 0, 1, 1]])
assert numpy.allclose(
    create_cube(2).triangles,
    [(0, 1, 3), (3, 1, 0), (0, 2, 3), (3, 2, 0)])
assert create_cube(2).vertices.shape == (2, 4)
assert create_cube(2).triangles.shape == (2 * 2, 3)
assert create_cube(3).vertices.shape == (3, 8)
assert create_cube(3).triangles.shape == (2 * 12, 3)

#TODO
def create_sphere(dimensions):
    raise NotImplementedError


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
    return Model(numpy.array(vertices).transpose(), triangles)
