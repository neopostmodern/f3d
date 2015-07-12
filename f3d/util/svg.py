import numpy as np
from copy import deepcopy
from f3d.settings import Settings

__author__ = 'neo post modern'


def into_svg(point):
    return [point[0] + Settings.image.size.x / 2,
            point[1] + Settings.image.size.y / 2]


def from_svg(point):
    return [point[0] - 960,
            point[1] - 540]


def generate_css3_3d_transformation_matrix(surface, target_area):
    source_points = np.array([[0, 0],
                              [surface.size.x, 0],
                              [0, surface.size.y],
                              [surface.size.x, surface.size.y]])

    matrix = np.zeros((8, 8))
    reference = np.zeros(8)

    # print(target_area)

    for index, target_point_original in enumerate(target_area):
        row_index = index * 2
        target_point = into_svg(target_point_original)
        # source_point = source_point_original

        source_point = source_points[index]
        # print(source_point, target_point)
        
        matrix[row_index][0] = source_point[0]
        matrix[row_index][1] = source_point[1]
        matrix[row_index][2] = 1
        matrix[row_index][6] = -1 * source_point[0] * target_point[0]
        matrix[row_index][7] = -1 * source_point[1] * target_point[0]

        reference[row_index] = target_point[0]

        matrix[row_index + 1][3] = source_point[0]
        matrix[row_index + 1][4] = source_point[1]
        matrix[row_index + 1][5] = 1
        matrix[row_index + 1][6] = -1 * source_point[0] * target_point[1]
        matrix[row_index + 1][7] = -1 * source_point[1] * target_point[1]

        reference[row_index + 1] = target_point[1]

    T = np.linalg.solve(matrix, reference)

    transformation_matrix = [
        [T[0], T[3], 0, T[6]],
        [T[1], T[4], 0, T[7]],
        [   0,    0, 1,    0],
        [T[2], T[5], 0,    1]
    ]

    return np.array(transformation_matrix)
