#!/usr/bin/env python
#-*- coding: utf-8 -*-

import abc

import scipy.interpolate.interpolate as interpolate

from f3d.util.ranged_function import RangedFunction
from f3d.util.vectors import Vector3

__author__ = 'neopostmodern'


class BaseAnimatedVector3(object):
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
        """
        return


class StaticVector3(BaseAnimatedVector3):
    """
    Naive wrapper for a Vector3 object, to comply with AnimatedVector3.
    Always returns the vector it's instantiated with.
    """
    def __init__(self, vector):
        self.vector = vector

    def get_for_time(self, time):
        return self.vector


class AnimatedVector3(BaseAnimatedVector3):
    def __init__(self, animation, identifier=None, default=None, constructor=None):
        if constructor is not None:
            self.constructor = constructor
        else:
            self.constructor = lambda x: x

        first_frame = animation[0]

        if identifier is None:
            if len(first_frame.keys()) < 2:
                raise ValueError("Missing value: No identifier set.")
            identifier = next(key for key in first_frame.keys() if key is not 'time')

        if default is None:
            if identifier not in first_frame:
                raise ValueError("Missing value: No default or value '%s' found for animation." % identifier)
            default = self.constructor(first_frame[identifier])  # possibly redundant but important

        if float(first_frame['time']) is not 0.0:
            animation.insert(0, {
                'time': 0.0
            })

        timestamps = []
        values = []
        for frame in animation:
            timestamps.append(float(frame['time']))

            if identifier in frame:
                value = default = Vector3.from_dict(frame[identifier])  # todo: make generic
            else:
                # consider: only using 'default' for first/last frame?
                value = default

            values.append(value)

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
