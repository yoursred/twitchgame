"""
Engine class definition
"""
import time
from typing import Union

import pygame
from PIL import Image

from engine.animation import ScreenAnimation
from engine.map import Map
# from engine.npc import Player
from engine.ui.dialogue import Dialogue

black = lambda _, r: Image.new('RGBA', r, (0, 0, 0, int(255*_)))
curve = lambda x: 1-((x-24)/24)**2

def pilImageToSurface(pilImage):
    return pygame.image.fromstring(
        pilImage.tobytes(), pilImage.size, pilImage.mode).convert()


class Engine:
    def __init__(self, maps, player, starting_map, data=None, res=(240, 160)):
        self.maps: dict[str, Map] = maps
        self.player: Player = player
        if self.player is not None:
            self.player.parent = self

        self._current_map: str = starting_map
        if data is None:
            self.data = {}
        else:
            self.data = data

        self.moving = False
        self.blocked = False
        self.paused_for_animation = False
        self.animation: Union[ScreenAnimation, None] = None
        self.dialogue: Union[Dialogue, None] = None

        self.res = res
        self.pf = 0
        self.fade = 0

        self.running = False
        pygame.init()
        self.window = pygame.display.set_mode((res[0]*3, res[1]*3))
        self.clock = pygame.time.Clock()

    def tick(self):
        if not self.paused_for_animation:
            self.current_map.tick(self.player, self.pf)
            self.pf = (self.pf + 1) % 60
        if self.animation is not None:
            self.animation.tick()
            if self.animation.done:
                self.animation = None

    def animate(self, animation):
        self.animation = animation

    def render_(self):
        return self.current_map.render(self.player, self.res, self.pf)

    def render(self):
        if self.animation is not None:
            if not self.animation.done:
                return self.animation.render(self)
            else:
                return self.render_()
        return self.render_()

    def pause_animation(self):
        self.paused_for_animation = True

    def unpause_animation(self):
        self.paused_for_animation = False

    def move(self, x, y):
        self.current_map.move(x, y, self.player)

    def run(self, debug=False):
        font = pygame.font.SysFont('Ubuntu Mono', 36)

        dt = 1
        wt = 1
        tt = 1
        rt = 1

        self.running = True
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            x = time.time()
            if self.dialogue is None:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_w]:
                    self.move(0, -1)
                elif keys[pygame.K_s]:
                    self.move(0, 1)
                elif keys[pygame.K_a]:
                    self.move(-1, 0)
                elif keys[pygame.K_d]:
                    self.move(1, 0)

                self.tick()
                tt = time.time() - x

                x = time.time()
                warpto, offset, callback, mode = self.get_warp()

                if warpto:
                    # print(warpto, callback.__name__ if callback is not None else None)
                    if callback is not None:
                        callback(self, warpto, offset, mode)
                    else:
                        self.maps[warpto].map_warp(offset, mode, *self.current_map.warpfrom)
                        self._current_map = warpto

                wt = time.time() - x

                x = time.time()

                pygameSurface = self.render()

                self.window.fill(0)
                self.window.blit(pygame.transform.scale(pygameSurface, self.window.get_size()), (0, 0))

                rt = time.time() - x
                if debug:
                    text =  f'c: {self.current_map.center}\n'
                    text += f'd: {self.current_map.destination}\n'
                    text += f'\nm: {self.current_map.moving}\nb: {self.current_map.blocked}\npf: {self.pf}'
                    text += f'\nfps: {round(1000/dt)}\ntt: {round(tt*1000, 1)}\nwt: {round(wt*1000, 1)}'
                    text += f'\nrt: {str(round(rt*1000, 1)).zfill(5)}'
                    for i, textlet in enumerate(text.splitlines()):
                        t = font.render(textlet, True, (255, 255, 255), (0, 0, 0, 127))
                        self.window.blit(t, (0, i*36))
            else:
                rendered = self.dialogue.render()
                self.dialogue.update(self.pf)
                self.window.blit(rendered, (0, 0))
            pygame.display.flip()
            dt = self.clock.tick(60)

    def get_warp(self):
        x, y = self.current_map.destination

        if x in self.current_map.warp_data:
            if y not in self.current_map.warp_data[x]:
                x = None
        elif x not in self.current_map.warp_data:
            x = None
        if y not in self.current_map.warp_data[x].keys():
            y = None

        return self.current_map.warp_data[x][y]

    @property
    def current_map(self) -> Map:
        return self.maps[self._current_map]

    # def __getattr__(self, item):
