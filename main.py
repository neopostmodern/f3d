#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import logging

from f3d.file_management import FileManagement
from f3d.settings import Settings

__author__ = 'neopostmodern'

from f3d import film

DEFAULT_SETTING_PATH = 'setting.f3d.json'

parser = argparse.ArgumentParser(description='F3D : Pseudo-3D generative SVG film scenes.')
parser.add_argument('setting_file', default=DEFAULT_SETTING_PATH, type=str, nargs='?',
                    help="File to read setting from [Default: %s]" % DEFAULT_SETTING_PATH)
parser.add_argument('-v', '--verbose', help='Produce more output',
                    action="store_const", dest="log_level", const=logging.INFO)
parser.add_argument('-d', '--debug', help='Produce all debugging output',
                    action="store_const", dest="log_level", const=logging.DEBUG)

arguments = parser.parse_args()
logging.basicConfig(level=arguments.log_level)

logging.debug("Debugging ('debug') output enabled.")
logging.info("Verbose ('info') output enabled.")

film = film.FakeFilm(arguments.setting_file)
fm = FileManagement()

for index in range(int(Settings.timing['out'] * Settings.frames_per_second)):
    fm.svg_output(index, film.render(index / Settings.frames_per_second))