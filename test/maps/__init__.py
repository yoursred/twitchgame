from setuptools import find_packages
import os

# import pallet_town

__all__ = find_packages(os.path.abspath(os.path.join(__file__, os.pardir)))

def mapgetter(name, player, spawn):
    if name in __all__:
        exec(f'from . import {name} as map_', globals())
        return map_.get_map(player, spawn)
    else:
        raise ValueError(f'Map with name {name} not found')