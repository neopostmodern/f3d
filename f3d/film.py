#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'neopostmodern'

from warnings import warn
from copy import deepcopy
from lxml import etree
import json

from f3d.isvg import provider
from f3d.settings import Settings
from f3d.camera import Camera
from f3d.util.vectors import Vector3

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


class FakeFilm():
    def __init__(self, setting_path):
        with open(setting_path, mode='r') as setting_json:
            try:
                setting = json.load(setting_json) #, object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))
            except ValueError:
                raise Exception("[FakeFilm] Parsing of setting '%s' failed." % setting_path)

        Settings.set(setting['settings'])

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
            svg_provider = None
            if surface['type'] == "animated":
                svg_provider = provider.AnimatedSvgProvider(surface)
            else:
                warn("[ERROR] FakeFilm: Unsupported surface type '%s'." % surface['type'])

            return Surface(surface, svg_provider)

        return [load_surface(surface) for surface in surfaces]

    def render(self, time):
        container = deepcopy(self.container_svg)
        surface_container = container.find(".//*[@id='container']")
        alpha_container = container.find(".//*[@id='defs']")

        for surface in self.surfaces:
            surface = surface.get_for_time(time, self.camera)

            #todo: handle alpha channels

            surface_container.append(surface)

        return container


class Surface():
    def __init__(self, specification, svg_provider):
        self.svg_provider = svg_provider
        self.position = Vector3.from_dict(specification['position'])

        if 'rotation' in specification:
            self.rotation = Vector3.from_dict(specification['rotation'])
        else:
            self.rotation = Vector3(0, 0, 0)

        self.normal_vector = Vector3(0, 0, 1).rotate(self.rotation)

    def get_for_time(self, time, camera):
        svg = self.svg_provider.get_for_time(time)
        projection = camera.project_surface(self)

        if projection is not None:
            print(projection)
            # mapping = svg_utility.generate_css3_3d_transformation_matrix(projection)
            # svg_container.append(surface.get_svg_transformed_to(mapping))

        return svg
