#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math
import numpy

from f3d.util.vectors import Vector3, intersect
from f3d.tools_3d.object_3d import Object3D
from f3d.settings import Settings

__author__ = 'neopostmodern'


MAPPING_GRID_SIZE = 5  # consider: something more dynamic maybe?


class Camera(Object3D):
    def __init__(self, specification):
        super().__init__(specification)

        self.focal_length = int(specification.get('focal_length', 50))

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

        canvas_normal = Vector3(0, 0, 1).rotate(camera_rotation)

        # the canvas is moved back as necessary by the 'focal length' by the `canvas_distance`
        canvas_distance = Settings.image.size.x / math.tan(self.angle_of_view / 2)
        # the canvas origin will be located in the 'upper right' corner,
        # resulting in lower left corner of the flipped canvas, acting as (0, 0)
        canvas_origin = camera_position + Vector3(
            0.5 * Settings.image.size.x,
            0.5 * Settings.image.size.y,
            0
        ).rotate(camera_rotation)

        canvas_origin -= canvas_normal.array_representation * canvas_distance

        def intersection_point_by_origin(origin_point):
            surface_corner = Vector3(origin_point).rotate(surface_rotation) + surface_position

            ray_direction = camera_position - surface_corner

            intersection = intersect(
                camera_position.array_representation,
                ray_direction.array_representation,
                canvas_origin.array_representation,
                canvas_normal.array_representation,
                minimum=0  # intersection must be _behind_ camera, i.e. on the canvas
            )

            if intersection is None:
                return None

            return Vector3.resolve_relative_position(
                canvas_origin,
                camera_rotation,
                Vector3(intersection),
                inverted=True
            )

        def intersection_point_by_target(target_point):
            inverted_target_point = [-1 * component for component in target_point]
            canvas_corner = Vector3(inverted_target_point).rotate(camera_rotation) + canvas_origin
            ray_direction = camera_position - canvas_corner

            intersection = intersect(
                camera_position.array_representation,
                ray_direction.array_representation,
                surface_position.array_representation,
                Vector3(0, 0, 1).rotate(surface_rotation).array_representation,
                minimum=0  # intersection must be _in front of_  the camera
            )

            if intersection is None:
                return None

            return Vector3.resolve_relative_position(
                surface_position,
                surface_rotation,
                Vector3(intersection)
            )

        factors = []
        for x in numpy.linspace(0, 1, num=MAPPING_GRID_SIZE, endpoint=True):
            for y in numpy.linspace(0, 1, num=MAPPING_GRID_SIZE, endpoint=True):
                factors.append((x, y))

        origin_positions = [[surface_size.x * x_factor, surface_size.y * y_factor, 0] for x_factor, y_factor in factors]

        possible_intersection_points = [
            (point, intersection_point_by_origin(point))
            for point in origin_positions
        ]

        target_positions = [[Settings.image.size.x * x_factor, Settings.image.size.y * y_factor, 0]
                            for x_factor, y_factor in factors]
        possible_intersection_points.extend([
            (intersection_point_by_target(point), point)
            for point in target_positions
        ])

        # drop all failed projections first
        possible_intersection_points = [
            points for points in possible_intersection_points
            if points[0] is not None and points[1] is not None
        ]

        # sort by closeness to origin to reduce numerical errors
        possible_intersection_points.sort(
            key=lambda points: numpy.linalg.norm(points[0]) + numpy.linalg.norm(points[1])
        )

        intersection_points = []

        for origin, target in possible_intersection_points:

            # filter aligned points because they (potentially) don't carry information
            # todo: find more efficient means to filter redundant points
            unaligned = True
            for index_a, (_, point_a) in enumerate(intersection_points):
                for index_b, (_, point_b) in enumerate(intersection_points):
                    if index_a != index_b:
                        # check if aligned, via empty triangle surface http://stackoverflow.com/a/3813755/2525299
                        if abs(target[0] * (point_a[1] - point_b[1])
                                + point_a[0] * (point_b[1] - target[1])
                                + point_b[0] * (target[1] - point_a[1])) < 1e-5:
                            unaligned = False
            if unaligned:
                intersection_points.append((origin, target))

            if len(intersection_points) >= 4:
                break

        if len(intersection_points) >= 4:
            return intersection_points

        return None

