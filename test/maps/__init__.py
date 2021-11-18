from setuptools import find_packages
import os

# import pallet_town

__all__ = find_packages(os.path.abspath(os.path.join(__file__, os.pardir)))

__all__.remove('template')

def mapgetter(name):
    if name in __all__:
        exec(f'from . import {name} as map_', globals())
        return map_.get_map()
    else:
        raise ValueError(f'Map with name {name} not found')

def get_all_maps():
    return {map_: mapgetter(map_) for map_ in __all__}
