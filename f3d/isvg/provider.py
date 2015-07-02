__author__ = 'neopostmodern'

import abc
import os
from copy import deepcopy
from warnings import warn

from lxml import etree

import f3d.isvg.animations as animation_tools
import f3d.util.vectors as vectors
from f3d.settings import Settings


class BaseSvgProvider(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, surface):
        # todo: load position, rotation as vectors.Position
        basic_property_names = ['position', 'rotation', 'meta', 'identifier']
        basic_properties = filter(lambda i: i[0] in basic_property_names, surface.items)
        self.__dict__.update(basic_properties)

        if not hasattr(self, 'rotation'):
            self.rotation = vectors.Vector3(0, 0, 0)

    @abc.abstractmethod
    def get_for_time(self, time):
        """Generate the frame at specific frame index"""
        return


class StaticSvgProvider(BaseSvgProvider):
    def __init__(self, surface):
        frame_description = surface['frame']

        # todo: make base path modifiable (not only CWD)
        file_path = os.path.join(os.getcwd(), Settings.paths['svg_resources'], frame_description['path'])

        try:
            with open(file_path, 'r') as svg_file:
                svg_tree = etree.parse(svg_file)
                # todo: unset IDs - collisions! or are they necessary somewhere?
                self.frame = svg_tree.find("//*[@id='%s']" % frame_description['identifier'])
        except FileNotFoundError as fileNotFoundException:
            raise Exception("[ERROR] SVG Provider: File '%s' not found!" % file_path) from fileNotFoundException

    def get_for_time(self, time):
        return deepcopy(self.frame)


class AnimatedSvgProvider(BaseSvgProvider):
    def __init__(self, surface):
        self.named_frames = {}

        frames = surface['frames']
        animations = surface['animations']

        for frame in frames:
            # todo: make base path modifiable (not only CWD)
            file_path = os.path.join(os.getcwd(), Settings.paths['svg_resources'], frame['path'])

            try:
                with open(file_path, 'r') as svg_file:
                    svg_tree = etree.parse(svg_file)
                    element = svg_tree.find("//*[@id='%s']" % frame['identifier'])

                    self.named_frames[frame['name']] = element
            except FileNotFoundError:
                warn("[ERROR] SVG Provider: File '%s' not found!" % file_path)

        base_frame_name = surface.get('baseFrame', frames[0]['identifier'])
        self.base_frame = self.named_frames[base_frame_name]

        self.animations = []

        for animation in animations:
            if animation['type'] == "interpolation":
                self.animations.append(animation_tools.Interpolation(animation, self.named_frames))

            else:
                warn("[ERROR] SVG Provider: Unsupported animation '%s'." % animation['type'])

    def get_for_time(self, time):
        frame = deepcopy(self.base_frame)

        for animation in self.animations:
            frame = animation.get_for_time(time, frame)

        return frame
