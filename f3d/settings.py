#!/usr/bin/env python
# -*- coding: utf-8 -*-
import multiprocessing
from f3d.util.vectors import Vector2

__author__ = 'neopostmodern'


class _Image:
    def __init__(self, specification):
        if 'size' in specification:
            self.size = Vector2.from_dict(specification['size'], ['width', 'height'])

        if 'input_size' not in specification:
            self.input_size = self.size  # todo: probably doesn't make sense!
            self.output_size = self.size

        # todo: other combinations of sizes / values

        # todo: fail if none above present


class _Timing:
    def __init__(self, specification):
        self.begin = specification.get('in', 0)
        if 'out' not in specification:
            raise ValueError("Settings: Missing value for 'timing/out'.")
        self.end = specification['out']

        self.duration = self.end - self.begin


class _Settings:
    def __init__(self):
        self.processor_count = multiprocessing.cpu_count()

    def set(self, settings):
        # todo: make all properties explicit
        self.__dict__.update(settings)

        self.image = _Image(self.image)

        if 'timing' not in settings:
            raise ValueError("Settings: Missing value for 'timing'.")
        self.timing = _Timing(settings['timing'])

    def add(self, name, value):
        setattr(self, name, value)

Settings = _Settings()