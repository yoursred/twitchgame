"""
Map
"""
from PIL.Image import Image, open as imopen, new as imnew

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

black = imnew('RGB', (240, 160))

class Map:
    def __init__(self, background, player):
        self.background: Image = imopen(background)

        if sum([_ % 16 for _ in self.background.size]) != 0:
            raise ValueError(
                f'Provided background image has size {self.background.size}, not a multiple of 16'
            )

        self.player = player
        self.tiles = []
        self.objects = []

        self.fx, self.fy = 0, 0
        self.pf = 0
        self.cooldown = 0
        self.player_facing = 'south'
        self.moving = False
        self.just_moved = 0

        self.cx, self.cy = 0, 0

        self.dx, self.dy = self.cx, self.cy


    def move(self, x, y):
        if getfacing(x, y, self.player_facing) != self.player_facing and not self.moving:
            self.player_facing = getfacing(x, y, self.player_facing)
            self.cooldown = 5
            self.just_moved = 4
        elif (checksameaxis((self.cx + x, self.cy + y), (self.dx, self.dy)) and not self.moving) or\
           (checksameaxis((self.cx + x, self.cy + y), (self.cx, self.cy)) and not self.moving):
            if not self.cooldown:
                self.moving = True
                self.dx += x
                self.dy += y

    def tick(self):
        if self.cooldown:
            self.cooldown -= 1
        if self.moving and self.cy == self.dy:
            if not (self.pf % 15):
                self.player.tick()
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
                self.player.current_frame = 0
        elif self.moving and self.cx == self.dx:
            if not (self.pf % 12):
                self.player.tick()
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
                self.player.current_frame = 0
        self.pf = (self.pf + 1) % 16

    def render(self):
        blackcopy = black.copy()
        copy = self.background.copy()
        self.objects.sort(key=lambda _:_.y)
        for tile in self.tiles:
            copy.paste(tile.sprite, tile.screen_pos)
        for obj in self.objects:
            copy.paste(obj.sprite, obj.pos)
        if not self.moving:
            blackcopy.paste(copy, ((-self.cx+7)*16, (-2*self.cy+9)*8))
        else:
            blackcopy.paste(copy, ((-self.cx+7)*16 - self.fx, (-2*self.cy+9)*8 - self.fy))
        player = self.player.render(self.moving, self.player_facing, self.just_moved)
        blackcopy.paste(player, (112, 64), player)
        if self.just_moved:
            self.just_moved -= 1
        return blackcopy