#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'neopostmodern'

import abc
import re as regex

import numpy as numpy
import scipy.interpolate.interpolate as interpolate

from f3d.util.ranged_function import RangedFunction

NUMBER_REGEX = regex.compile('-?\d+(?:\.\d+)?')

class BaseAnimation(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get_for_time(self, time, frame):
        """Generate the frame at specific frame index"""
        return


class Interpolation(BaseAnimation):
    def __init__(self, animation, named_frames):
        timestamps = [keyframe['time'] for keyframe in animation['keyframes']]
        time_range = (timestamps[0], timestamps[-1])

        self.interpolations = {}

        # uses ANY frame, since towards the searched elements/attributes they must be identical
        base_frame_identifier, base_frame = next(iter(named_frames.items()))

        for identifier in animation['identifiers']:
            element_name = identifier['element']
            base_element = base_frame.find(".//*[@id='%s']" % element_name)

            self.interpolations[element_name] = {}

            for property_name in identifier['properties']:
                property_value = base_element.get(property_name)

                property_count = len(NUMBER_REGEX.findall(property_value))

                interpolation_values = numpy.zeros((property_count, len(animation['keyframes'])))

                for keyframe_index, keyframe in enumerate(animation['keyframes']):
                    frame = named_frames[keyframe['frame']]
                    # the leading . (dot) avoids some funky "SyntaxError: cannot use absolute path on element"
                    element = frame.find(".//*[@id='%s']" % element_name)

                    property_value = element.get(property_name)

                    for match_index, match in enumerate(NUMBER_REGEX.finditer(property_value)):
                        interpolation_values[match_index][keyframe_index] = float(match.group())

                interpolations = [
                    RangedFunction(
                        interpolate.interp1d(timestamps, series),
                        time_range
                    )
                    for series in interpolation_values
                ]

                self.interpolations[element_name][property_name] = interpolations

    @staticmethod
    def apply_interpolation(frame, element_name, property_name, values):
        element = frame.find(".//*[@id='%s']" % element_name)
        property_value = element.get(property_name)
        property_value = NUMBER_REGEX.sub("%f", property_value)
        element.set(property_name, property_value % tuple(values))

    def get_for_time(self, time, frame):
        for element_name, interpolation in self.interpolations.items():
            for property_name, functions in interpolation.items():
                interpolated_values = [function(time) for function in functions]
                self.apply_interpolation(frame, element_name, property_name, interpolated_values)

        return frame

