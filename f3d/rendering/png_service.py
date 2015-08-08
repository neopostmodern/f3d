#!/usr/bin/env python
#-*- coding: utf-8 -*-
from multiprocessing.pool import Pool
from concurrent.futures import ThreadPoolExecutor
import os
import subprocess
import tempfile
import logging
import re
import sys
from f3d.file_management import FileManagement
from f3d.settings import Settings

__author__ = 'neopostmodern'

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
    # hack: make private again, but currently global `merge_frames` function depends on this
    @staticmethod
    def file_name_for_colored_background(file_path, color):
        path, file_name = os.path.split(file_path)
        file_name = file_name.replace(".png", "-%s.png" % color.replace('#', ''))

        if Settings.in_memory_storage:
            # todo: make platform independent, check if acceptable use of `/run/shm` at all
            path = "/run/shm/"

        return os.path.join(path, file_name)

    @staticmethod
    def render_svg_to_png(frame_indices):
        VERSION_PATTERN = "{ color: '%s', filePath: '%s' }"

        commands = []

        tasks = []
        for frame_index in frame_indices:
            versions = []
            file_path = FileManagement.png_file_path_for_frame(frame_index)

            if Settings.transparent:
                for color in COLORS:
                    colored_file_path = PngService.file_name_for_colored_background(
                        file_path,
                        color
                    )
                    versions.append(VERSION_PATTERN % (color, colored_file_path))
            else:
                versions.append(VERSION_PATTERN % ('none', file_path))

            tasks.append("""
    {
        url: 'http://localhost:8000/html/%d',
        index: %d,
        versions: [
            %s
        ]
    }""" % (frame_index, frame_index, ',\n\t\t\t'.join(versions)))

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
                        console.log(task.index + "/" + version.color);
                    });

                    page.close();
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

        with tempfile.NamedTemporaryFile(suffix='.js') as slimer_file:
            slimer_file.write(bytes('\n'.join(commands), 'UTF-8'))
            slimer_file.flush()

            environment = os.environ.copy()
            environment['SLIMERJSLAUNCHER'] = Settings.configuration.firefox_executable

            command = []

            if Settings.headless:
                command.append('xvfb-run')
                command.append('-a')

            command.append(Settings.configuration.slimerjs_executable)
            command.append(os.path.abspath(slimer_file.name))

            if Settings.transparent:
                class ProcessCounter:
                    def __init__(self):
                        self.total_images_to_merge = len(frame_indices)
                        self.total_images_to_render = self.total_images_to_merge * 2

                        self.rendered_images_count = 0
                        self.merged_images_count = 0

                    def increase_rendered(self, *args, **kwargs):
                        self.rendered_images_count += 1
                        self.print_progress()

                    def increase_merged(self, *args, **kwargs):
                        self.merged_images_count += 1
                        self.print_progress()

                    def print_progress(self):
                        sys.stdout.write("Rendered %3.0f%%, Merged %3.0f%%\r" % (
                            100 * self.rendered_images_count / self.total_images_to_render,
                            100 * self.merged_images_count / self.total_images_to_merge
                        ))
                        sys.stdout.flush()

                counter = ProcessCounter()

                # todo: maybe we can catch errors here
                process = subprocess.Popen(command, stdout=subprocess.PIPE, env=environment)

                rendered_images = {}
                for frame_index in frame_indices:
                    rendered_images[frame_index] = 0

                with ThreadPoolExecutor(max_workers=(Settings.processor_count - 1)) as pool:
                    for line in process.stdout:
                        text = line.decode("utf-8")
                        frame_index = int(re.match(r'\d+', text).group())
                        # we don't care about the color for now, we just need both to finish

                        counter.increase_rendered()

                        rendered_images[frame_index] += 1
                        if rendered_images[frame_index] == 2:
                            merge_process = pool.submit(merge_frame, frame_index)
                            merge_process.add_done_callback(counter.increase_merged)

            else:
                try:
                    subprocess.check_call(command, stdout=subprocess.DEVNULL, env=environment)
                except subprocess.CalledProcessError as error:
                    print(error.output)
                    raise ChildProcessError("[PNG Service] SlimerJS Rendering failed with exit code '%d'." % error.returncode) from error
