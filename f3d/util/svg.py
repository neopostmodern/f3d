import numpy as np

__author__ = 'neo post modern'


def into_svg(point):
    return [point[0] + 960,
            point[1] + 540]


def from_svg(point):
    return [point[0] - 960,
            point[1] - 540]


def generate_css3_3d_transformation_matrix(target_area):
    reference_points = np.array([[0, 0],
                                 [1920, 0],
                                 [0, 1080],
                                 [1920, 1080]])

    target_matrix = np.zeros((8, 8))
    reference = np.zeros(8)

    for index, target_point in enumerate(target_area):
        row_index = index * 2
        target_matrix[row_index][0] = target_point[0]
        target_matrix[row_index][1] = target_point[1]
        target_matrix[row_index][2] = 1
        target_matrix[row_index][6] = -1 * target_point[0] * reference_points[index][0]
        target_matrix[row_index][7] = -1 * target_point[1] * reference_points[index][0]

        reference[row_index] = reference_points[index][0]

        target_matrix[row_index + 1][3] = target_point[0]
        target_matrix[row_index + 1][4] = target_point[1]
        target_matrix[row_index + 1][5] = 1
        target_matrix[row_index + 1][6] = -1 * target_point[0] * reference_points[index][1]
        target_matrix[row_index + 1][7] = -1 * target_point[1] * reference_points[index][0]

        reference[row_index + 1] = reference_points[index][0]

    T = np.linalg.solve(target_matrix, reference)

    transformation_matrix = [
        [T[0], T[3], 0, T[6]],
        [T[1], T[4], 0, T[7]],
        [   0,    0, 1,    0],
        [T[2], T[5], 0,    1]
    ]

    return np.array(transformation_matrix)