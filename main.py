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

houseAlpha = view.AlphaMask('textures/houses-alpha.svg', np.array([-960, -540, 2000]), IMAGE_SIZE)

houseSurface = view.TexturedSurface('textures/houses.svg', np.array([-960, -540, 2000]), IMAGE_SIZE)
houseBackgroundSurface = view.TexturedSurface('textures/houses-gray.svg', np.array([-960, -540, 2100]), IMAGE_SIZE, mask_identifier=houseAlpha.identifier)

for z in range(0, 2200, 20):
    camera.position[0] = z / 2
    camera.position[1] = z / -4
    camera.position[2] = z

    container_svg = etree.parse(open("container.svg", mode='r'))
    svg_container = container_svg.find("//*[@id='container']")
    defs_container = container_svg.find("//*[@id='defs']")

    defs_container.append(houseAlpha.get_transformed_to(
        camera.project_surface(houseAlpha)
    ))
    svg_container.append(houseBackgroundSurface.get_transformed_to(
        camera.project_surface(houseBackgroundSurface)
    ))
    svg_container.append(houseSurface.get_transformed_to(
        camera.project_surface(houseSurface)
    ))

    with open("svg/test-%d.svg" % z, mode="w") as output_file:
        output_file.write(etree.tostring(container_svg, encoding='unicode'))

    # https://inkscape.org/en/doc/inkscape-man.html
    command = ['inkscape',
               '-z',  # without GUI
               '-f', '%s/svg/test-%d.svg' % (PATH, z), '-w 1920',
               '-j',
               '-e', '%s/output/output-%d.png' % (PATH, z)]
    subprocess.Popen(command)
    # subprocess.check_call(command)