#!/usr/bin/env python
#-*- coding: utf-8 -*-
from copy import deepcopy

from f3d.settings import Settings
from f3d.tools_3d.object_3d import Object3D
from f3d.tools_3d import svg_3d as SvgUtility
from f3d.util.animated_vectors import StaticVector
from f3d.util.vectors import Vector2

__author__ = 'neopostmodern'


class Surface(Object3D):
    def __init__(self, specification, svg_provider):
        super().__init__(specification)

        self.svg_provider = svg_provider

        self.meta = specification['meta']

        target_size = deepcopy(Settings.image.size)
        source_size = deepcopy(Settings.image.size)

        if 'size' in specification:
            if 'width' in specification['size']:
                source_size = target_size = Vector2.from_dict(specification['size'], ['width', 'height'])
            else:
                if 'target' in specification['size']:
                    target_size = Vector2.from_dict(specification['size']['target'], ['width', 'height'])

                if 'source' in specification['size']:
                    source_size = Vector2.from_dict(specification['size']['source'], ['width', 'height'])

                if 'scale' in specification['size']:
                    target_size.array_representation = source_size.array_representation * specification['size']['scale']

        self.source_size = source_size
        self.target_size = StaticVector(target_size)

    def get_svg_transformed_to(self, mapping, svg_element):
        # todo: review!
        transformation = ", ".join(["%.6f" % value for value in mapping.flatten()])
        transformations = " ".join(["%stransform: matrix3d(%s);" % (prefix, transformation) for prefix in ["-webkit-", ""]])

        svg_element.set("style", transformations)  # consider: `transform-origin: 280px 50px 0px;`

        # svg_element.set("id", self.identifier)
        # svg_element.set("opacity", str(self.opacity))
        return svg_element

    def get_for_time(self, time, camera):
        svg = self.svg_provider.get_for_time(time)
        projection = camera.project_surface(self, time)

        if all([p is not None for p in projection]):
            mapping = SvgUtility.generate_css3_3d_transformation_matrix(self.source_size, projection)
            return self.get_svg_transformed_to(mapping, svg)
        else:
            # todo: proper error handling if projection failed
            print("Couldn't project surface '%s'" % self.meta['name'])

        return svg
