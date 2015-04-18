#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'neopostmodern'

import numpy as numpy
import math


class Vector3():
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        self.array_representation = numpy.array([x, y, z])

    @classmethod
    def from_array(cls, array_like):
        return cls(array_like[0], array_like[1], array_like[2])

    @classmethod
    def from_object(cls, object_like):
        return cls(object_like.x, object_like.y, object_like.z)

    @classmethod
    def from_dict(cls, dict_like):
        return cls(dict_like['x'], dict_like['y'], dict_like['z'])

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

    def rotate(self, rotation):
        rotated_vector = self.array_representation

        rotated_vector = Vector3.rotation_matrix_x(rotation.x).dot(rotated_vector)
        rotated_vector = Vector3.rotation_matrix_y(rotation.y).dot(rotated_vector)
        rotated_vector = Vector3.rotation_matrix_z(rotation.z).dot(rotated_vector)

        self.from_array(rotated_vector)

        return self


class Vector2():
    def __init__(self, x, y):
        self.x = x
        self.y = y

        self.array_representation = numpy.array([x, y])

    @classmethod
    def from_array(cls, array_like):
        return cls(array_like[0], array_like[1])

    @classmethod
    def from_object(cls, object_like):
        return cls(object_like.x, object_like.y)

    @classmethod
    def from_dict(cls, dict_like):
        return cls(dict_like['x'], dict_like['y'])


def intersect(ray_origin, ray_direction, plane_origin, plane_normal_vector, allow_negative=False):

    # https://en.wikipedia.org/wiki/Line%E2%80%93plane_intersection#Algebraic_form
    distance_factor = ((plane_origin.array_representation - ray_origin).dot(plane_normal_vector.array_representation)) \
                      / ray_direction.array_representation.dot(plane_normal_vector.array_representation)

    if distance_factor <= 0 or allow_negative:
        return None

    return ray_origin + ray_direction.array_representation * distance_factor