"""
Map
"""
from PIL.Image import Image, open as imopen, new as imnew
import time

checksameaxis = lambda _, __: (_[0] == __[0] and _[1] != __[1]) ^ (_[0] != __[0] and _[1] == __[1])


def getfacing(x, y, e):
    if x > 0:
        return 'east'
    elif x < 0:
        return  'west'
    elif y > 0:
        return 'south'
    elif y < 0:
        return 'north'
    else:
        return e

black = imnew('RGBA', (240, 160))

class Map:
    def __init__(self, background, player, default_collisions=None, spawn=(0, 0)):
        self.background: Image = imopen(background)

        # self.background = self.background.convert('RGBA')

        if sum([_ % 16 for _ in self.background.size]) != 0:
            raise ValueError(
                f'Provided background image has size {self.background.size}, not a multiple of 16'
            )

        self.player = player
        self.tiles = {
            0: [],
            1: [],
            2: []
        }
        self.objects = []
        if default_collisions is None:
            self.default_collisions = []
        else:
            self.default_collisions = default_collisions

        self.fx, self.fy = 0, 0
        self.pf = 0
        self.cooldown = 0
        self.player_facing = 'south'
        self.moving = False
        self.blocked = False
        self.just_moved = 0

        self.cx, self.cy = spawn

        self.dx, self.dy = self.cx, self.cy
        self.lastframe = time.time()

    def start(self):
        for tile in self.tiles[0]:
            if 'start' in dir(tile):
                tile.start()
        for tile in self.tiles[1]:
            if 'start' in dir(tile):
                tile.start()

    def stop(self):
        for tile in self.tiles[0]:
            if 'stop' in dir(tile):
                tile.start()
        for tile in self.tiles[1]:
            if 'stop' in dir(tile):
                tile.start()

    def collisions(self):
        for tile in self.tiles[1]:
            if tile.collision:
                yield tile.pos

    def move(self, x, y):
        if (self.cx + x, self.cy + y) in (list(self.collisions()) + self.default_collisions):
            self.player_facing = getfacing(x, y, self.player_facing)
            self.blocked = True
        elif getfacing(x, y, self.player_facing) != self.player_facing and not self.moving:
            self.player_facing = getfacing(x, y, self.player_facing)
            self.cooldown = 5
            self.just_moved = 4
            self.blocked = False
        elif (checksameaxis((self.cx + x, self.cy + y), (self.dx, self.dy)) and not self.moving) or\
           (checksameaxis((self.cx + x, self.cy + y), (self.cx, self.cy)) and not self.moving):
            self.blocked = False
            if not self.cooldown:
                self.moving = True
                self.dx += x
                self.dy += y
                self.player.last_moved_leg = int(not self.player.last_moved_leg)

    def tick(self):
        if self.cooldown:
            self.cooldown -= 1
        if self.blocked:
            if not (self.pf % 15):
                self.player.tick()
                self.blocked = False
        elif self.moving and self.cy == self.dy:
            if (self.dx - self.cx) != int(self.fx / 16):
                if self.dx - self.cx > 0:
                    self.player_facing = 'east'
                else:
                    self.player_facing = 'west'
                self.fx += abs(self.dx - self.cx) // (self.dx - self.cx)
            else:
                self.fx = 0
                self.cx = self.dx
                self.moving = False
                # self.player.current_frame = 1
        elif self.moving and self.cx == self.dx:
            if (self.dy - self.cy) != int(self.fy / 16):
                if self.dy - self.cy > 0:
                    self.player_facing = 'south'
                else:
                    self.player_facing = 'north'
                self.fy += abs(self.dy - self.cy) // (self.dy - self.cy)
            else:
                self.fy = 0
                self.cy = self.dy
                self.moving = False
                # self.player.current_frame = 1
        self.pf = (self.pf + 1) % 60

    def render(self):
        blackcopy = black.copy()
        copy = self.background.copy()
        self.objects.sort(key=lambda _:_.y)
        for tile in self.tiles[0]:
            blackcopy.alpha_composite(tile.render(), tile.screen_pos(self.cx, self.cy, self.fx, self.fy))
        if not self.moving:
            blackcopy.alpha_composite(copy, ((-self.cx+7)*16, (-2*self.cy+9)*8))

        else:
            blackcopy.alpha_composite(copy, ((-self.cx+7)*16 - self.fx, (-2*self.cy+9)*8 - self.fy))
        for tile in self.tiles[1]:
            blackcopy.alpha_composite(tile.render(), tile.screen_pos(self.cx, self.cy, self.fx, self.fy))
        # render(self, moving, blocked, facing, just_moved, f=0
        player = self.player.render(self.moving, self.blocked, self.player_facing, self.just_moved, abs(self.fx + self.fy))
        blackcopy.alpha_composite(player, (112, 64))
        for tile in self.tiles[2]:
            blackcopy.alpha_composite(tile.render(), tile.screen_pos(self.cx, self.cy, self.fx, self.fy))
        if self.just_moved:
            self.just_moved -= 1
        self.lastframe = time.time()
        return blackcopy

    @property
    def fps(self):
        ft = (time.time()- self.lastframe)
        # return ft
        if ft:
            return 1/ft
        else:
            return float('inf')