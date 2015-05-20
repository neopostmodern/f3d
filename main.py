#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import logging
import os

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

try:
    film = film.FakeFilm(os.path.join(os.getcwd(), arguments.setting_file))
    fm = FileManagement()
except Exception as exception:  # todo: more specific error catching
    print("Fatal error during initialization: ")
    print(exception)
    exit(1)

for index in range(int(Settings.timing['out'] * Settings.frames_per_second)):
    fm.svg_output(index, film.render(index / Settings.frames_per_second))
