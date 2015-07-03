#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lxml import etree

__author__ = 'neopostmodern'

import os
import shutil
import subprocess as subprocess

from f3d.settings import Settings


class FileManagement():
    def __init__(self):
        self.svg_output_base_directory = os.path.join(
            os.getcwd(),
            Settings.paths['svg_output']
        )
        self.svg_output_directory = os.path.join(
            self.svg_output_base_directory,
            Settings.project_identifier
        )
        
        self.png_output_base_directory = os.path.join(
            os.getcwd(),
            Settings.paths['png_output']
        )
        self.png_output_directory = os.path.join(
            self.png_output_base_directory,
            Settings.project_identifier
        )

        self.__ensure_directory_exists(self.svg_output_base_directory)
        self.__ensure_directory_exists(self.svg_output_directory, override=True)
        self.__ensure_directory_exists(self.png_output_base_directory)
        self.__ensure_directory_exists(self.png_output_directory, override=True)

    @staticmethod
    def __ensure_directory_exists(path, override=False):
        if os.path.exists(path):
            if override:
                shutil.rmtree(path)
            else:
                return

        os.makedirs(path)

    @staticmethod
    def svg_file_name_for_index(frame_index):
        return "%s-frame-%04d.svg" % (Settings.project_identifier, frame_index)

    def svg_file_path_for_frame(self, frame_index):
        return os.path.join(
            self.svg_output_directory,
            self.svg_file_name_for_index(frame_index)
        )
    
    @staticmethod
    def png_file_name_for_index(frame_index):
        return "%s-frame-%04d.png" % (Settings.project_identifier, frame_index)

    def png_file_path_for_frame(self, frame_index):
        return os.path.join(
            self.png_output_directory,
            self.png_file_name_for_index(frame_index)
        )

    def svg_output(self, frame_index, svg):
        with open(self.svg_file_path_for_frame(frame_index), mode="w"
        ) as output_file:
            output_file.write(etree.tostring(svg, encoding='unicode'))

    # todo: move into different module?
    def render_svg_to_png(self, frame_index):
        # https://inkscape.org/en/doc/inkscape-man.html
        command = ['inkscape',
                   '-z',  # without GUI
                   '-f', self.svg_file_path_for_frame(frame_index),
                   '-w 1920',
                   '-j',
                   '-e', self.png_file_path_for_frame(frame_index)]

        subprocess.Popen(command)
        # subprocess.check_call(command)
