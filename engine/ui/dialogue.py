"""Dialogue box class"""

import pygame


class Dialogue:
    def __init__(self, text: str, font: pygame.font.Font, shadow: pygame.font.Font):
        self.lines = text.splitlines()
        self.char = 0
        self.line = 0
        self.rate = 15

        self.font = font
        self.shadow = shadow

        self.done = False

    def render(self, res):
        canvas = pygame.Surface(res, pygame.SRCALPHA)

        text = self.lines[self.line][:self.char]

        snippet0 = text
        snippet1 = ''
        if self.line:
            snippet1 = self.lines[self.line - 1]

        if snippet1:
            canvas.blit(self.font.render(snippet1, False, (0, 0, 0)), (16, 124))
            canvas.blit(self.font.render(snippet0, False, (0, 0, 0)), (16, 139))

        else:
            canvas.blit(self.font.render(snippet0, False, (0, 0, 0)), (16, 124))

        return canvas

    def update(self, pf):
        if not pf % self.rate:
            if len(self.lines[self.line]) - 1 == self.char:
                if len(self.lines) - 1 == self.line:
                    self.done = True
                else:
                    self.char = 0
                    self.line += 1
            else:
                self.char += 2