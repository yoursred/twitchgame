import os
from typing import Union

from PIL.Image import open as imopen, Image
import pygame

from engine.animation import PlayerAnimation
from engine.engine import Engine

"""
NPC and player
"""


DIRECTIONS = {
    'north': ( 0, -1),
    'south': ( 0,  1),
    'east' : ( 1,  0),
    'west' : (-1,  0)
}


def sd_from_directory(path, rs=1):
    d = {}
    for file in os.listdir(path):
        f = os.path.join(path, file)
        file = file.replace('.png', '')
        _ = d.setdefault(file.split('_')[0], {})
        __ = _.setdefault('anim', {})
        if '_' not in file:
            z = pygame.image.load(f).convert()
            z.set_colorkey((255, 0, 255))
            _.setdefault('still', pygame.transform.scale(z, (16 * rs, 20 * rs)))
        else:
            z = pygame.image.load(f).convert()
            z.set_colorkey((255, 0, 255))
            __.setdefault(int(file.split('_')[1]), pygame.transform.scale(z, (16 * rs, 20 * rs)))

    return d


class Player:
    def __init__(self, sprite_dict=None, parent=None):
        self.animation: Union[PlayerAnimation, None] = None
        self.sprite_dict = sprite_dict
        self.facing = 'south'
        self.current_frame = 0
        self.last_moved_leg = 0

        self.parent: Union[Engine, None] = parent

        self.rs = self.parent.render_scale

    def tick(self):
        self.current_frame = (self.current_frame + 1) % 4

    def animation_tick(self):
        if self.animation is not None:
            self.animation.tick()
            if self.animation.done:
                self.animation = None

    def screen_pos(self, cx, cy, res, fx=0, fy=0):
        if self.animation is not None:
            if not self.animation.done:
                return self.animation.screen_pos(self, cx, cy, res, fx, fy)
            else:
                return self.rs * ((res[0] - 16) // 2), self.rs * (res[1] // 2 - 16)
        else:
            return self.rs * ((res[0] - 16) // 2), self.rs * (res[1] // 2 - 16)

    def render_(self, moving, blocked, just_moved, pf, f=0) -> Image:
        if not moving and not blocked:
            if just_moved:
                copy = self.sprite_dict[self.facing]['anim'][0].copy()
            else:
                copy = self.sprite_dict[self.facing]['still'].copy()
        elif moving:
            frame = int(f not in range(9)) + 2 * self.last_moved_leg
            copy = self.sprite_dict[self.facing]['anim'][frame].copy()
        elif blocked:
            copy = self.sprite_dict[self.facing]['anim'][self.current_frame].copy()
        else:
            copy = self.sprite_dict[self.facing]['still'].copy()
        return copy

    def render(self, moving, blocked, just_moved, pf, f=0, tfps=30) -> Image:
        if self.animation is not None and not self.animation.done:
            return self.animation.render(self, moving, blocked, just_moved, pf, f)
        else:
            if not moving and not blocked:
                if just_moved:
                    copy = self.sprite_dict[self.facing]['anim'][0].copy()
                else:
                    copy = self.sprite_dict[self.facing]['still'].copy()
            elif moving:
                frame = int((f*60//tfps) not in range(8)) + 2 * self.last_moved_leg
                copy = self.sprite_dict[self.facing]['anim'][frame].copy()
            elif blocked:
                copy = self.sprite_dict[self.facing]['anim'][self.current_frame].copy()
            else:
                copy = self.sprite_dict[self.facing]['still'].copy()
            return copy

    def animate(self, animation):
        self.animation = animation


class NPC:
    def __init__(self, sprite_dict=None, pos=(0, 0)):
        self.sprite_dict = sprite_dict
        self.x, self.y = pos
        self.facing = 'south'
        self.current_frame = 0

    def move(self, direction):
        self.facing = direction
        self.x += DIRECTIONS[direction][0]
        self.y += DIRECTIONS[direction][1]

    def render(self):
        pass
