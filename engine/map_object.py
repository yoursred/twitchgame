"""
Map Object
"""
import os
import re
from operator import mod
from typing import BinaryIO

from PIL.Image import Image, open as imopen


class MapObject:
    def __init__(self, pos=(0,0), sprite=None, colsize=(0, 0), props=None):
        if isinstance(sprite, Image):
            self.sprite: Image = sprite
        else:
            self.sprite: Image = imopen(sprite)

        if sum(map(mod, self.sprite.size, (16, 16))):
            raise ValueError(
                f'Provided sprite has size {self.sprite.size}, not a multiple of 16'
            )


        self.collision_level = 0
        self.x, self.y = pos

        self.props = props

    @property
    def pos(self):
        return self.x, self.y


    def interact(self, player):
        pass

    def collision(self, player):
        pass
