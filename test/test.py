from engine.map import Map
from engine.map_tile import MapTile, AnimatedMapTile
from engine.npc import Player, sd_from_directory
import pygame

player = Player(sd_from_directory('/home/mcxreeper/poop/player'))
testmap = Map('test/back.png', player)

def pilImageToSurface(pilImage):
    return pygame.image.fromstring(
        pilImage.tobytes(), pilImage.size, pilImage.mode).convert()

pygame.init()
window = pygame.display.set_mode((240, 160))
clock = pygame.time.Clock()
font = pygame.font.SysFont('Ubuntu Mono', 16)

# testmap.cx = 5
# testmap.cy = 3



run = True
while run:
    clock.tick(60)
    text = f'center: {testmap.cx, testmap.cy}\ndestination: {testmap.dx, testmap.dy}\nframe: {testmap.fx, testmap.fy}'
    text += f'\nmoving: {testmap.moving}'
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        testmap.move(0, -1)
    elif keys[pygame.K_s]:
        testmap.move(0, 1)
    elif keys[pygame.K_a]:
        testmap.move(-1, 0)
    elif keys[pygame.K_d]:
        testmap.move(1, 0)



    testmap.tick()
    pygameSurface = pilImageToSurface(testmap.render())
    window.fill(0)
    window.blit(pygameSurface, (0, 0))
    for i, textlet in enumerate(text.split('\n')):
        t = font.render(textlet, True, (255, 255, 255))
        window.blit(t, (0, i*16))
    pygame.display.flip()