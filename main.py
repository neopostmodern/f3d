#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import logging
import os
import traceback
import sys
import time

from f3d.file_management import FileManagement
from f3d.rendering.png_service import PngService
from f3d.rendering.svg_server import SvgServer
from f3d.settings import Settings
from f3d import film

__author__ = 'neopostmodern'

__start_time = time.perf_counter()


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

arguments = parser.parse_args()

Settings.add('headless', arguments.headless)
Settings.add('transparent', arguments.transparent)

# configure logging
logging.basicConfig(level=arguments.log_level, stream=sys.stdout)
# hack: http://stackoverflow.com/questions/3105521/google-app-engine-python-change-logging-formatting/3105859#3105859
logging.getLogger().handlers[0].setFormatter(logging.Formatter("%(levelname)-8s %(message)s"))  # "%(asctime)s >

def add_coloring_to_emit_ansi(fn):
    # add methods we need to the class
    def new(*args):
        levelno = args[1].levelno
        if(levelno>=50):
            color = '\x1b[31m' # red
        elif(levelno>=40):
            color = '\x1b[31m' # red
        elif(levelno>=30):
            color = '\x1b[33m' # yellow
        elif(levelno>=20):
            color = '\x1b[32m' # green
        elif(levelno>=10):
            color = '\x1b[35m' # pink
        else:
            color = '\x1b[0m' # normal
        args[1].msg = color + str(args[1].msg) +  '\x1b[0m'  # normal
        return fn(*args)
    return new
logging.StreamHandler.emit = add_coloring_to_emit_ansi(logging.StreamHandler.emit)

logging.info("Hello. This is F3D!")
logging.debug("Selected setting file: %s (as %s)" % (arguments.setting_file, os.path.join(os.getcwd(), arguments.setting_file)))

try:
    film = film.FakeFilm(os.path.join(os.getcwd(), arguments.setting_file))
except Exception as exception:  # todo: more specific error catching
    logging.error("Fatal error during initialization: ")
    logging.error(exception)
    logging.debug(traceback.format_exc())
    exit(1)


frame_count = int(Settings.timing['out'] * Settings.frames_per_second)

logging.info("Starting SVG creation...")
for frame_index in range(frame_count):
    FileManagement.svg_output(frame_index, film.render(frame_index / Settings.frames_per_second))
    # FileManagement.render_svg_to_png(index)
    # png.render_svg_to_png(frame_index)
logging.info("SVG creation complete.")

try:
    logging.info("Starting SVG to PNG rendering...")
    SvgServer()
    png = PngService()
    png.batch_render_svg_to_png(range(frame_count))
    logging.info("SVG to PNG rendering complete.")
except Exception as exception:  # todo: more specific error catching
    logging.error("Fatal error during rendering: ")
    logging.error(exception)
    logging.debug(traceback.format_exc())
    exit(1)

__end_time = time.perf_counter()

logging.info("We're done, it took just %.2f seconds. Good bye!" % (__end_time - __start_time))
