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

    # hack: make private again, but currently global `merge_frames` function depends on this
    @staticmethod
    def file_name_for_colored_background(file_path, color):
        path, file_name = os.path.split(file_path)
        file_name = file_name.replace(".png", "-%s.png" % color.replace('#', ''))

        if Settings.in_memory_storage:
            path = "/run/shm/"

        return os.path.join(path, file_name)

    @staticmethod
    def __merge_into_transparent_frames(frame_indices):
        # todo: switch to pathos when 3.x compliant - https://github.com/uqfoundation/pathos/issues/1
        with Pool(processes=Settings.processor_count) as pool:
            for return_value, output_file in pool.imap_unordered(merge_frame, frame_indices):
                if return_value != 0:
                    logging.debug("Frame merge to transparent exited with %d for '%s'" % (return_value, output_file))

        # for frame_index in frame_indices:
        #     merge_frame(frame_index)

    def render_svg_to_png(self, frame_indices):
        VERSION_PATTERN = "{ color: '%s', filePath: '%s' }"

        commands = []

        tasks = []
        for frame_index in frame_indices:
            versions = []
            file_path = FileManagement.png_file_path_for_frame(frame_index)

            if Settings.transparent:
                for color in COLORS:
                    colored_file_path = self.file_name_for_colored_background(
                        file_path,
                        color
                    )
                    versions.append(VERSION_PATTERN % (color, colored_file_path))
            else:
                versions.append(VERSION_PATTERN % ('none', file_path))

            tasks.append("""
    {
        url: 'http://localhost:8000/html/%d',
        versions: [
            %s
        ]
    }""" % (frame_index, ',\n\t\t\t'.join(versions)))

        commands.append("const Tasks = [\n\t%s\n];" % ',\n\t'.join(tasks))

        # todo: how are errors passed back to us and handled?
        commands.append("""

var queue = [];
Tasks.forEach(function(task) {
    var p = new Promise(function(resolve, reject) {
        var page = require('webpage').create();
        page.viewportSize = { width: 1920, height: 1080 };
        page.open(task.url)
            .then(function(status) {
                if (status == "success") {
                    task.versions.forEach(function (version) {
                        page.evaluate(function(color) {
                            document.body.style.background = color;
                        }, version.color);
                        page.render(version.filePath, { onlyViewport: true });
                    });

                    page.close();
                    console.log("Done with " + task.url);
                    resolve();
                } else {
                    console.log("Sorry, the page is not loaded for " + url);
                    reject(new Error("Some problem occurred with " + url));
                }
            });
    });
    queue.push(p);
});

Promise.all(queue).then(function() {
    phantom.exit();
});""")

        self.__execute_slimer_commands('\n'.join(commands))

        if Settings.transparent:
            logging.debug("Starting merging to transparent...")
            PngService.__merge_into_transparent_frames(frame_indices)
            logging.debug("Post production done.")
        else:
            logging.debug("No post production necessary.")
