#!/usr/bin/env python
#-*- coding: utf-8 -*-
import threading

__author__ = 'neopostmodern'

import http.server
import socketserver
import re as regex

import os
from f3d.settings import Settings
from f3d.file_management import FileManagement

PORT = 8000

class SvgRequestHandler(http.server.BaseHTTPRequestHandler):
    # ignore the log for every connection coming in: http://stackoverflow.com/a/3389505/2525299
    def log_message(self, _format, *args):
        return

    def do_GET(self):
        # todo: make 'static'

        if 'html' in self.path:
            return self.serve_html()
        if 'svg' in self.path:
            return self.serve_svg()

        self.send_error(404, 'No such route: %s' % self.path)
        print("SVG SERVER", 'No such route: %s' % self.path)

    def serve_html(self):
        frame_index_match = regex.search(r'\d+', self.path)
        if frame_index_match is None:
            self.send_error(400, 'No frame index passed: %s' % self.path)
            print("SVG SERVER", 'No frame index passed: %s' % self.path)
            return
        frame_index = int(frame_index_match.group(0))
        frame_path = FileManagement.svg_file_path_for_frame(frame_index)

        try:
            with open(frame_path, mode='r') as svg_file:

#                 html = """
# <!DOCTYPE HTML>
# <html>
#     <head></head>
#     <body>
#         %s
#     </body>
# </html>
#                 """ % svg_file.read()
                html = """
<!DOCTYPE HTML>
<html>
    <head>
        <style>
            body {
                margin: 0;
            }
        </style>
    </head>
    <body>
        <img src="http://localhost:8000/svg/%d" />
    </body>
</html>
                """ % frame_index

                self.send_response(200)
                self.send_header("content-type", "text/html")
                self.end_headers()

                self.wfile.write(bytes(html, 'UTF-8'))
        except IOError as error:
            self.send_error(404, 'SVG frame not found: %d [%s] {Error: %s}' % (frame_index, frame_path, error))
            print("SVG SERVER", 'SVG frame not found: %d [%s] {Error: %s}' % (frame_index, frame_path, error))

    def serve_svg(self):
        frame_index_match = regex.search(r'\d+', self.path)
        if frame_index_match is None:
            self.send_error(400, 'No frame index passed: %s' % self.path)
            print("SVG SERVER", 'No frame index passed: %s' % self.path)
            return
        frame_index = int(frame_index_match.group(0))
        frame_path = FileManagement.svg_file_path_for_frame(frame_index)

        try:
            with open(frame_path, mode='r') as svg_file:
                self.send_response(200)
                self.send_header("content-type", "image/svg+xml")
                self.end_headers()

                self.wfile.write(bytes(svg_file.read(), 'UTF-8'))
        except IOError as error:
            self.send_error(404, 'SVG frame not found: %d [%s] {Error: %s}' % (frame_index, frame_path, error))
            print("SVG SERVER", 'SVG frame not found: %d [%s] {Error: %s}' % (frame_index, frame_path, error))


class SvgServer:
    def __init__(self):
        self.server = http.server.HTTPServer(('', PORT), SvgRequestHandler)
        # http://stackoverflow.com/a/6640475/2525299
        self.server_thread = threading.Thread(target=self.server.serve_forever, daemon=True).start()

    # todo: how to call this with threading?
    def stop(self):
        self.server.socket.close()
