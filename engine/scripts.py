from gimpformats.GimpLayer import GimpLayer
from gimpformats.gimpXcfDocument import GimpDocument
from PIL.Image import NEAREST
import numpy as np
import pygame

def pilImageToSurface(pilImage):
    return pygame.image.fromstring(
        pilImage.tobytes(), pilImage.size, pilImage.mode)

def map_from_xcf(path):
    xcf = GimpDocument(path)

    if len(xcf.layers) != 3:
        raise ValueError('Provided xcf doesn\'t have exactly 3 layers')

    layers: dict[str, GimpLayer] = {layer.name: layer for layer in xcf.layers}

    layernames = ['foreground', 'collisions', 'background']
    for layername in layers.keys():
        layernames.remove(layername)

    if len(layernames):
        raise ValueError('Layers should have names (\'foreground\', \'collisions\', \'background\')\n'
                         f'provided: {tuple(layers.keys())}')


    collisions = layers['collisions'].image

    collisions = collisions.resize(
        tuple(np.array(collisions.size)//16),
        NEAREST
    )

    collisions = collisions.convert('L').point(lambda p: p > 0 and 255).convert('1')

    collisions = np.array(collisions).transpose()

    foreground = layers['foreground'].image

    background = layers['background'].image

    return pilImageToSurface(foreground), collisions, pilImageToSurface(background)

