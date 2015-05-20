#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'neopostmodern'

import math

import numpy as numpy

from f3d.util.vectors import Vector3, intersect

from f3d.util import json_inheritor

from f3d.settings import Settings


class Camera(json_inheritor.JsonInheritor):
    def __init__(self, specification):
        super().__init__(specification)

        self.position = Vector3.from_dict(self.position)

        if hasattr(self, 'rotation'):
            self.rotation = Vector3.from_dict(self.rotation)
        else:
            self.rotation = Vector3(0, 0, 0)

        # todo: implement focal length feature
        # self.angleOfView = math.radians(angle_of_view / 2)
        self.angle_of_view = math.radians(40)

    def project_surface(self, surface):
        def intersection_point(x_factor, y_factor):
            # todo: cache?
            ray_direction = Vector3(
                math.sin(self.angle_of_view),
                math.sin(self.angle_of_view) * Settings.image.size.y / Settings.image.size.x,
                1
            )

            ray_direction.x *= x_factor
            ray_direction.y *= y_factor

            ray_direction = ray_direction.rotate(self.rotation)

            intersection = intersect(
                self.position.array_representation,
                ray_direction,
                surface.position,
                surface.normal_vector
            )

            if intersection is None:
                return None

            return intersection

        # lower left, lower right, upper left, upper right
        factors = [(-1, -1),
                   ( 1, -1),
                   (-1,  1),
                   ( 1,  1)]

        return [intersection_point(x_factor, y_factor) for x_factor, y_factor in factors]

    def position_at_time(self, time):
        return self.position