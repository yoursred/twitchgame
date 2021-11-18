"""
Animation
"""
from abc import ABC, abstractmethod

from PIL import Image
import pygame


# black = lambda _, r: pygame.Surface(r, pygame.SRCALPHA) # Image.new('RGBA', r, (0, 0, 0, int(255 * _)))

def black(_, r):
    surface = pygame.Surface(r, pygame.SRCALPHA)
    surface.fill((0, 0, 0, int(255 * _)))
    return surface
curve = lambda x, l, e=2: 1 - ((x - l) / l) ** e


class PlayerAnimation(ABC):
    def __init__(self, length):
        self.length = length
        self.frame = length

    def tick(self):
        if self.frame:
            self.frame -= 1

    @property
    def done(self):
        return not bool(self.frame)

    @abstractmethod
    def screen_pos(self, obj: 'Player', cx: int, cy: int, res: tuple[int, int], fx: int = 0, fy: int = 0):
        ...

    @abstractmethod
    def render(self, obj: 'Player', moving: bool, blocked: bool, just_moved: int, pf: int, f: int = 0):
        ...


class ScreenAnimation(ABC):
    def __init__(self, length):
        self.length = length
        self.frame = length

    def tick(self):
        if self.frame:
            self.frame -= 1

    @property
    def done(self):
        return not bool(self.frame)

    @abstractmethod
    def render(self, obj):
        ...


class TranslateDown(PlayerAnimation):
    def screen_pos(self, obj, cx, cy, res, fx=0, fy=0):
        return (res[0] - 16) // 2, res[1] // 2 - 16 - self.frame // 2

    def render(self, obj, moving, blocked, just_moved, pf, f=0):
        # return obj.render_(*args)
        return obj.sprite_dict[obj.facing]['anim'][pf % 4]

class TranslateUp(PlayerAnimation):
    def screen_pos(self, obj, cx, cy, res, fx=0, fy=0):
        return (res[0] - 16) // 2, res[1] // 2 - 16 + self.frame // 2

    def render(self, obj, moving, blocked, just_moved, pf, f=0):
        # return obj.render_(*args)
        return obj.sprite_dict[obj.facing]['anim'][(pf//16) % 4]

class FadeToBlack(ScreenAnimation):
    def render(self, obj):
        if self.frame == self.length:
            obj.pause_animation()
        if self.frame == self.length // 2:
            obj.unpause_animation()
        frame = obj.render_()
        frame.blit(black(curve(self.frame, self.length), obj.res), (0, 0))
        return frame


class OpenDoor(ScreenAnimation):
    def render(self, obj):
        if self.frame == self.length:
            obj.pause_animation()
        elif self.frame == self.length // 2:
            obj.unpause_animation()

        if self.frame >= self.length * 1 / 2:
            pasted = black(1, obj.res)
        else:
            pasted = black(0, obj.res)
            pasted.blit(black(
                1,
                (
                    int(obj.res[0] * curve(2 * self.frame, self.length) / 2),
                    obj.res[1]
                )
            ), (0, 0))
            pasted.blit(black(
                1,
                (
                    (s := int(obj.res[0] * curve(2 * self.frame, self.length) / 2)),
                    obj.res[1]
                ),
            ), (obj.res[0] - s, 0))
        frame = obj.render_()
        frame.blit(pasted, (0, 0))
        return frame


class OnLedge(PlayerAnimation):
    def screen_pos(self, obj, cx, cy, res, fx=0, fy=0):
        return (res[0] - 16) // 2, res[1] // 2 - 16

    def render(self, obj, moving, blocked, just_moved, pf, f=0):
        # print(pf//15)
        return obj.sprite_dict[obj.facing]['anim'][pf // 15].copy()


class OffLedge(PlayerAnimation):
    def __init__(self, length):
        super(OffLedge, self).__init__(16)
    def screen_pos(self, obj, cx, cy, res, fx=0, fy=0):
        return (res[0] - 16) // 2, res[1] // 2 - 16 - int(12 * curve(abs(fx+fy), 8, 4))

    def render(self, obj, moving, blocked, just_moved, pf, f=0):
        player = obj.render_(True, False, just_moved, pf, f)
        return player