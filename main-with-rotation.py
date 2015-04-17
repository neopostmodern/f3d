
import subprocess
import math

import numpy as np
from lxml import etree

import view
from f3d.util import svg


__author__ = 'neo post modern'

PATH = os.path.dirname(__file__)
IMAGE_SIZE = np.array([1920, 1080])
PROJECT_NAME = "rotation-3d"
SVG_BASE_DIRECTORY = os.path.join(PATH, "svg")
SVG_DIRECTORY = os.path.join(SVG_BASE_DIRECTORY, PROJECT_NAME)
PNG_BASE_DIRECTORY = os.path.join(PATH, "output")
PNG_DIRECTORY = os.path.join(PNG_BASE_DIRECTORY, PROJECT_NAME)





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
    camera.rotation[1] = rotation / 50 * math.pi / 2


    for alpha in alphas:
        projection = camera.project_surface(houseAlpha)
        # print(projection)

        if projection is not None:
            mapping = svg.generate_css3_3d_transformation_matrix(projection)
            # print(mapping)
            # check = mapping.dot([1920, 1080, 0, 1])
            svg_zero = svg.into_svg([0, 0])
            check = mapping.dot([svg_zero[0], svg_zero[1], 0, 1])
            print(projection[1])
            print(check[0] / check[3], check[1] / check[3])

            defs_container.append(houseAlpha.get_svg_transformed_to(mapping))
            svg_container.append(houseAlpha.get_svg_transformed_to(mapping))

    for surface in surfaces:
        projection = camera.project_surface(surface)

        if projection is not None:
            mapping = svg.generate_css3_3d_transformation_matrix(projection)
            svg_container.append(surface.get_svg_transformed_to(mapping))

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