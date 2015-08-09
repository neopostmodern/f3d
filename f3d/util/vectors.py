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

    def __repr__(self):
        return "Vector3{x: %.4f, y: %.4f, z: %.4f}" % tuple(self.array_representation)

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

    def rotate(self, rotation):
        rotation_matrix = numpy.identity(3)
        rotation_matrix = Vector3.rotation_matrix_x(rotation.x).dot(rotation_matrix)
        rotation_matrix = Vector3.rotation_matrix_y(rotation.y).dot(rotation_matrix)
        rotation_matrix = Vector3.rotation_matrix_z(rotation.z).dot(rotation_matrix)

        self.array_representation = rotation_matrix.dot(self.array_representation)

        return self

    def convert_to_radian(self):
        self.array_representation = [math.radians(value) for value in self.array_representation]
        return self

    @staticmethod
    def resolve_relative_position(origin, rotation, point):
        """
        Calculates the relative X and Y position on a given plane for a point
        :type origin Vector3
        :param origin: Point supporting the plane
        :type rotation Vector3
        :param rotation: Rotation of the normal, relative to the Z-Axis [0, 0, 1]
        :type point Vector3
        :param point: The point to map onto the plane
        :return: The X and Y position as an array[2] or None if the point was not on the plane
        """

        # move to origin
        normalized_point = point - origin
        x_component = Vector3(1, 0, 0).rotate(rotation)
        y_component = Vector3(0, 1, 0).rotate(rotation)
        z_component = Vector3(0, 0, 1).rotate(rotation)

        mapped_intersection = numpy.linalg.solve(
            [
                [x_component.x, y_component.x, z_component.x],
                [x_component.y, y_component.y, z_component.y],
                [x_component.z, y_component.z, z_component.z]
            ],
            normalized_point.array_representation
        )

        # if the Z component is bigger than a reasonable numerical error (a 1000th of the point's norm)
        # then the point wasn't on the plane
        if mapped_intersection[2] > (numpy.linalg.norm(normalized_point.array_representation) / 1000):
            return None

        return [mapped_intersection[0], mapped_intersection[1], 0]

        # todo: check if more efficient version is equivalent (should be)

        # mapped_intersection = numpy.linalg.solve(
        #     [
        #         [x_component.x, y_component.x],
        #         [x_component.y, y_component.y]
        #     ],
        #     intersection[:2]
        # )

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


def intersect(ray_origin, ray_direction, plane_origin, plane_normal_vector, minimum=0, maximum=None):
    """
    Intersects a line and a plane. Restrictions on the range of the intersection can be applied.
    :param ray_origin:
    :param ray_direction:
    :param plane_origin:
    :param plane_normal_vector:
    :param minimum: The minimum multiplier for the ray_direction, defaults to 0. Use None to disable.
    :param maximum: The maximum multiplier for the ray_direction, defaults to None. Use None to disable.
    :return: The intersection as vector[3] or None if no intersection exists, given the minimum/maximum restrictions.
    """

    # https://en.wikipedia.org/wiki/Line%E2%80%93plane_intersection#Algebraic_form
    distance_factor = ((plane_origin - ray_origin).dot(plane_normal_vector)) \
                      / ray_direction.dot(plane_normal_vector)

    if minimum is not None and distance_factor < minimum:
        return None

    if maximum is not None and distance_factor > maximum:
        return None

    return ray_origin + ray_direction * distance_factor
