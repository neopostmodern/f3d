import copy
import math
import uuid
import numpy as np

from lxml import etree

import rotation_utility
import svg_utility
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
    def __init__(self, origin, size, svg_element, rotation=[0, 0, 0], prefix="", opacity=1.0):
        self.origin = origin
        self.size = size
        self.rotation = rotation
        self.opacity = opacity

        self.normalVector = np.array([0, 0, 1])
        self.normalVector = rotation_utility.rotate_vector_3d(self.normalVector, rotation)

        self.svgElement = svg_element
        self.identifier = prefix + str(uuid.uuid4())

    def get_transformed_to(self, mapping):
        svg_element = copy.deepcopy(self.svgElement)
        svg_element.set("transform", "matrix(%f %f %f %f %f %f)"
                            % tuple(svg_utility.generate_svg_transformation_matrix(mapping)))
        svg_element.set("id", self.identifier)
        svg_element.set("opacity", str(self.opacity))
        return svg_element


class TexturedSurface(Surface):
    def __init__(self, texture_path, origin, size, rotation=[0, 0, 0], opacity=1.0, mask_identifier=None):
        with open(texture_path, 'r') as svg_file:
            svg_tree = etree.parse(svg_file)
            texture = svg_tree.find("//*[@id='texture']")

            if texture is None:
                raise ValueError("SVG file without texture!")

            Surface.__init__(self, origin, size, texture, rotation, opacity=opacity, prefix="textured-")

            self.maskIdentifier = mask_identifier

    def get_transformed_to(self, mapping):
        svg_texture = super().get_transformed_to(mapping)

        if self.maskIdentifier is not None:
            mask_wrapper = etree.Element("g")
            mask_wrapper.set("mask", "url(#%s)" % self.maskIdentifier)
            mask_wrapper.append(svg_texture)
            return mask_wrapper
        else:
            return svg_texture


class AlphaMask(Surface):
    def __init__(self, mask_path, origin, size, rotation=[0, 0, 0], opacity=1.0):
        with open(mask_path, 'r') as svg_file:
            svg_tree = etree.parse(svg_file)
            texture = svg_tree.find("//*[@id='mask']")

            if texture is None:
                raise ValueError("SVG file without mask!")

            Surface.__init__(self, origin, size, texture, rotation, opacity=opacity, prefix="mask-")

    def get_transformed_to(self, mapping):
        svg_mask = super().get_transformed_to(mapping)

        mask_wrapper = etree.Element("mask")
        mask_wrapper.set("id", self.identifier)
        mask_wrapper.append(svg_mask)
        return mask_wrapper

