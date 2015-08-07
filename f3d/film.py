#!/usr/bin/env python
# -*- coding: utf-8 -*-
from f3d.file_management import FileManagement
from f3d.surface import Surface

__author__ = 'neopostmodern'

from warnings import warn
from copy import deepcopy
from lxml import etree
import json
import numpy as numpy

from f3d.isvg import provider
from f3d.settings import Settings
from f3d.camera import Camera
import f3d.tools_3d.svg_3d as SvgUtility

CONTAINER_SVG = """<?xml version="1.0" standalone="no"?>
<svg
   xmlns:dc="http://purl.org/dc/elements/1.1/"
   xmlns:cc="http://creativecommons.org/ns#"
   xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
   xmlns:svg="http://www.w3.org/2000/svg"
   xmlns="http://www.w3.org/2000/svg"
   width="1920"
   height="1080"
   viewBox="0 0 1920 1080"
   version="1.1">
  <defs id="defs">
  </defs>
  <metadata
     id="metadata7">
    <rdf:RDF>
      <cc:Work
         rdf:about="">
        <dc:format>image/svg+xml</dc:format>
        <dc:type
           rdf:resource="http://purl.org/dc/dcmitype/StillImage" />
        <dc:title />
      </cc:Work>
    </rdf:RDF>
  </metadata>
  <g
     id="container"
     style="display:inline"></g>
</svg>
"""

TIME_SVG = """
<text   id="time-indicator"
        y="100"
        x="-150"
        style="font-size:29.15789223px;font-family:'Courier New';fill:#000000;fill-opacity:1;stroke:none;"
        xml:space="preserve">
    <tspan>
        %s
    </tspan>
</text>
"""


class FakeFilm:
    def __init__(self, setting_path):
        try:
            with open(setting_path, mode='r') as setting_json:
                try:
                    setting = json.load(setting_json) #, object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))
                except ValueError:
                    raise Exception("[FakeFilm] Parsing of setting '%s' failed." % setting_path)
        except FileNotFoundError as fileError:
            raise Exception("[FakeFilm] Settings file '%s' not found." % setting_path) from fileError

        Settings.set(setting['settings'])
        FileManagement.initialize()  # hack: depends on settings being loaded!

        self.camera = Camera(setting['camera'])
        # todo: image object? (properties moved into common settings...)
        # self.image = Image(setting['image'])

        # for property_name in setting:
        #     setattr(self, property_name, setting[property_name])

        self.surfaces = self.load_resources(setting['surfaces'])

        self.container_svg = etree.fromstring(CONTAINER_SVG)

    @staticmethod
    def load_resources(surfaces):
        def load_surface(surface):
            svg_provider = {
                "animated": provider.AnimatedSvgProvider,
                "static": provider.StaticSvgProvider
            }.get(surface['type'], None)

            if svg_provider is None:
                warn("[ERROR] FakeFilm: Unsupported surface type '%s'." % surface['type'])
                return None  # todo: appropriate error handling?

            return Surface(surface, svg_provider(surface))

        return [load_surface(surface) for surface in surfaces]

    def render(self, time):
        container = deepcopy(self.container_svg)
        surface_container = container.find(".//*[@id='container']")
        alpha_container = container.find(".//*[@id='defs']")

        for surface in self.surfaces:
            surface = surface.get_for_time(time, self.camera)

            #todo: handle alpha channels

            surface_container.append(surface)

        if Settings.add_timestamp:
            minutes, seconds = divmod(time, 60)
            surface_container.append(etree.fromstring(TIME_SVG % ("00:%02.0f:%07.4f" % (minutes, seconds))))

        return container


class NaiveSurface(Surface):
    # hack: redefined parameters! mapping -> projection
    def get_svg_transformed_to(self, projection, svg_element):
        lower_left = SvgUtility.into_svg(projection[0])
        lower_right = SvgUtility.into_svg(projection[1])
        upper_left = SvgUtility.into_svg(projection[2])

        old_coordinates = [
            lower_left[0], lower_left[1],
            lower_right[0], lower_right[1],
            upper_left[0], upper_left[1]
        ]

        # look at this: https://developer.mozilla.org/en-US/docs/Web/SVG/Attribute/transform
        target_matrix = numpy.array([
            [0, 0, 0, 0, 1, 0],
            [0, 0, 0, 0, 0, 1],
            [Settings.image.size.x, 0, 0, 0, 1, 0],
            [0, Settings.image.size.x, 0, 0, 0, 1],
            [0, 0, Settings.image.size.y, 0, 1, 0],
            [0, 0, 0, Settings.image.size.y, 0, 1]
        ])

        transform_matrix = numpy.linalg.solve(target_matrix, old_coordinates)

        svg_element.set("transform", "matrix(%f %f %f %f %f %f)" % tuple(transform_matrix))
        return svg_element

    def get_for_time(self, time, camera):
        svg = self.svg_provider.get_for_time(time)
        projection = camera.project_surface(self)

        if projection is not None:
            return self.get_svg_transformed_to(projection, svg)

        return svg
