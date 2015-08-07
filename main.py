#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import logging
import os
import traceback
import time

from f3d.file_management import FileManagement
from f3d.rendering.png_service import PngService
from f3d.rendering.svg_server import SvgServer
from f3d.settings import Settings
from f3d.util.logging_configuration import configure_logging
from f3d import film

__author__ = 'neopostmodern'

__performance = {'start': time.perf_counter()}


DEFAULT_SETTING_PATH = 'setting.f3d.json'

parser = argparse.ArgumentParser(description='F3D : Pseudo-3D generative SVG film scenes.')
parser.add_argument('setting_file', default=DEFAULT_SETTING_PATH, type=str, nargs='?',
                    help="File to read setting from [Default: %s]" % DEFAULT_SETTING_PATH)
parser.add_argument('-v', '--verbose', help='Produce more output',
                    action="store_const", dest="log_level", const=logging.INFO)
parser.add_argument('-d', '--debug', help='Produce all debugging output',
                    action="store_const", dest="log_level", const=logging.DEBUG)
parser.add_argument('-s', '--headless', help='Run headless (opens no windows, previews etc.)',
                    action="store_const", dest="headless", const=True, default=False)
parser.add_argument('-t', '--transparent', help='Alpha channel for output files [Very slow!]',
                    action="store_const", dest="transparent", const=True, default=False)
parser.add_argument('-m', '--tmpfs', help='Try to write temporary files to RAM',
                    action="store_const", dest="tmpfs", const=True, default=False)
parser.add_argument('--timestamp', help='Adds a timestamp to each frame',
                    action="store_const", dest="timestamp", const=True, default=False)

arguments = parser.parse_args()

Settings.add('headless', arguments.headless)
Settings.add('transparent', arguments.transparent)
Settings.add('in_memory_storage', arguments.tmpfs)
Settings.add('add_timestamp', arguments.timestamp)

configure_logging(arguments.log_level)

logging.info("Hello. This is F3D!")
logging.debug("Selected setting file: %s (as %s)" % (arguments.setting_file, os.path.join(os.getcwd(), arguments.setting_file)))

try:
    film = film.FakeFilm(os.path.join(os.getcwd(), arguments.setting_file))
except Exception as exception:  # todo: more specific error catching
    logging.error("Fatal error during initialization: ")
    logging.error(exception)
    logging.debug(traceback.format_exc())
    exit(1)

frame_indices = range(
    int(Settings.timing.begin * Settings.frames_per_second),
    int(Settings.timing.end * Settings.frames_per_second)
)
frame_count = len(frame_indices)

logging.info("Starting SVG creation...")
__performance['start_svg'] = time.perf_counter()
for frame_index in frame_indices:
    FileManagement.svg_output(frame_index, film.render(frame_index / Settings.frames_per_second))
    # FileManagement.render_svg_to_png(index)
    # png.render_svg_to_png(frame_index)
__performance['end_svg'] = time.perf_counter()
logging.info("SVG creation complete. [%.2fs]" % (__performance['end_svg'] - __performance['start_svg']))

try:
    logging.info("Starting SVG to PNG rendering...")
    __performance['start_rendering'] = time.perf_counter()
    SvgServer()
    png = PngService()
    png.render_svg_to_png(frame_indices)
    __performance['end_rendering'] = time.perf_counter()
    logging.info("SVG to PNG rendering complete. [%.2fs]" %
                 (__performance['end_rendering'] - __performance['start_rendering']))
except Exception as exception:  # todo: more specific error catching
    logging.error("Fatal error during rendering: ")
    logging.error(exception)
    logging.debug(traceback.format_exc())
    exit(1)

__performance['end'] = time.perf_counter()

logging.info("We're done, it took just %.2f seconds. Good bye!" % (__performance['end'] - __performance['start']))
