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


def generate_svg_transformation_matrix(target_area, full_3d=False):
    if full_3d:
        reference_points = np.array([0, 0, 0,
                                     1920, 0, 0,
                                     0, 1080, 0,
                                     1920, 1080, 0])

        target_matrix = np.zeros((12, 12))

        for reference_point_index in range(4):
            for axis_index in range(3):
                for i in range(4):
                    target_matrix[reference_point_index * 3 + axis_index][axis_index * 3 + i] = \
                        1 if (i is 3) else target_area[reference_point_index][i]

        print(target_matrix)
    # if full_3d:
    #     reference_points = np.array(target_area).reshape((12,))
    #     print(reference_points)
    #
    #     corners = np.array([[0, 0, 0],
    #                         [1920, 0, 0],
    #                         [0, 1080, 0],
    #                         [1920, 1080, 0]])
    #
    #     target_matrix = np.zeros((12, 12))
    #
    #     for reference_point_index in range(4):
    #         for axis_index in range(3):
    #             for i in range(4):
    #                 target_matrix[reference_point_index * 3 + axis_index][axis_index * 3 + i] = \
    #                     1 if (i is 3) else corners[reference_point_index][i]
    #
    #     print(target_matrix)

    else:
        reference_points = np.array([0, 0,
                                     1920, 0,
                                     0, 1080,
                                     1920, 1080])

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

        reference_points = reference_points[:6]

    return np.linalg.solve(target_matrix, reference_points)