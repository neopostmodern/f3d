#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import logging
import os

from f3d.file_management import FileManagement
from f3d.rendering.png_service import PngService
from f3d.rendering.svg_server import SvgServer
from f3d.settings import Settings
from f3d import film

__author__ = 'neopostmodern'



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
except Exception as exception:  # todo: more specific error catching
    print("Fatal error during initialization: ")
    print(exception)
    exit(1)

SvgServer()

png = PngService()
for frame_index in range(int(Settings.timing['out'] * Settings.frames_per_second)):
    FileManagement.svg_output(frame_index, film.render(frame_index / Settings.frames_per_second))
    # FileManagement.render_svg_to_png(index)
    png.render_svg_to_png(frame_index)
