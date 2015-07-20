#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math

from f3d.util.vectors import Vector3, intersect
from f3d.util.animated_vectors import StaticVector, AnimatedVector
from f3d.tools_3d.object_3d import Object3D
from f3d.settings import Settings

__author__ = 'neopostmodern'


class Camera(Object3D):
    def __init__(self, specification):
        super().__init__(specification)

        # todo: replace with pythonic one-liner
        if 'focal_length' in specification:
            self.focal_length = int(specification['focal_length'])
        else:
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

        camera_position = self.position(time)
        camera_rotation = self.rotation(time)

        surface_rotation = surface.rotation(time)
        surface_position = surface.position(time)
        surface_size = surface.target_size(time)

        # the camera position will actually be the _canvas_ position.
        # the camera is moved back as necessary by the 'focal length', further called `camera_distance`
        camera_distance = Settings.image.size.x / math.tan(self.angle_of_view / 2)

        canvas_normal = Vector3(0, 0, 1).rotate(camera_rotation)
        canvas_origin = camera_position + Vector3(
            -0.5 * Settings.image.size.x,
            -0.5 * Settings.image.size.y,
            0
        ).rotate(camera_rotation)

        adjusted_camera_position = camera_position - canvas_normal.array_representation * camera_distance

        def intersection_point(x_factor, y_factor):
            surface_corner = Vector3(
                surface_size.x * x_factor,
                surface_size.y * y_factor,
                0
            ).rotate(surface_rotation)\
                + surface_position

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
