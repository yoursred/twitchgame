from setuptools import find_packages
import os

# import pallet_town

__all__ = find_packages(os.path.abspath(os.path.join(__file__, os.pardir)))

__all__.remove('template')

def mapgetter(name, parent):
    if name in __all__:
        exec(f'from . import {name} as map_', globals())
        m = map_.get_map(parent)
        return m
    else:
        raise ValueError(f'Map with name {name} not found')

def get_all_maps(parent):
    return {map_: mapgetter(map_, parent) for map_ in __all__}
