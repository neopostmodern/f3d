#!/usr/bin/env python
#-*- coding: utf-8 -*-
import logging
import sys

__author__ = 'neopostmodern'


def configure_logging(log_level):
    logging.basicConfig(level=log_level, stream=sys.stdout)

    # hack: http://stackoverflow.com/questions/3105521/google-app-engine-python-change-logging-formatting/3105859#3105859
    logging.getLogger().handlers[0].setFormatter(logging.Formatter("%(levelname)-8s %(message)s"))  # "%(asctime)s >

    def add_coloring_to_emit_ansi(fn):
        # add methods we need to the class
        def new(*args):
            level = args[1].levelno
            if level >= 50:
                color = '\x1b[31m'  # red
            elif level >= 40:
                color = '\x1b[31m'  # red
            elif level >= 30:
                color = '\x1b[33m'  # yellow
            elif level >= 20:
                color = '\x1b[32m'  # green
            elif level >= 10:
                color = '\x1b[35m'  # pink
            else:
                color = '\x1b[0m'  # normal
            args[1].msg = color + str(args[1].msg) + '\x1b[0m'  # normal
            return fn(*args)
        return new

    logging.StreamHandler.emit = add_coloring_to_emit_ansi(logging.StreamHandler.emit)