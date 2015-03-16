import math
import uuid
import numpy as np
import rotation_utility
import vector_utility

__author__ = 'neo post modern'

class Camera:
    def __init__(self, position, angle_of_view, image_size, rotation=[0, 0, 0]):
        self.position = position
        self.rotation = rotation
        self.angleOfView = math.radians(angle_of_view / 2)
        self.imageSize = image_size

    def project_surface(self, surface):
        intersection_points = []

        # lower left, lower right, upper left, upper right
        factors = [[-1, -1],
                   [1, -1],
                   [-1, 1],
                   [1, 1]]

        for factor_pair in factors:
            ray_direction = np.array([
                math.sin(self.angleOfView),
                math.sin(self.angleOfView) * self.imageSize[1] / self.imageSize[0],
                1
            ])

            ray_direction[:2] = ray_direction[:2] * factor_pair

            ray_direction = rotation_utility.rotate_vector_3d(ray_direction, self.rotation)

            intersection_points.append(
                vector_utility.intersect(self.position, ray_direction, surface.origin, surface.normalVector)
            )

        return intersection_points




class Surface:
    def __init__(self, origin, size, rotation=[0, 0, 0]):
        self.origin = origin
        self.size = size
        self.rotation = rotation

        self.normalVector = np.array([0, 0, 1])

        self.normalVector = rotation_utility.rotate_vector_3d(self.normalVector, rotation)

        self.identifier = uuid.uuid4()

