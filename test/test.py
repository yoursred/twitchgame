from engine.map import Map
from engine.map_tile import MapTile, AnimatedMapTile, ScalableAnimatedMapTile, ScalableMapTile
from engine.npc import Player, sd_from_directory
import pygame

# TODO: make maps serializable
# TODO: clean up
# TODO: menu ui

def from_ranges(s):
    ranges_ = s.splitlines()
    points = []
    for r in ranges_:
        if '->' in r:
            r = r.split(' -> ')
            x0, y0 = eval(r[0])
            x1, y1 = eval(r[1])
            for x in range(x0, x1+1):
                for y in range (y0, y1+1):
                    points.append((x, y))
        else:
            points.append(eval(r))
    return points

ranges = '''(6, 7) -> (6, 25)
(7, 6) -> (17, 6)
(19, 6) -> (28, 6)
(17, 5) -> (17, 6)
(19, 5) -> (20, 6)
(28, 7) -> (28, 25)
(10, 9) -> (15, 19)
(19, 9) -> (24, 19)
(10, 22) -> (15, 22)
(10, 25)'''



player = Player(sd_from_directory('/home/mcxreeper/poop/player'))
testmap = Map('/home/mcxreeper/poop/towns/pallet.png', player, from_ranges(ranges), (5, 6))
print(testmap.background.mode)

# water = AnimatedMapTile((6, 4), '/home/mcxreeper/poop/anim/water')
puddle = ScalableAnimatedMapTile((12, 20), [(x, y) for x in range(4) for y in range(10)],
                                 '/home/mcxreeper/poop/anim/water')
flowers = ScalableAnimatedMapTile(
    (0, 0), [(14, 0), (25, 0), *[(x, y) for x in range(10, 13) for y in range(17, 19)]],
    # (10, 13), [(4, -13), (15, -13), *[(x, y) for x in range(3) for y in range(2)]],
    '/home/mcxreeper/poop/anim/flowers_red',
    0.3
)

house_rooves = [
    ScalableMapTile((10, 8), [(0, 0), (9, 0)], '/home/mcxreeper/poop/buildings/house0/0.png'),
    ScalableMapTile((11, 8),
                    [(0, 0), (1, 0), (2, 0), (9, 0), (10, 0), (11, 0)],
                    '/home/mcxreeper/poop/buildings/house0/1.png'),
    ScalableMapTile((14, 8), [(0, 0), (9, 0)], '/home/mcxreeper/poop/buildings/house0/2.png'),
]

oak_roof = [
    MapTile((18, 14), '/home/mcxreeper/poop/buildings/oak/0.png'),
    ScalableMapTile((19, 14),
                    [(0, 0), (1, 0), (2, 0), (3, 0)],
                    '/home/mcxreeper/poop/buildings/oak/1.png'),
    MapTile((23, 14), '/home/mcxreeper/poop/buildings/oak/2.png'),
    MapTile((24, 14), '/home/mcxreeper/poop/buildings/oak/3.png'),
]

mailboxes = [
    ScalableMapTile((9, 11), [(0, 0), (9, 0)], '/home/mcxreeper/poop/misc/mailbox.png'),
]

testmap.tiles[0].append(puddle)
testmap.tiles[1].append(flowers)
testmap.tiles[2] += (house_rooves + oak_roof + mailboxes)


testmap.start()

def pilImageToSurface(pilImage):
    return pygame.image.fromstring(
        pilImage.tobytes(), pilImage.size, pilImage.mode).convert()

pygame.init()
window = pygame.display.set_mode((240, 160))
clock = pygame.time.Clock()
font = pygame.font.SysFont('Ubuntu Mono', 12)
font_bold = pygame.font.SysFont('Ubuntu Mono', 12, bold=True)

# testmap.cx = 5
# testmap.cy = 3



run = True
while run:
    clock.tick(60)
    text = f'center: {testmap.cx, testmap.cy}\ndestination: {testmap.dx, testmap.dy}\nframe: {testmap.fx, testmap.fy}'
    text += f'\nmoving: {testmap.moving}\nblocked: {testmap.blocked}\npf: {testmap.pf}'
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            testmap.stop()
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
        window.blit(t, (0, i*12))
    pygame.display.flip()