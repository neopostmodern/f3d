#!/usr/bin/env python
#-*- coding: utf-8 -*-
import os
import subprocess
import tempfile
from f3d.file_management import FileManagement

__author__ = 'neopostmodern'

SLIMER_EXECUTABLE = os.path.join(os.getcwd(), "../slimerjs/slimerjs")

class PngService:
    def __init__(self):
        pass

    def render_svg_to_png(self, frame_index):
        slimer_commands = """
var webpage = require('webpage').create();
webpage
  .open('%s')
  .then(function () {
    webpage.viewportSize = { width: 1920, height: 1080 };
    webpage.render('%s', { onlyViewport: true });
    slimer.exit()
  });
        """ % ('http://localhost:8000/html/%d' % frame_index,
               FileManagement.png_file_path_for_frame(frame_index))

        with tempfile.NamedTemporaryFile(suffix='.js') as slimer_file:
            slimer_file.write(bytes(slimer_commands, 'UTF-8'))
            slimer_file.flush()

            command = [
                SLIMER_EXECUTABLE,
                os.path.abspath(slimer_file.name)
            ]

            # subprocess.Popen(command)
            os.system(' '.join(command))
