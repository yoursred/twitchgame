from engine.animation import TranslateDown, TranslateUp, FadeToBlack, OpenDoor
from engine.map_tile import *
from engine.map import Map

import os
import threading

def local_path(path):
    return os.path.abspath(os.path.join(__file__, os.pardir, path))

# Warp callbacks

def fade(engine, warpto, offset, mode):
    engine.maps[warpto].map_warp(offset, mode, *engine.current_map.warpfrom)
    engine._current_map = warpto
    engine.animate(FadeToBlack(60))

def open_door(engine, warpto, offset, mode):
    if engine.player.facing == 'south':
        engine.maps[warpto].map_warp(offset, mode, *engine.current_map.warpfrom)
        engine._current_map = warpto
        engine.animate(OpenDoor(60))

def translate_down(engine, warpto, offset, mode):
    if engine.player.facing == 'west':
        engine.player.animate(TranslateDown(16))
        engine.animate(FadeToBlack(60))
        engine.maps[warpto].map_warp(offset, mode, *engine.current_map.warpfrom)
        engine._current_map = warpto
        engine.current_map.dx -= 2

def translate_up(engine, warpto, offset, mode):
    if engine.player.facing == 'east':
        engine.player.animate(TranslateUp(16))
        engine.animate(FadeToBlack(60))
        engine.maps[warpto].map_warp(offset, mode, *engine.current_map.warpfrom)
        engine._current_map = warpto
        engine.current_map.dx += 2


# Map xcf location
xcf = 'player_house.xcf'

# Map tile layer 0
l0 = [

]

# Map tile layer 1
l1 = [

]

# Warp data
warp = {
    None: {
        None: (False, None, None, None),
    },
    8: {
        None: (False, None, None, None),
        2: ('player_house', (30, 2), translate_down, True)
    },
    29: {
        None: (False, None, None, None),
        2: ('player_house', (7, 2), translate_up, True)
    },
    22: {
        None: (False, None, None, True),
        9 : ('pallet_town', (11, 18), open_door, True)
    }
}

def get_map():
    map_ =  Map(
        local_path(xcf),
        spawn=(6, 6),
        warp_data=warp
    )

    map_.tiles[0] += l0
    map_.tiles[1] += l1

    return map_