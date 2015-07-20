#!/usr/bin/env python
#-*- coding: utf-8 -*-
import math
from f3d.util.animated_vectors import AnimatedVector, StaticVector
from f3d.util.vectors import Vector3

__author__ = 'neopostmodern'


class Object3D:
    def __init__(self, specification):
        is_animated = 'animation' in specification

        if 'position' in specification:
            position = Vector3.from_dict(specification['position'])
        else:
            if is_animated:
                position = None
            else:
                raise ValueError("Camera defined without position (and no animation)")

        if 'rotation' in specification:
            rotation = Vector3.from_dict(specification['rotation']).convert_to_radian()
        else:
            rotation = Vector3()

        if is_animated:
            self.position = AnimatedVector(
                specification['animation'],
                identifier='position',
                constructor=Vector3,
                default=position
            )
            for frame in specification['animation']:
                if 'rotation' in frame:
                    for dimension in ['x', 'y', 'z']:
                        frame['rotation'][dimension] = math.radians(frame['rotation'][dimension])
            self.rotation = AnimatedVector(
                specification['animation'],
                identifier='rotation',
                constructor=Vector3,
                default=rotation
            )
        else:
            self.position = StaticVector(position)
            self.rotation = StaticVector(rotation)
