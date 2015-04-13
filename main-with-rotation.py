import shutil
import subprocess
import os
import math

import numpy as np
from lxml import etree

import view
import svg_utility

__author__ = 'neo post modern'

PATH = os.path.dirname(__file__)
IMAGE_SIZE = np.array([1920, 1080])
PROJECT_NAME = "rotation"
SVG_BASE_DIRECTORY = os.path.join(PATH, "svg")
SVG_DIRECTORY = os.path.join(SVG_BASE_DIRECTORY, PROJECT_NAME)
PNG_BASE_DIRECTORY = os.path.join(PATH, "output")
PNG_DIRECTORY = os.path.join(PNG_BASE_DIRECTORY, PROJECT_NAME)


def ensure_directory_exists(path, override=False):
    if os.path.exists(path):
        if override:
            shutil.rmtree(path)
        else:
            return

    os.makedirs(path)

ensure_directory_exists(SVG_BASE_DIRECTORY)
ensure_directory_exists(SVG_DIRECTORY, override=True)
ensure_directory_exists(PNG_BASE_DIRECTORY)
ensure_directory_exists(PNG_DIRECTORY, override=True)



camera = view.Camera(np.array([0, 0, 1000]), 55, IMAGE_SIZE)

houseAlpha = view.AlphaMask('textures/houses-alpha.svg', np.array([-960, -540, 2000]), IMAGE_SIZE)

houseSurface = view.TexturedSurface(
    'textures/houses.svg',
    np.array([-960, -540, 2000]),
    IMAGE_SIZE)
houseBackgroundSurface = view.TexturedSurface(
    'textures/houses-gray.svg',
    np.array([-960, -540, 2100]),
    IMAGE_SIZE,
    mask_identifier=houseAlpha.identifier)


houseSurfaceRotated = view.TexturedSurface(
    'textures/houses-blue.svg',
    np.array([-960, -540, 2000]),
    IMAGE_SIZE,
    rotation=[math.pi / 4, 0, 0])

# print(houseSurface.normalVector)
# print(houseSurfaceRotated.normalVector)
# print(houseSurfaceRotated.rotation)

alphas = [houseAlpha]
surfaces = [houseBackgroundSurface, houseSurface, houseSurfaceRotated]

for index, rotation in enumerate(range(-50, 50, 5)):
    # camera.position[2] = z
    # todo: camera.rotation[1] = rotation / 50 * math.pi / 2

    container_svg = etree.parse(open("container.svg", mode='r'))
    svg_container = container_svg.find("//*[@id='container']")
    defs_container = container_svg.find("//*[@id='defs']")

    for alpha in alphas:
        projection = camera.project_surface(houseAlpha)

        if projection is not None:
            print(projection)
            print(svg_utility.generate_svg_transformation_matrix(projection, full_3d=True))
            exit(42)
            print(houseAlpha.get_svg_transformed_to(projection))

        if projection is not None:
            defs_container.append(houseAlpha.get_svg_transformed_to(projection))

    for surface in surfaces:
        projection = camera.project_surface(surface)
        if projection is not None:
            svg_container.append(surface.get_svg_transformed_to(projection))

    with open(os.path.join(SVG_DIRECTORY, "test-%04d.svg" % index), mode="w") as output_file:
        output_file.write(etree.tostring(container_svg, encoding='unicode'))

    # https://inkscape.org/en/doc/inkscape-man.html
    command = ['inkscape',
               '-z',  # without GUI
               '-f', os.path.join(SVG_DIRECTORY, 'test-%04d.svg' % index),  # input file
               '-w 1920',
               '-j',
               '-e', os.path.join(PNG_DIRECTORY, 'output-%04d.png' % index)  # output file
               ]
    subprocess.Popen(command)
    # subprocess.check_call(command)