#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lxml import etree

__author__ = 'neopostmodern'

import os
import shutil

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

    def svg_output(self, frame_index, svg):
        with open(os.path.join(
                self.svg_output_directory,
                "%s-frame-%04d.svg" % (Settings.project_identifier, frame_index)), mode="w"
        ) as output_file:
            output_file.write(etree.tostring(svg, encoding='unicode'))
