from engine.animation import OnLedge, OffLedge
from engine.map_tile import *
from engine.map import Map

import os

def local_path(path):
    return os.path.abspath(os.path.join(__file__, os.pardir, path))

ledges = {
    13: [
        (8, 14),
        (16, 22)
    ],
    18: [
        (8, 14)
    ],
    23: [
        (10, 16)
    ],
    28: [
        (8, 10),
        (10, 14),
        (17, 28)
    ],
    34: [
        (23, 28)
    ],
    39: [
        (8, 12),
        (16, 28)
    ],
}

ledges = [(x, y) for y, _ in ledges.items() for __ in _ for x in range(*__)]


def ledge0(engine, facing, *args):
    if engine.current_map.destination in ledges:
        if engine.player.facing == facing:
            engine.current_map.dy += 1
            engine.player.animate(OffLedge(16))
        else:
            engine.current_map.destination = engine.current_map.center
            engine.current_map.offgrid = 0, 0
            if engine.player.animation is None or engine.player.animation.done:
                engine.player.animate(OnLedge(12))

def ledge1(engine, facing, *args):
    if engine.player.facing == facing:
        engine.current_map.dy += 1
        engine.player.animate(OffLedge(16))
    else:
        engine.current_map.destination = engine.current_map.center
        engine.current_map.offgrid = 0, 0
        if engine.player.animation is None or engine.player.animation.done:
            engine.player.animate(OnLedge(12))

# Map xcf location
xcf ='route1.xcf'


# Map tile layer 0
l0 = [

]

# (14, 0), (25, 0),

# Map tile layer 1
l1 = [

]

# Warp data
warp = {
    None: {
        None: (False, None, None, None),
        44: ('pallet_town', (-1, -38), None, False)
    }
}

for x, y in ledges:
    if x in warp:
        warp[x][y] = ('south', None, ledge1, None)
    else:
        warp[x] = {None: (False, None, None, None),}
        warp[x][y] = ('south', None, ledge1, None)


def get_map(parent=None):
    map_ =  Map(
        local_path(xcf),
        spawn=(18, 49),
        warp_data=warp,
        parent=parent
    )

    map_.tiles[0] += l0
    map_.tiles[1] += l1

    return map_