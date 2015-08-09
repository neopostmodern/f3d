#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import multiprocessing
import os
from f3d.util.vectors import Vector2

__author__ = 'neopostmodern'


class _Image:
    def __init__(self, specification):
        if 'size' in specification:
            self.size = Vector2.from_dict(specification['size'], ['width', 'height'])
        else:
            raise ValueError("Settings: Missing value for 'image/size'.")


class _Timing:
    def __init__(self, specification):
        self.begin = specification.get('in', 0)
        if 'out' not in specification:
            raise ValueError("Settings: Missing value for 'timing/out'.")
        self.end = specification['out']

        self.duration = self.end - self.begin


class _Configuration:
    def __init__(self, specification, base_path):
        for name, path in specification['executables'].items():
            if path.startswith('.'):
                specification['executables'][name] = os.path.realpath(
                    os.path.join(base_path, path)
                )

        self.slimerjs_executable = specification['executables']['slimerjs']
        self.firefox_executable = specification['executables'].get('firefox', 'firefox')


class _Settings:
    def __init__(self):
        self.processor_count = multiprocessing.cpu_count()
        self.program_path = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))

        config_path = os.path.join(self.program_path, "config.json")

        try:
            with open(config_path, mode='r') as config_json:
                try:
                    config = json.load(config_json)
                    self.configuration = _Configuration(config, self.program_path)
                except ValueError:
                    raise Exception("[Settings] Parsing of config '%s' failed." % config_path)
        except FileNotFoundError as fileError:
            raise Exception("[Settings] Configuration file '%s' not found." % config_path) from fileError

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