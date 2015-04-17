#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'neopostmodern'

from numpy import clip


class RangedInterpolation():
    def __init__(self, function, time_range):
        self.function = function
        self.start_time = time_range[0]
        self.end_time = time_range[1]

    def __call__(self, *args, **kwargs):
        if len(args) != 1:
            raise Exception("Call 'RangedInterpolation' with exactly one parameter: time")

        time = clip(args[0], self.start_time, self.end_time)

        return self.function(time)

