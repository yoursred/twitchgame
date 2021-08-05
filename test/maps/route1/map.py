from engine.map_tile import *
from engine.map import Map

import os
def local_path(path):
    return os.path.abspath(os.path.join(__file__, os.pardir, path))


# Map xcf location
xcf ='route1.xcf'


# Map tile layer 0
l0 = [

]

# (14, 0), (25, 0),

# Map tile layer 1
l1 = [

]

def get_map(player, spawn):
    map_ =  Map(
        player,
        local_path(xcf),
        spawn=spawn
    )

    map_.tiles[0] += l0
    map_.tiles[1] += l1

    return map_