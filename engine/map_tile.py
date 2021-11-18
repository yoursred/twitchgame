"""
Map Tile
"""
import numpy as np
from PIL.Image import Image, open as imopen, new as imnew
import pygame

import os


def rect(w, h):
    return [(x, y) for x in range(w) for y in range(h)]


black = imnew('RGBA', (16, 16))


class MapTile:
    def __init__(self, pos=(0,0), sprite=None):
        self.sprites = None
        self.current_frame = None
        self.interval = None
        if isinstance(sprite, pygame.Surface):
            self.sprite = sprite
        else:
            self.sprite: pygame.Surface = pygame.image.load(sprite).convert()

        self.sprite_size = self.sprite.get_width(), self.sprite.get_width(),

        if self.sprite_size != (16, 16) and self.sprite is not None:
            raise ValueError(
                f'Provided background image has size {self.sprite_size}, not a multiple of 16'
            )

        self.collision = False
        self.animated = False
        self.x, self.y = pos

    @property
    def pos(self):
        return self.x, self.y

    def screen_pos(self, cx, cy, res, fx=0, fy=0):
        return (2 * (self.x - cx) + int(np.ceil(res[0]/16)) - 1) * 8 - fx, \
               (2 * (self.y - cy) + int(np.ceil(res[1]/16)) - 1) * 8 - fy

    def interact(self, player):
        pass

    def collision(self, player):
        pass

    def render(self):
        return self.sprite

    def start(self):
        pass

    def stop(self):
        pass

    @property
    def width(self):
        return 16

    @property
    def height(self):
        return 16


class ScalableMapTile(MapTile):
    def __init__(self, pos, where=None, sprite=None):
        super(ScalableMapTile, self).__init__(pos, sprite)

        if where is None:
            self._where = [(0, 0)]
        else:
            self._where = where

        self._width = max(self._where, key=lambda _: _[0])[0] - min(self._where, key=lambda _: _[0])[0]
        self._height = max(self._where, key=lambda _: _[1])[1] - min(self._where, key=lambda _: _[1])[1]

        self._width = (self._width + 1) * 16
        self._height = (self._height + 1) * 16

        self._x_offset = min(self._where, key=lambda _: _[0])[0] * 16
        self._y_offset = min(self._where, key=lambda _: _[1])[1] * 16

        self._canvas = pygame.Surface([self._width, self._height], pygame.SRCALPHA) # imnew('RGBA', (self._width, self._height))

    def render(self):
        canvas = self._canvas.copy()

        for pos in self._where:
            canvas.blit(self.sprite,
                         (pos[0]*16 - self._x_offset, pos[1]*16 - self._y_offset))

        return canvas

    def screen_pos(self, cx, cy, res, fx=0, fy=0):
        return (2 * (self.x - cx) + int(np.ceil(res[0]/16)) - 1) * 8 - fx + self._x_offset, \
               (2 * (self.y - cy) + int(np.ceil(res[1]/16)) - 1) * 8 - fy + self._y_offset

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height


class AnimatedMapTile(MapTile):
    def __init__(self, pos, sprites=None, interval=1):
        if sprites is None:
            sprites = []

        if isinstance(sprites, str):
            path = sprites
            files = os.listdir(path)
            files.sort(key=lambda _:int(_.replace('.png', '')))
            sprites = [os.path.join(path, x) for x in files]

        sprites = [
            *map(lambda _: _ if isinstance(_, pygame.Surface) else pygame.image.load(_).convert(), sprites)
        ]

        sprite = sprites[0] if len(sprites) else black.copy()

        super(AnimatedMapTile, self).__init__(pos=pos, sprite=sprite)

        self.sprites: list[pygame.Surface] = sprites

        self.current_frame = 0
        self.animated = True

        self.interval = interval

    def render(self):
        return self.sprites[self.current_frame].copy()


class ScalableAnimatedMapTile(AnimatedMapTile):
    def __init__(self, pos, where=None, sprites=None, interval=1):
        super(ScalableAnimatedMapTile, self).__init__(pos, sprites, interval)


        if where is None:
            self._where = [(0, 0)]
        else:
            self._where = where

        self._width = max(self._where, key=lambda _: _[0])[0] - min(self._where, key=lambda _: _[0])[0]
        self._height = max(self._where, key=lambda _: _[1])[1] - min(self._where, key=lambda _: _[1])[1]

        self._width = (self._width + 1) * 16
        self._height = (self._height + 1) * 16

        self._x_offset = min(self._where, key=lambda _: _[0])[0] * 16
        self._y_offset = min(self._where, key=lambda _: _[1])[1] * 16

        self._canvas = pygame.Surface([self._width, self._height], pygame.SRCALPHA) # imnew('RGBA', (self._width, self._height))

    def render(self):
        canvas = self._canvas.copy()

        for pos in self._where:
            canvas.blit(self.sprites[self.current_frame],
                        (pos[0]*16 - self._x_offset, pos[1]*16 - self._y_offset))

        return canvas

    def screen_pos(self, cx, cy, res, fx=0, fy=0):
        return (2 * (self.x - cx) + int(np.ceil(res[0]/16)) - 1) * 8 - fx + self._x_offset, \
               (2 * (self.y - cy) + int(np.ceil(res[1]/16)) - 1) * 8 - fy + self._y_offset

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height


T = MapTile
ST = ScalableMapTile
AT = AnimatedMapTile
SAT = ScalableAnimatedMapTile
