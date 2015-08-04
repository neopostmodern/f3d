#!/usr/bin/env python
#-*- coding: utf-8 -*-
from multiprocessing.pool import Pool
import os
import subprocess
import tempfile
import logging
from f3d.file_management import FileManagement
from f3d.settings import Settings

__author__ = 'neopostmodern'

SLIMER_EXECUTABLE = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../slimerjs/slimerjs")

# todo: enable transparent rendering
# one (bad) approach: https://github.com/laurentj/slimerjs/issues/154#issuecomment-58495876
COLORS = ["#0000FF", "#FFFF00"]


# hack: must be a top level function for pickling to work
# http://stackoverflow.com/a/1816969/2525299
def merge_frame(frame_index):
    file_name = FileManagement.png_file_path_for_frame(frame_index)

    input_file_names = [
        PngService.file_name_for_colored_background(file_name, COLORS[0]),
        PngService.file_name_for_colored_background(file_name, COLORS[1])
    ]

    merged_file_name = FileManagement.png_file_path_for_frame(frame_index)

    command = "convert %s %s -alpha off " \
        "\( -clone 0,1 -compose difference -composite -separate -evaluate-sequence max -auto-level -negate \) " \
        "\( -clone 0,2 -fx \"v==0?0:u/v-u.p{0,0}/v+u.p{0,0}\" \) " \
        "-delete 0,1 +swap -compose Copy_Opacity -composite %s" % (
            input_file_names[0],
            input_file_names[1],
            merged_file_name
        )

    return_value = os.system(command)

    for input_file_name in input_file_names:
        os.remove(input_file_name)

    return return_value, merged_file_name


class PngService:
    def __init__(self):
        # http://stackoverflow.com/a/5209746/2525299
        # self.executor = ThreadPoolExecutor(max_workers=1)
        pass

    def __execute_slimer_commands(self, commands):
        with tempfile.NamedTemporaryFile(suffix='.js') as slimer_file:
            slimer_file.write(bytes(commands, 'UTF-8'))
            slimer_file.flush()

            command = [
                SLIMER_EXECUTABLE,
                os.path.abspath(slimer_file.name)
            ]

            if Settings.headless:
                command.insert(0, 'xvfb-run')

            # subprocess.Popen(command)
            os.system(' '.join(command))

    @staticmethod
    def __slimer_initialization_code():
        return "page.viewportSize = { width: 1920, height: 1080 };"

    # hack: make private again, but currently global `merge_frames` function depends on this
    @staticmethod
    def file_name_for_colored_background(file_path, color):
        path, file_name = os.path.split(file_path)
        file_name = file_name.replace(".png", "-%s.png" % color.replace('#', ''))

        if Settings.in_memory_storage:
            path = "/run/shm/"

        return os.path.join(path, file_name)


    @staticmethod
    def __slimer_image_rendering_code(file_name):
        code = ""
        if Settings.transparent:
            for color in COLORS:
                code += """
    page.evaluate(function() {
        document.body.style.background = '%s';
    });
    page.render('%s', { onlyViewport: true });
                """ % (color, PngService.file_name_for_colored_background(file_name, color))
        else:
            code = "page.render('%s', { onlyViewport: true });" % file_name

        return code

    @staticmethod
    def __merge_into_transparent_frames(frame_indices):
        # todo: switch to pathos when 3.x compliant - https://github.com/uqfoundation/pathos/issues/1
        with Pool(processes=Settings.processor_count) as pool:
            for return_value, output_file in pool.imap_unordered(merge_frame, frame_indices):
                if return_value != 0:
                    logging.debug("Frame merge to transparent exited with %d for '%s'" % (return_value, output_file))

        # for frame_index in frame_indices:
        #     merge_frame(frame_index)

    def render_svg_to_png(self, frame_index):
        slimer_commands = """
var page = require('webpage').create();
page
  .open('%s')
  .then(function () {
    %s
    %s
    slimer.exit()
  });
        """ % (
            'http://localhost:8000/html/%d' % frame_index,
            self.__slimer_initialization_code(),
            self.__slimer_image_rendering_code(FileManagement.png_file_path_for_frame(frame_index))
        )

        self.__execute_slimer_commands(slimer_commands)

    # todo: enable parallel rendering
    def batch_render_svg_to_png(self, frame_indices):
        slimer_command_head = """
const { defer } = require('sdk/core/promise');
var page = require('webpage').create();
%s
var deferred = defer();
deferred.resolve();
deferred.promise.then(function () {
        """ % (self.__slimer_initialization_code())

        commands = [slimer_command_head]

        for frame_index in frame_indices:
            command = """
    return page.open('%s');
}).then(function () {
    %s
            """ % (
                'http://localhost:8000/html/%d' % frame_index,
                self.__slimer_image_rendering_code(FileManagement.png_file_path_for_frame(frame_index))
            )

            commands.append(command)

        commands.append("slimer.exit(); });")

        slimer_commands = ''.join(commands)

        self.__execute_slimer_commands(slimer_commands)

        if Settings.transparent:
            logging.debug("Starting merging to transparent...")
            PngService.__merge_into_transparent_frames(frame_indices)
            logging.debug("Post production done.")
        else:
            logging.debug("No post production necessary.")
