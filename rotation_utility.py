import copy
import math
import numpy as np

__author__ = 'neo post modern'

def rotate_vector_3d(vector, rotation):
    rotated_vector = copy.copy(vector)
    rotated_vector = rotation_matrix_x(rotation[0]).dot(rotated_vector)
    rotated_vector = rotation_matrix_y(rotation[1]).dot(rotated_vector)
    rotated_vector = rotation_matrix_z(rotation[2]).dot(rotated_vector)
    return rotated_vector

def rotation_matrix_x(angle):
    return np.array([[1, 0, 0],
                     [0, math.cos(angle), -1 * math.sin(angle)],
                     [0, math.sin(angle), math.cos(angle)]])
def rotation_matrix_y(angle):
    return np.array([[math.cos(angle), 0, math.sin(angle)],
                     [0, 1, 0],
                     [-1 * math.sin(angle), 0, math.cos(angle)]])
def rotation_matrix_z(angle):
    return np.array([[math.cos(angle), -1 * math.sin(angle), 0],
                     [math.sin(angle), math.cos(angle), 0],
                     [0, 0, 1]])
