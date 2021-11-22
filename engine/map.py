"""
Map
"""
from typing import Callable, Any, Tuple

import numpy as np
import pygame
from pygame.transform import scale
import time

from engine.map_tile import MapTile
from engine.misc import map_from_xcf

checksameaxis = lambda _, __: (_[0] == __[0] and _[1] != __[1]) ^ (_[0] != __[0] and _[1] == __[1])


def scaletup(_: tuple[int, int], __: int) -> tuple[int, int]:
    return tuple((___ * __ for ___ in _))


def getfacing(x, y, e):
    if x > 0:
        return 'east'
    elif x < 0:
        return 'west'
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


black = lambda _: pygame.Surface(_)


class Map:
    def __init__(self, xcf_path=None, background=None, foreground=None, collisions=None, spawn=(0, 0),
                 warp_data=None, parent=None):
        self.pf_scale = 1
        self.rs = rs = parent.render_scale
        if xcf_path is not None:
            foreground, collisions, background = map_from_xcf(xcf_path)
        if isinstance(background, str):
            self.background: pygame.Surface = pygame.image.load(background).convert()
        else:
            self.background: pygame.Surface = background
        if isinstance(foreground, str):
            self.foreground: pygame.Surface = pygame.image.load(foreground).convert()
        else:
            self.foreground: pygame.Surface = foreground
        self.default_collisions: np.array = collisions

        if sum([_ % 16 for _ in self.background.get_size()]) != 0:
            raise ValueError(
                f'Provided background image has size {self.background.get_size()}, not a multiple of 16'
            )
        if background.get_size() != foreground.get_size():
            raise ValueError(
                f'Provided foreground image has size {self.foreground.get_size()}, different to background size of '
                f'{self.background.get_size()}'
            )

        w = self.default_collisions.shape[0] * 16
        h = self.default_collisions.shape[1] * 16

        if (w, h) != self.background.get_size():
            raise ValueError(
                f'Provided collision array has size {w // 16, h // 16}, does not conform to background size of '
                f'{self.background.get_size()}'
            )

        # Map scaling for subpixel precision

        self.background = scale(background, scaletup(background.get_size(), rs))
        self.foreground = scale(foreground, scaletup(foreground.get_size(), rs))

        self.canvas = black(scaletup(parent.res, self.rs))

        self.size = self.default_collisions.shape

        # self.player = player
        self.parent = parent
        self.tiles: dict[int, list[MapTile]] = {
            0: [],
            1: []
        }

        self.fx_, self.fy_ = 0, 0
        self.pf = 0
        self.cooldown = 0
        self.player_facing = 'south'
        self.moving = False
        self.blocked = False
        self.just_moved = 0

        self.cx, self.cy = spawn

        self.dx, self.dy = self.cx, self.cy
        self.lastframe = time.time()

        if warp_data is None:
            self.warp_data: dict[int, dict[int, tuple]] = {}
        else:
            self.warp_data: dict[int, dict[int, tuple]] = warp_data

    def collisions(self):
        for tile in self.tiles[1]:
            if tile.collision:
                yield tile.pos

    def move(self, x, y, player):
        xy = (self.cx + x, self.cy + y)

        # print(x, y)

        if xy[0] not in range(self.size[0]) or xy[1] not in range(self.size[1]):
            player.facing = getfacing(x, y, player.facing)
            self.blocked = True
        elif xy in self.collisions() or self.default_collisions[xy]:
            player.facing = getfacing(x, y, player.facing)
            self.blocked = True
        elif getfacing(x, y, player.facing) != player.facing and not self.moving:
            player.facing = getfacing(x, y, player.facing)
            self.cooldown = 5
            self.just_moved = 4
            self.blocked = False
        elif (checksameaxis(xy, (self.dx, self.dy)) and not self.moving) or \
                (checksameaxis(xy, (self.cx, self.cy)) and not self.moving):
            self.blocked = False
            if not self.cooldown:
                self.moving = True
                self.dx += x
                self.dy += y
                # print(x, y)
                player.last_moved_leg = int(not player.last_moved_leg)
        elif (checksameaxis(xy, (self.dx, self.dy)) and self.moving) or \
                (checksameaxis(xy, (self.cx, self.cy)) and self.moving):
            if abs(sum(self.offgrid)) == 0 and self.destination != self.center:
                self.dx += x
                self.dy += y
                # print(x, y)
                player.last_moved_leg = int(not player.last_moved_leg)

    def tick(self, player, pf):
        self.pf_scale = self.parent.target_fps / 60
        if self.cooldown:
            self.cooldown -= 1

        player.animation_tick()

        if self.blocked and self.moving:
            self.blocked = False
        if self.blocked:
            if not (pf % round(15 * self.pf_scale)):
                player.tick()
                self.blocked = False
        elif self.moving and self.cy == self.dy:
            if (self.dx - self.cx) != int(self.fx_ / (16 * self.pf_scale)):
                if self.dx - self.cx > 0:
                    player.facing = 'east'
                else:
                    player.facing = 'west'
                self.fx_ += abs(self.dx - self.cx) // (self.dx - self.cx)
            else:
                self.fx_ = 0
                self.cx = self.dx
                self.moving = False
                # player.current_frame = 1
        elif self.moving and self.cx == self.dx:
            if (self.dy - self.cy) != int(self.fy_ / (16 * self.pf_scale)):
                if self.dy - self.cy > 0:
                    player.facing = 'south'
                else:
                    player.facing = 'north'
                self.fy_ += abs(self.dy - self.cy) // (self.dy - self.cy)
            else:
                self.fy_ = 0
                self.cy = self.dy
                self.moving = False
        for tile in self.tiles[0]:
            if tile.animated:
                if not pf % tile.interval:
                    tile.current_frame = (tile.current_frame + 1) % len(tile.sprites)
        for tile in self.tiles[1]:
            if tile.animated:
                if not pf % tile.interval:
                    tile.current_frame = (tile.current_frame + 1) % len(tile.sprites)

    def render(self, player, res, pf, tfps, noplayer=False):
        xf = (-2 * self.cx + round(res[0] / 16) - 1) * 8 * self.rs - self.fx
        yf = (-2 * self.cy + round(res[1] / 16) - 1) * 8 * self.rs - self.fy
        self.canvas.fill((0, 0, 0))

        for tile in self.tiles[0]:
            x0, y0 = tile.screen_pos(self.cx, self.cy, res, self.fx, self.fy)
            x1, y1 = x0 + tile.width, y0 + tile.height
            if screen_visible(x0, y0, x1, y1, *res):
                self.canvas.blit(tile.render(), (x0, y0))

        self.canvas.blit(self.background, (xf, yf))

        for tile in self.tiles[1]:
            x0, y0 = tile.screen_pos(self.cx, self.cy, res, self.fx, self.fy)
            x1, y1 = x0 + tile.width, y0 + tile.height
            if screen_visible(x0, y0, x1, y1, *res):
                self.canvas.blit(tile.render(), (x0, y0))

        if not noplayer:
            player_sprite = player. \
                render(self.moving, self.blocked, self.just_moved, pf, abs(self.fx_ + self.fy_), tfps)

            self.canvas.blit(player_sprite, player.screen_pos(self.cx, self.cy, res, self.fx, self.fy))

        self.canvas.blit(self.foreground, (xf, yf))

        if self.just_moved:
            self.just_moved -= 1
        self.lastframe = time.time()
        return self.canvas

    def map_warp(self, o, m, c, d, f):
        if m:
            self.cx, self.cy = o
            self.dx, self.dy = o
        else:
            self.cx, self.cy = c[0] + o[0], c[1] + o[1]
            self.dx, self.dy = d[0] + o[0], d[1] + o[1]
        self.fx_, self.fy_ = f

    @property
    def warpfrom(self):
        return (self.cx, self.cy), (self.dx, self.dy), (self.fx, self.fy)

    @property
    def center(self):
        return self.cx, self.cy

    @center.setter
    def center(self, value):
        self.cx, self.cy = value

    @property
    def destination(self):
        return self.dx, self.dy

    @destination.setter
    def destination(self, value):
        self.dx, self.dy = value

    @property
    def offgrid(self):
        return self.fx_, self.fy_

    @offgrid.setter
    def offgrid(self, value):
        self.fx_, self.fy_ = value

    @property
    def fps(self):
        ft = (time.time() - self.lastframe)
        # return ft
        if ft:
            return 1 / ft
        else:
            return float('inf')

    @property
    def fx(self):
        return round(self.rs * self.fx_ / self.pf_scale)

    @property
    def fy(self):
        return round(self.rs * self.fy_ / self.pf_scale)

