"""
UNUSED LEGACY CODE

Will be recycled soon.
"""


import copy
import uuid

import numpy as np
from lxml import etree


__author__ = 'neo post modern'




class Surface:
    def __init__(self, origin, size, svg_element, rotation=[0, 0, 0], prefix="", opacity=1.0):
        self.origin = origin
        self.size = size
        self.rotation = rotation
        self.opacity = opacity

        self.normalVector = np.array([0, 0, 1])
        self.normalVector = rotation.rotate_vector_3d(self.normalVector, rotation)

        self.svgElement = svg_element
        self.identifier = prefix + str(uuid.uuid4())

    def get_svg_transformed_to(self, mapping):
        svg_element = copy.deepcopy(self.svgElement)

        svg_element.set("style", "transform-origin: 280px 50px 0px; transform: matrix3d(%s);" %
                        ", ".join(["%.6f" % value for value in mapping.flatten()]))

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

    def get_svg_transformed_to(self, mapping):
        svg_texture = super().get_svg_transformed_to(mapping)

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

    def get_svg_transformed_to(self, mapping):
        svg_mask = super().get_svg_transformed_to(mapping)

        mask_wrapper = etree.Element("mask")
        mask_wrapper.set("id", self.identifier)
        mask_wrapper.append(svg_mask)
        return mask_wrapper

