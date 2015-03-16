import numpy as np

__author__ = 'neo post modern'


def into_svg(point):
    return [point[0] + 960,
            point[1] + 540]


def from_svg(point):
    return [point[0] - 960,
            point[1] - 540]

#
# def generate_svg_transformation_matrix(target_area):
#     # reference_points = np.array([0, 0,
#     #                              1920, 0,
#     #                              0, 1080])
#     reference_points = np.array([-960, -540,
#                                  960, -540,
#                                  -960, 540])
#     target_matrix = np.array([
#         [target_area[0][0], 0, target_area[0][1], 0, 1, 0],
#         [0, target_area[0][0], 0, target_area[0][1], 0, 1],
#         [target_area[1][0], 0, target_area[1][1], 0, 1, 0],
#         [0, target_area[1][0], 0, target_area[1][1], 0, 1],
#         [target_area[2][0], 0, target_area[2][1], 0, 1, 0],
#         [0, target_area[2][0], 0, target_area[2][1], 0, 1]
#     ])
#
#     return np.linalg.solve(target_matrix, reference_points)


def generate_svg_transformation_matrix(target_area):
    reference_points = np.array([0, 0,
                                 1920, 0,
                                 0, 1080])

    lower_left = into_svg(target_area[0])
    lower_right = into_svg(target_area[1])
    upper_left = into_svg(target_area[2])

    target_matrix = np.array([
        [lower_left[0], 0, lower_left[1], 0, 1, 0],
        [0, lower_left[0], 0, lower_left[1], 0, 1],
        [lower_right[0], 0, lower_right[1], 0, 1, 0],
        [0, lower_right[0], 0, lower_right[1], 0, 1],
        [upper_left[0], 0, upper_left[1], 0, 1, 0],
        [0, upper_left[0], 0, upper_left[1], 0, 1]
    ])

    return np.linalg.solve(target_matrix, reference_points)