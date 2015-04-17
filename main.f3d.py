#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from lxml import etree
from f3d.file_management import FileManagement
from f3d.settings import Settings

__author__ = 'neopostmodern'

from f3d import film

PROJECT_SETTING_PATH = './setting.f3d.json'

film = film.FakeFilm(PROJECT_SETTING_PATH)

fm = FileManagement()

frames_per_second = 10.0 #todo

for index in range(int(Settings.timing['out'] * frames_per_second)):
    fm.svg_output(index, film.render(index / frames_per_second))