import subprocess
import os

__author__ = 'neo post modern'

import view
import numpy as np

PATH = os.path.dirname(__file__)
IMAGE_SIZE = np.array([1920, 1080])

camera = view.Camera(np.array([0, 0, 1000]), 55, IMAGE_SIZE)
surface = view.Surface(np.array([-960, -540, 2000]), IMAGE_SIZE)

projection_points = camera.project_surface(surface)

lower_left_projected = projection_points[0][:2]
lower_right_projected = projection_points[0][:2]
upper_left_projected = projection_points[0][:2]
upper_right_projected = projection_points[0][:2]

print(projection_points)
print(camera.generate_svg_transformation_matrix(projection_points))