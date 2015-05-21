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
            canvas_normal = Vector3(0, 0, 1).rotate(self.rotation)
            canvas_origin = self.position + canvas_normal.array_representation * 3000  # todo: legitimate values please

            surface_corner = Vector3(Settings.image.size.x * x_factor, Settings.image.size.y * y_factor, 0)\
                .rotate(surface.rotation)\
                + surface.position

            ray_direction = surface_corner - self.position

            intersection = intersect(
                self.position.array_representation,
                ray_direction,
                canvas_origin,
                canvas_normal
            )

            if intersection is None:
                return None

            return intersection

        # lower left, lower right, upper left, upper right
        factors = [(0, 0),
                   (1, 0),
                   (0, 1),
                   (1, 1)]

        return [intersection_point(x_factor, y_factor) for x_factor, y_factor in factors]

    def position_at_time(self, time):
        return self.position