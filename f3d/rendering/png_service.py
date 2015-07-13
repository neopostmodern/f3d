#!/usr/bin/env python
#-*- coding: utf-8 -*-
import os
import subprocess
import tempfile
from f3d.file_management import FileManagement
from f3d.settings import Settings

__author__ = 'neopostmodern'

SLIMER_EXECUTABLE = os.path.join(os.getcwd(), "../slimerjs/slimerjs")

class PngService:
    def __init__(self):
        # http://stackoverflow.com/a/5209746/2525299
        # self.executor = ThreadPoolExecutor(max_workers=1)
        pass

    def __execute_slimer_commands(self, commands):
        with tempfile.NamedTemporaryFile(suffix='.js') as slimer_file:
            slimer_file.write(bytes(commands, 'UTF-8'))
            slimer_file.flush()

            # todo: run [headless](http://docs.slimerjs.org/current/installation.html#having-a-headless-slimerjs)
            command = [
                SLIMER_EXECUTABLE,
                os.path.abspath(slimer_file.name)
            ]

            if Settings.headless:
                command.insert(0, 'xvfb-run')

            # subprocess.Popen(command)
            os.system(' '.join(command))

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

        self.__execute_slimer_commands(slimer_commands)

    def batch_render_svg_to_png(self, frame_count):
        slimer_command_head = "const { defer } = require('sdk/core/promise');" \
                              "var webpage = require('webpage').create();" \
                              "webpage.viewportSize = { width: 1920, height: 1080 };" \
                              "var deferred = defer();" \
                              "deferred.resolve();" \
                              "deferred.promise.then(function () {"

        commands = [slimer_command_head]

        for frame_index in range(frame_count):
            command = "return webpage.open('%s'); }).then(function () { webpage.render('%s', { onlyViewport: true });" % (
                'http://localhost:8000/html/%d' % frame_index,
                FileManagement.png_file_path_for_frame(frame_index)
            )

            commands.append(command)

        commands.append("slimer.exit(); });")

        slimer_commands = ''.join(commands)

        self.__execute_slimer_commands(slimer_commands)
