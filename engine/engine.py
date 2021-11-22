"""
Engine class definition
"""
import time
from typing import Union

import pygame

from engine.animation import ScreenAnimation
from engine.map import Map
# from engine.misc import scaletup, pil_image_to_surface, curve, black
from engine.misc import scaletup
from engine.ui.dialogue import Dialogue


class Engine:
    def __init__(self, maps, player, starting_map, data=None, res=(240, 160), target_fps=60):
        self.maps: dict[str, Map] = maps
        self.player = player
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
        self.render_scale = rs = 6
        self.pf = 0
        self.fade = 0
        self.target_fps = target_fps

        self.max_fps = 200
        self.fps_lock = False
        self.t = 1
        self.t_history = []
        self.r = 1

        self.running = False
        pygame.init()
        self.window = pygame.display.set_mode((res[0] * rs, res[1] * rs))
        self.clock = pygame.time.Clock()

    def tick(self):
        if not self.paused_for_animation:
            self.current_map.tick(self.player, self.pf)
            self.pf = (self.pf + 1) % self.target_fps
            # print(self.target_fps)
        if self.animation is not None:
            self.animation.tick()
            if self.animation.done:
                self.animation = None

    def animate(self, animation):
        self.animation = animation

    def render_(self):
        return self.current_map.render(self.player, self.res, self.pf, self.target_fps)

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
        font = pygame.font.SysFont('Ubuntu Mono', 12 * self.render_scale)

        dt = 1

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
                elif keys[pygame.K_t]:
                    self.max_fps = 120
                elif keys[pygame.K_r]:
                    self.max_fps = 60
                elif keys[pygame.K_e]:
                    self.max_fps = 30
                elif keys[pygame.K_UP]:
                    if not sum(self.current_map.offgrid):
                        self.current_map.fx_ += round(60*self.timescale)
                        self.current_map.fy_ += round(60 * self.timescale)

                self.tick()
                tt = time.time() - x

                x = time.time()
                warpto, offset, callback, mode = self.get_warp()

                if warpto:
                    if callback is not None:
                        callback(self, warpto, offset, mode, self.timescale)
                    else:
                        self.maps[warpto].map_warp(offset, mode, *self.current_map.warpfrom)
                        self._current_map = warpto

                wt = time.time() - x

                x = time.time()

                rendered = self.render()
                self.window.blit(rendered, (0, 0))

                rt = time.time() - x
                self.t = tt + wt + rt
                self.t_history.append(self.t)
                avg_fps = 1
                if len(self.t_history) > 64:
                    self.t_history.pop(0)
                if not self.fps_lock:
                    avg_fps = round(len(self.t_history) / sum(self.t_history))
                    self.update_fps(avg_fps)
                if debug:
                    text = f'c: {self.current_map.center}\n'
                    text += f'd: {self.current_map.destination}\n'
                    text += f'f_: {self.current_map.fx_, self.current_map.fy_}\n'
                    text += f'f : {self.current_map.fx, self.current_map.fy}\n'
                    text += f'r: {str(round(self.r, 1)).zfill(5)}'
                    text += f'\nm: {self.current_map.moving}\nb: {self.current_map.blocked}\npf: {self.pf}'
                    text += f'\nfps: {round(1000/dt)}\navg: {avg_fps}'
                    text += f'\nT: {str(round(self.t*1000, 1)).zfill(5)}'
                    text += f'\ndt: {str(round(dt, 1)).zfill(5)}'
                    for i, textlet in enumerate(text.splitlines()):
                        t = font.render(textlet, True, (255, 255, 255), (0, 0, 0, 127))
                        self.window.blit(t, (0, i*12*self.render_scale))
            else:
                rendered = self.dialogue.render(res=self.res)
                self.dialogue.update(self.pf)
                self.window.blit(rendered, (0, 0))
            pygame.display.flip()
            dt = self.clock.tick(self.target_fps)

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

    def update_fps(self, fps=None):
        oldfps = self.target_fps
        if fps is None:
            newfps = min(round(1/self.t), self.max_fps)
        else:
            newfps = min(fps, self.max_fps)
        self.r = newfps/oldfps
        self.pf = round(self.pf * self.r)
        self.current_map.fx_ = round(self.current_map.fx_ * self.r)
        self.current_map.fy_ = round(self.current_map.fy_ * self.r)
        self.target_fps = newfps

    @property
    def real_res(self):
        return scaletup(self.res, self.render_scale)

    @property
    def timescale(self):
        return self.target_fps/60
