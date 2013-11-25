import numpy as np
from graphics import apply_matrix


class Model(object):
    def __init__(self, vertices, triangles):
        self.vertices = vertices
        self.triangles = triangles

    def transform(self, matrix):
        self.vertices = apply_matrix(matrix, self.vertices)

    def unite(self, other):
        raise NotImplementedError

    def shift(self, shift):
        raise NotImplementedError

    def rescale(self, scale):
        raise NotImplementedError

    def rotate(self, angle, axis):
        raise NotImplementedError


class World(object):
    def __init__(self, objects=None):
        self.objects = objects
        if self.objects is None:
            self.objects = []

    def add_object(self, obj):
        self.objects.append(obj)

    def destroy_object(self, obj):
        self.objects.remove(obj)

    def resolve_collisions(self):
        pass

    def update(self):
        for obj in self.objects:
            obj.update()
        self.resolve_collisions()


class Object(object):
    def __init__(self, world_to_object, model):
        self.world_to_object = world_to_object
        self.model = model

    @property
    def object_to_world(self):
        return np.linalg.inv(self.world_to_object)

    def update(self):
        pass


class Sun(Object):
    pass


class Body(Object):
    def __init__(self, world_to_object, model, velocity):
        Object.__init__(self, world_to_object, model)
        self.velocity = velocity


class Spaceship(Object):
    def update(self):
        #ask for rotation commands

        #rotate

        #engine commands

        #total acceleration
        pass