from engine.map import Map
from engine.map_tile import MapTile, AnimatedMapTile, ScalableAnimatedMapTile, ScalableMapTile
from engine.npc import Player, sd_from_directory
import pygame

from maps import mapgetter
import sys


# player = Player(sd_from_directory('/home/mcxreeper/poop/player'))
# route1 = mapgetter('route1', player, (18, 49))
# pallet = mapgetter('pallet_town', player, (11, 18))
#
# testmap = pallet
#
#
# testmap.start()
#
# def pilImageToSurface(pil_image):
#     return pygame.image.fromstring(
#         pil_image.tobytes(), pil_image.size, pil_image.mode).convert()
#
# pygame.init()
# window = pygame.display.set_mode((240, 160))
# clock = pygame.time.Clock()
# font = pygame.font.SysFont('Ubuntu Mono', 12)
# font_bold = pygame.font.SysFont('Ubuntu Mono', 12, bold=True)
#
# # testmap.cx = 5
# # testmap.cy = 3
#
#
#
# run = True
# while run:
#     clock.tick(60)
#     text = f'center: {testmap.cx, testmap.cy}\ndestination: {testmap.dx, testmap.dy}\nframe: {testmap.fx, testmap.fy}'
#     text += f'\nmoving: {testmap.moving}\nblocked: {testmap.blocked}\npf: {testmap.pf}'
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             pallet.stop()
#             route1.stop()
#             run = False
#
#     keys = pygame.key.get_pressed()
#     if keys[pygame.K_w]:
#         testmap.move(0, -1)
#     elif keys[pygame.K_s]:
#         testmap.move(0, 1)
#     elif keys[pygame.K_a]:
#         testmap.move(-1, 0)
#     elif keys[pygame.K_d]:
#         testmap.move(1, 0)
#
#     testmap.tick()
#
#     if testmap is pallet and testmap.dy == 5:
#         route1.map_warp((1, 38), *pallet.warpfrom)
#         testmap = route1
#     if testmap is route1 and testmap.dy == 44:
#         pallet.map_warp((-1, -38), *route1.warpfrom)
#         testmap = pallet
#
#     pygameSurface = pilImageToSurface(testmap.render())
#     window.fill(0)
#     window.blit(pygameSurface, (0, 0))
#     for i, textlet in enumerate(text.split('\n')):
#         t = font.render(textlet, True, (0, 0, 0))
#         window.blit(t, (0, i*12))
#     pygame.display.flip()