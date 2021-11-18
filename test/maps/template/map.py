from engine.map_tile import *
from engine.map import Map

import os
def local_path(path):
    return os.path.abspath(os.path.join(__file__, os.pardir, path))


# Map xcf location
xcf =''

# Map tile layer 0
l0 = [

]

# Map tile layer 1
l1 = [

]

# Warp data
warp = {
    None: {
        None: (False, None),
    }
}

def get_map():
    map_ =  Map(
        local_path(xcf),
        spawn=(0, 0),
        warp_data=warp
    )

    map_.tiles[0] += l0
    map_.tiles[1] += l1

    return map_