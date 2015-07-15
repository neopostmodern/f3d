#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'neopostmodern'

import math

from f3d.util.vectors import Vector3, intersect
from f3d.util.animated_vectors import StaticVector3, AnimatedVector3
from f3d.util import json_inheritor
from f3d.settings import Settings


class Camera(json_inheritor.JsonInheritor):
    def __init__(self, specification):
        super().__init__(specification)

        position = Vector3.from_dict(self.position)

        if hasattr(self, 'rotation'):
            rotation = Vector3.from_dict(self.rotation).convert_to_radian()
        else:
            rotation = Vector3()

        if getattr(self, 'animated', False) is True:
            self.position = AnimatedVector3(
                self.animation,
                identifier='position',
                constructor=Vector3,
                default=position
            )
            self.rotation = AnimatedVector3(
                self.animation,
                identifier='rotation',
                constructor=lambda rotation: Vector3(rotation).convert_to_radian(),
                default=rotation
            )
        else:
            self.position = StaticVector3(position)
            self.rotation = StaticVector3(rotation)

        if not hasattr(self, 'focal_length'):
            self.focal_length = 50

        # 35 _roughly_ simulates a 35mm format (which is 3:2), the usual reference for focal lengths
        # assuming that most projects will be 16:9 though, it should be a good estimate
        self.angle_of_view = 2 * math.atan(35 / (2 * self.focal_length))

    def project_surface(self, surface, time):
        """
        Calculate the projection of a surface to the screen.
        :type surface: f3d.surface.Surface
        :param surface: The surface to project. No time transformations will be applied on it.
        :type time: float
        :param time: The time (not frame index) of the projection. Modifies camera only, surface has to be time-correct.
        :return: An array[4] of the surface's corners as screen positions [x, y] in the following order:
        lower left, lower right, upper left, upper right
        """

        position = self.position(time)
        rotation = self.rotation(time)

        # the camera position will actually be the _canvas_ position.
        # the camera is moved back as necessary by the 'focal length', further called `camera_distance`
        camera_distance = surface.size.x / math.tan(self.angle_of_view / 2)

        canvas_normal = Vector3(0, 0, 1).rotate(rotation)
        canvas_origin = position + Vector3(
            -0.5 * Settings.image.size.x,
            -0.5 * Settings.image.size.y,
            0
        ).rotate(rotation)

        adjusted_camera_position = position - canvas_normal.array_representation * camera_distance

        def intersection_point(x_factor, y_factor):
            surface_corner = Vector3(
                surface.size.x * x_factor,
                surface.size.y * y_factor,
                0
            ).rotate(surface.rotation)\
                + surface.position

            ray_direction = surface_corner - adjusted_camera_position

            intersection = intersect(
                adjusted_camera_position.array_representation,
                ray_direction.array_representation,
                canvas_origin.array_representation,
                canvas_normal.array_representation
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
