import os
from PIL.Image import open as imopen, Image
"""
NPC and player
"""

"""
I'm not on wifi, will get it and a new mic very soon
"""

DIRECTIONS = {
    'north': ( 0, -1),
    'south': ( 0,  1),
    'east' : ( 1,  0),
    'west' : (-1,  0)
}

def sd_from_directory(path):
    d = {}
    for file in os.listdir(path):
        f = os.path.join(path, file)
        file = file.replace('.png', '')
        _ = d.setdefault(file.split('_')[0], {})
        __ = _.setdefault('anim', {})
        if '_' not in file:
            _.setdefault('still', imopen(f))
        else:
            __.setdefault(int(file.split('_')[1]), imopen(f))

    return d


class Player:
    def __init__(self, sprite_dict=None):
        self.sprite_dict = sprite_dict
        self.current_frame = 0
        self.last_moved_leg = 0

    def tick(self):
        self.current_frame = (self.current_frame + 1) % 4

    def render(self, moving, blocked, facing, just_moved, f=0):
        if not moving and not blocked:
            if just_moved:
                copy = self.sprite_dict[facing]['anim'][0].copy()
            else:
                copy = self.sprite_dict[facing]['still'].copy()
        elif moving:
            frame = int(f not in range(8)) + 2*self.last_moved_leg
            copy = self.sprite_dict[facing]['anim'][frame].copy()
        elif blocked:
            copy = self.sprite_dict[facing]['anim'][self.current_frame].copy()
        else:
            copy = self.sprite_dict[facing]['still'].copy()
        return copy

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