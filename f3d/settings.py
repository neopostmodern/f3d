#!/usr/bin/env python
# -*- coding: utf-8 -*-
from f3d.util.vectors import Vector2

__author__ = 'neopostmodern'

from f3d.util.json_inheritor import JsonInheritor


# todo: make private or similar
class Image(JsonInheritor):
    def __init__(self, specification):
        super().__init__(specification)

        if hasattr(self, 'size'):
            self.size = Vector2.from_dict(self.size, ['width', 'height'])

        if not hasattr(self, 'input_size'):
            self.input_size = self.size  # todo: probably doesn't make sense!
            self.output_size = self.size

        # todo: other combinations of sizes / values

        # todo: fail if none above present


class _Settings():
    def set(self, settings):
        self.__dict__.update(settings)

        self.image = Image(self.image)

Settings = _Settings()