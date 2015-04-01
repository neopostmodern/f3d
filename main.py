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

houseSurface = view.TexturedSurface(
    'textures/houses.svg',
    np.array([-960, -540, 2000]),
    IMAGE_SIZE,
    opacity=0)
houseBackgroundSurface = view.TexturedSurface(
    'textures/houses-gray.svg',
    np.array([-960, -540, 2100]),
    IMAGE_SIZE,
    mask_identifier=houseAlpha.identifier,
    opacity=0)

alphas = [houseAlpha]
surfaces = [houseBackgroundSurface, houseSurface]

for index, z in enumerate(range(-3000, 2200, 5)):
    camera.position[0] = z / 2
    camera.position[1] = z / -4
    camera.position[2] = z

    container_svg = etree.parse(open("container.svg", mode='r'))
    svg_container = container_svg.find("//*[@id='container']")
    defs_container = container_svg.find("//*[@id='defs']")

    for alpha in alphas:
        if z < alpha.origin[2]:
            defs_container.append(houseAlpha.get_svg_transformed_to(
                camera.project_surface(houseAlpha)
            ))

    for surface in surfaces:
        if index < 400:
            surface.opacity = index / 400

        if z < surface.origin[2]:  # todo: hacky [too z-based]
            svg_container.append(surface.get_svg_transformed_to(
                camera.project_surface(surface)
            ))

    with open("svg/test-%04d.svg" % index, mode="w") as output_file:
        output_file.write(etree.tostring(container_svg, encoding='unicode'))

    # https://inkscape.org/en/doc/inkscape-man.html
    command = ['inkscape',
               '-z',  # without GUI
               '-f', '%s/svg/test-%04d.svg' % (PATH, index), '-w 1920',
               '-j',
               '-e', '%s/output/output-%04d.png' % (PATH, index)]
    subprocess.Popen(command)
    # subprocess.check_call(command)