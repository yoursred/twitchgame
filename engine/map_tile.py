"""
Map Tile
"""
from PIL.Image import Image, open as imopen, new as imnew

from threading import Timer
import os



black = imnew('RGBA', (16, 16))

class MapTile:
    def __init__(self, pos=(0,0), sprite=None):
        if isinstance(sprite, Image):
            self.sprite = sprite
        else:
            self.sprite: Image = imopen(sprite)

        if self.sprite.size != (16, 16) and self.sprite is not None:
            raise ValueError(
                f'Provided background image has size {self.sprite.size}, not a multiple of 16'
            )

        self.collision = False
        self.x, self.y = pos

    @property
    def pos(self):
        return self.x, self.y

    def screen_pos(self, cx, cy, fx=0, fy=0):
        return (self.x - cx + 7) * 16 - fx, (2*self.y - 2 * cy + 9) * 8 - fy

    def interact(self, player):
        pass

    def collision(self, player):
        pass

    def render(self):
        return self.sprite

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

        self._canvas = imnew('RGBA', (self._width, self._height))

    def render(self):
        canvas = self._canvas.copy()

        for pos in self._where:
            canvas.paste(self.sprite,
                         (pos[0]*16 - self._x_offset, pos[1]*16 - self._y_offset))

        return canvas

    def screen_pos(self, cx, cy, fx=0, fy=0):
        return (self.x - cx + 7) * 16 - fx + self._x_offset, \
               (2*self.y - 2 * cy + 9) * 8 - fy - self._y_offset

class AnimatedMapTile(MapTile):
    def __init__(self, pos, sprites=None, interval=1):
        if sprites is None:
            sprites = []

        if isinstance(sprites, str):
            path = sprites
            files = os.listdir(path)
            files.sort(key=lambda _:int(_.replace('.png', '')))
            sprites = [os.path.join(path, x) for x in files]

        sprites = [*map(lambda _: _ if isinstance(_, Image) else imopen(_), sprites)]

        sprite = sprites[0] if len(sprites) else black.copy()

        super(AnimatedMapTile, self).__init__(pos=pos, sprite=sprite)

        self.sprites = sprites

        self.current_frame = 0

        self.timer = Timer(1, self.tickframe)
        self.ticking = False
        self.interval = interval

    def tickframe(self):
        self.ticking = True
        self.current_frame = (self.current_frame + 1) % len(self.sprites)
        self.timer = Timer(self.interval, self.tickframe)
        self.timer.start()

    def start(self):
        self.tickframe()

    def stop(self):
        self.timer.cancel()
        self.ticking = False

    def render(self):
        return self.sprites[self.current_frame]

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

        self._canvas = imnew('RGBA', (self._width, self._height))

    def render(self):
        canvas = self._canvas.copy()

        for pos in self._where:
            canvas.paste(self.sprites[self.current_frame],
                         (pos[0]*16 - self._x_offset, pos[1]*16 - self._y_offset))

        return canvas

    def screen_pos(self, cx, cy, fx=0, fy=0):
        return (self.x - cx + 7) * 16 - fx + self._x_offset, \
               (2*self.y - 2 * cy + 9) * 8 - fy - self._y_offset