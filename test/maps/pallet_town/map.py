from engine.animation import FadeToBlack
from engine.map_tile import *
from engine.map import Map

import os


def local_path(path):
    return os.path.abspath(os.path.join(__file__, os.pardir, path))

# Warp callbacks


def fade(engine, warpto, offset, mode):
    engine.maps[warpto].map_warp(offset, mode, *engine.current_map.warpfrom)
    engine._current_map = warpto
    engine.animate(FadeToBlack(60))


# Map xcf location
xcf = 'pallet.xcf'

# Map tile layer 0
l0 = [
    # SAT((12, 27), rect(4, 8), '/home/mcxreeper/poop/anim/water', 60)
]

# Map tile layer 1
l1 = [
    # SAT((10, 22), rect(3, 2), '/home/mcxreeper/poop/anim/flowers_red', 18),
    # AT((14, 5), '/home/mcxreeper/poop/anim/flowers_red', 18),
    # AT((25, 5), '/home/mcxreeper/poop/anim/flowers_red', 18)
]

# Warp data
warp = {
    None: {
        None: (False, None, None, None),
        5: ('route1', (1, 38), None, False)
    },
    11: {
        None: (False, None, None, None),
        17: ('player_house', (22, 9), fade, True)
    }
}


def get_map():
    map_ =  Map(
        local_path(xcf),
        spawn=(11, 18),
        warp_data=warp
    )

    map_.tiles[0] += l0
    map_.tiles[1] += l1

    return map_