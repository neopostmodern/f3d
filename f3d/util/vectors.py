#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'neopostmodern'

import numpy as numpy
import math


class Vector3:
    def __init__(self, *args, **kwargs):
        if len(args) is 0:
            x = 0
            y = 0
            z = 0

        elif len(args) is 3:
            # assume they passed x, y, z
            [x, y, z] = args

        else:
            argument = args[0]

            # todo: don't explicitly type, ducking!
            if isinstance(argument, dict):
                x, y, z = argument['x'], argument['y'], argument['z']

            elif hasattr(argument, "__getitem__"):
                [x, y, z] = argument

            else:
                raise ValueError("Can't create Vector3 with", argument)

        self.x = x
        self.y = y
        self.z = z

    @property
    def array_representation(self):
        return numpy.array([self.x, self.y, self.z])

    @array_representation.setter
    def array_representation(self, value):
        self.x = value[0]
        self.y = value[1]
        self.z = value[2]
        return self.array_representation

    def __add__(self, other):
        modified_vector = Vector3(0, 0, 0)
        if isinstance(other, Vector3):
            modified_vector.array_representation = self.array_representation + other.array_representation
        else:
            modified_vector.array_representation = self.array_representation + other

        return modified_vector

    def __sub__(self, other):
        modified_vector = Vector3(0, 0, 0)
        if isinstance(other, Vector3):
            modified_vector.array_representation = self.array_representation - other.array_representation
        else:
            modified_vector.array_representation = self.array_representation - other

        return modified_vector

    @classmethod
    def from_object(cls, object_like):
        return cls(object_like.x, object_like.y, object_like.z)

    @classmethod
    def from_dict(cls, dict_like):
        return cls(dict_like['x'], dict_like['y'], dict_like['z'])

    @classmethod
    def from_list(cls, array_like):
        instance = cls(0, 0, 0)
        instance.array_representation = array_like  # todo: performance!!!
        return instance

    @staticmethod
    def rotation_matrix_x(angle):
        return numpy.array([[1, 0, 0],
                            [0, math.cos(angle), -1 * math.sin(angle)],
                            [0, math.sin(angle), math.cos(angle)]])

    @staticmethod
    def rotation_matrix_y(angle):
        return numpy.array([[math.cos(angle), 0, math.sin(angle)],
                            [0, 1, 0],
                            [-1 * math.sin(angle), 0, math.cos(angle)]])

    @staticmethod
    def rotation_matrix_z(angle):
        return numpy.array([[math.cos(angle), -1 * math.sin(angle), 0],
                            [math.sin(angle), math.cos(angle), 0],
                            [0, 0, 1]])

    # todo: https://en.wikipedia.org/wiki/Rodrigues%27_rotation_formula#Statement
    def rotate(self, rotation):
        rotated_vector = self.array_representation

        rotated_vector = Vector3.rotation_matrix_x(rotation.x).dot(rotated_vector)
        rotated_vector = Vector3.rotation_matrix_y(rotation.y).dot(rotated_vector)
        rotated_vector = Vector3.rotation_matrix_z(rotation.z).dot(rotated_vector)

        self.array_representation = rotated_vector

        return self

    def convert_to_radian(self):
        self.array_representation = [math.radians(value) for value in self.array_representation]
        return self

# todo: implement via subclassing of ndarray http://docs.scipy.org/doc/numpy/user/basics.subclassing.html
class Vector2():
    def __init__(self, x, y):
        self.x = x
        self.y = y

    @property
    def array_representation(self):
        return numpy.array([self.x, self.y])

    @array_representation.setter
    def array_representation(self, value):
        self.x = value[0]
        self.y = value[1]
        return self.array_representation

    @classmethod
    def from_object(cls, object_like):
        return cls(object_like.x, object_like.y)

    @classmethod
    def from_dict(cls, dict_like, keys=None):
        if keys is None:
            keys = ['x', 'y']
        return cls(dict_like[keys[0]], dict_like[keys[1]])


def intersect(ray_origin, ray_direction, plane_origin, plane_normal_vector, allow_negative=False):

    # https://en.wikipedia.org/wiki/Line%E2%80%93plane_intersection#Algebraic_form
    distance_factor = ((plane_origin - ray_origin).dot(plane_normal_vector)) \
                      / ray_direction.dot(plane_normal_vector)

    if distance_factor <= 0 or allow_negative:
        return None

    return ray_origin + ray_direction * distance_factor
