#!/usr/bin/env python
#-*- coding: utf-8 -*-

import abc

import scipy.interpolate.interpolate as interpolate

from f3d.util.ranged_function import RangedFunction
from f3d.util.vectors import Vector3

__author__ = 'neopostmodern'


class ConstantFunction:
    def __init__(self, value):
        self.value = value

    def __call__(self, *args, **kwargs):
        return self.value


class BaseAnimatedVector(object):
    __metaclass__ = abc.ABCMeta

    def __call__(self, *args, **kwargs):
        if len(args) != 1 or len(kwargs) > 0:
            raise Exception("Call 'BaseAnimatedVector' with exactly one parameter: time")
        time = args[0]

        return self.get_for_time(time)

    @abc.abstractmethod
    def get_for_time(self, time):
        """
        Returns the vector at a given time.
        :param time: Time in seconds
        :type time float
        :return: Vector3
        """
        return


class StaticVector(BaseAnimatedVector):
    """
    Naive wrapper for a Vector3 object, to comply with AnimatedVector3.
    Always returns the vector it's instantiated with.
    """
    def __init__(self, vector):
        self.vector = vector

    def get_for_time(self, time):
        return self.vector


class AnimatedVector(BaseAnimatedVector):
    def __init__(self, animation, identifier=None, default=None, constructor=None):
        if constructor is not None:
            self.constructor = constructor
        else:
            self.constructor = lambda x: x

        # consider: filtering frames based on if the property is present
        # would make animations of properties cross across other keyframes if they aren't mentioned
        # not yet sure how to handle conflict with automatic identifier pick-up and/or 0-time-frame insertion

        first_frame = animation[0]

        if identifier is None:
            if len(first_frame.keys()) < 2:
                raise ValueError("Missing value: No identifier set.")
            identifier = next(key for key in first_frame.keys() if key is not 'time')

        if default is None:
            if identifier not in first_frame:
                raise ValueError("Missing value: No default or value '%s' found for animation." % identifier)
            default = self.constructor(first_frame[identifier])  # possibly redundant but important

        unique_values = 0
        if float(first_frame['time']) != 0.0:
            animation.insert(0, {
                'time': 0.0
            })
            unique_values += 1

        timestamps = []
        values = []
        for frame in animation:
            timestamps.append(float(frame['time']))

            if identifier in frame:
                value = default = self.constructor(frame[identifier])
                unique_values += 1
            else:
                # consider: only using 'default' for first/last frame?
                value = default

            values.append(value)

        if unique_values < 2:
            self.animation_functions = [ConstantFunction(value) for value in values[0].array_representation]
        else:
            # todo: this is only linear interpolation. offer options for splines?
            self.animation_functions = [RangedFunction(
                interpolate.interp1d(
                    timestamps,
                    [value.array_representation[index] for value in values],
                    assume_sorted=True
                ),
                [timestamps[0], timestamps[-1]]
            ) for index in range(3)]

    def get_for_time(self, time):
        return self.constructor([animation_function(time) for animation_function in self.animation_functions])
