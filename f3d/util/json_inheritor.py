#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'neopostmodern'


class JsonInheritor():
    def __init__(self, specification):
        self.__dict__.update(specification)