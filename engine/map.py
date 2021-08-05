"""
Map
"""
import numpy as np
from PIL.Image import Image, open as imopen, new as imnew
import time
from engine.scripts import map_from_xcf

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

def screen_visible(x0, y0, x1, y1, w, h):
    if (0 < x1 < w) or (0 < x0 < w) or (x0 < 0 < x1) or (x0 < w < x1):
        x = True
    else:
        x = False
    if (0 < y1 < h) or (0 < y0 < h) or (y0 < 0 < y1) or (y0 < h < y1):
        y = True
    else:
        y = False
    return x and y
    # return (0 <= x0 < w and 0 <= y0 < h) or \
    #        (0 <= x1 < w and 0 <= y0 < h) or \
    #        (0 <= x0 < w and 0 <= y1 < h) or \
    #        (0 <= x1 < w and 0 <= y1 < h)

black = imnew('RGBA', (240, 160))

class Map:
    def __init__(self, player, xcf_path=None, background=None, foreground=None, collisions=None, spawn=(0, 0)):
        if xcf_path is not None:
            foreground, collisions, background = map_from_xcf(xcf_path)
        if isinstance(background, str):
            self.background: Image = imopen(background)
        else:
            self.background: Image = background
        if isinstance(foreground, str):
            self.foreground: Image = imopen(foreground)
        else:
            self.foreground: Image = foreground
        self.default_collisions: np.array = collisions


        if sum([_ % 16 for _ in self.background.size]) != 0:
            raise ValueError(
                f'Provided background image has size {self.background.size}, not a multiple of 16'
            )
        if background.size != foreground.size:
            raise ValueError(
                f'Provided foreground image has size {self.foreground.size}, different to background size of '
                f'{self.background.size}'
            )
        
        w = self.default_collisions.shape[0] * 16
        h = self.default_collisions.shape[1] * 16
        
        if (w, h) != self.background.size:
            raise ValueError(
                f'Provided collision array has size {w//16, h//16}, does not conform to background size of '
                f'{self.background.size}'
            )

        self.size = self.default_collisions.shape

        self.player = player
        self.tiles = {
            0: [],
            1: []
        }
        self.objects = []
        # if collisions is None:
        #     self.default_collisions = []
        # else:
        #     self.default_collisions = collisions

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
                tile.start()
        for tile in self.tiles[1]:
                tile.start()

    def stop(self):
        for tile in self.tiles[0]:
                tile.stop()
        for tile in self.tiles[1]:
                tile.stop()

    def collisions(self):
        for tile in self.tiles[1]:
            if tile.collision:
                yield tile.pos

    def move(self, x, y):
        if (xy := (self.cx + x, self.cy + y)) in self.collisions() or self.default_collisions[xy]:
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
        if self.blocked and self.moving:
            self.blocked = False

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

    def render(self, noplayer=False):
        blackcopy = black.copy()
        copy = self.background.copy()
        self.objects.sort(key=lambda _:_.y)

        for tile in self.tiles[0]:
            x0, y0 = tile.screen_pos(self.cx, self.cy, self.fx, self.fy)
            x1, y1 = x0 + tile.width, y0 + tile.height
            if screen_visible(x0, y0, x1, y1, 240, 160):
                blackcopy.alpha_composite(tile.render(), (x0, y0))

        blackcopy.alpha_composite(copy, ((-self.cx+7)*16 - self.fx, (-2*self.cy+9)*8 - self.fy))

        for tile in self.tiles[1]:
            x0, y0 = tile.screen_pos(self.cx, self.cy, self.fx, self.fy)
            x1, y1 = x0 + tile.width, y0 + tile.height
            if screen_visible(x0, y0, x1, y1, 240, 160):
                blackcopy.alpha_composite(tile.render(), (x0, y0))

        if not noplayer:
            player = self.player.\
                render(self.moving, self.blocked, self.player_facing, self.just_moved, abs(self.fx + self.fy))

            blackcopy.alpha_composite(player, (112, 64))

        blackcopy.alpha_composite(self.foreground, ((-self.cx+7)*16 - self.fx, (-2*self.cy+9)*8 - self.fy))

        if self.just_moved:
            self.just_moved -= 1
        self.lastframe = time.time()
        return blackcopy

    def map_warp(self, o, c, d, f, pf, facing):
        self.cx, self.cy = c[0] + o[0], c[1] + o[1]
        self.dx, self.dy = d[0] + o[0], d[1] + o[1]
        self.fx, self.fy = f
        self.pf = pf
        self.player_facing = facing

    @property
    def warpfrom(self):
        return (self.cx, self.cy), (self.dx, self.dy), (self.fx, self.fy), self.pf, self.player_facing

    @property
    def fps(self):
        ft = (time.time()- self.lastframe)
        # return ft
        if ft:
            return 1/ft
        else:
            return float('inf')

