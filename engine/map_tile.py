"""
Map Tile
"""
from PIL.Image import Image, open as imopen

from threading import Timer

#TODO: scalable tiles

class MapTile:
    def __init__(self, pos=(0,0), sprite=None):
        self.sprite: Image = imopen(sprite)

        if self.sprite.size != (16, 16) and self.sprite is not None:
            raise ValueError(
                f'Provided background image has size {self.sprite.size}, not a multiple of 16'
            )

        self.collision_level = 0
        self.x, self.y = pos

    @property
    def pos(self):
        return self.x, self.y

    @property
    def screen_pos(self):
        return 16*self.x, 16*self.y

    def interact(self, player):
        pass

    def collision(self, player):
        pass



class AnimatedMapTile(MapTile):
    def __init__(self, pos, sprites=None, interval=1):
        super(AnimatedMapTile, self).__init__(pos=pos)

        if sprites is None:
            sprites = []

        self.sprites = [*map(lambda _: _ if isinstance(_, Image) else imopen(_, sprites))]

        self.current_frame = 0

        self.timer = Timer(1, self.tickframe)
        self.ticking = False

    def tickframe(self):
        self.ticking = True
        self.current_frame = (self.current_frame + 1) % len(self.sprites)
        self.timer = Timer(1, self.tickframe)
        self.timer.start()

    def start(self):
        self.tickframe()

    def stop(self):
        self.timer.cancel()
        self.ticking = False

    @property
    def sprite(self):
        return self.sprites[self.current_frame]
