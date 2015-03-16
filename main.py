import subprocess
import os

import numpy as np
from lxml import etree

import view
import svg_utility

__author__ = 'neo post modern'

PATH = os.path.dirname(__file__)
IMAGE_SIZE = np.array([1920, 1080])

camera = view.Camera(np.array([0, 0, 0]), 55, IMAGE_SIZE)
surface = view.Surface(np.array([-960, -540, 2000]), IMAGE_SIZE)

container_svg = etree.parse(open("container.svg", mode='r'))
container_element = (container_svg.find("//*[@id='container']"))

svg_tree = etree.parse(open("scene.svg", 'r'))
svg_texture = svg_tree.find("//*[@id='texture']")

for z in range(0, 900, 20):
    camera.position[0] = z / 2
    camera.position[1] = z / -4
    camera.position[2] = z

    intersections = camera.project_surface(surface)

    element.set("transform", "matrix(%f %f %f %f %f %f)"
                % tuple(svg_utility.generate_svg_transformation_matrix(intersections)))



    with open("svg/test-%d.svg" % z, mode="w") as output_file:
        output_file.write(etree.tostring(svg_tree, encoding='unicode'))

    # https://inkscape.org/en/doc/inkscape-man.html
    command = ['inkscape',
               '-z',  # without GUI
               '-f', '%s/svg/test-%d.svg' % (PATH, z), '-w 1920',
               '-j',
               '-e', '%s/output/output-%d.png' % (PATH, z)]
    subprocess.Popen(command)
    # subprocess.check_call(command)