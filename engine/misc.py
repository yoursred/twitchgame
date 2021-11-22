import os.path as ospath
import pickle

from gimpformats.GimpLayer import GimpLayer
from gimpformats.gimpXcfDocument import GimpDocument
from PIL.Image import NEAREST
import numpy as np
import pygame


def pil_image_to_surface(pil_image):
    return pygame.image.fromstring(
        pil_image.tobytes(), pil_image.size, pil_image.mode).convert()


def map_from_xcf(path):
    xcf = GimpDocument(path)

    mdir = ospath.dirname(path)

    if ospath.exists(cache := ospath.join(mdir, 'map.pkl')) and ospath.getmtime(cache) - ospath.getmtime(path) > 0:
        with open(cache, 'rb') as f:
            foreground, collisions, background, fs, bs = pickle.load(f)
            foreground = pygame.image.fromstring(foreground, fs, 'RGB')
            background = pygame.image.fromstring(background, bs, 'RGB')
            foreground.set_colorkey((255, 0, 255))
            return foreground, collisions, background

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
        tuple(np.array(collisions.size) // 16),
        NEAREST
    )

    collisions = collisions.convert('L').point(lambda p: p > 0 and 255).convert('1')

    collisions = np.array(collisions).transpose()
    foreground = pil_image_to_surface(layers['foreground'].image)
    fs = foreground.get_size()
    background = pil_image_to_surface(layers['background'].image)
    bs = background.get_size()

    # background.set_colorkey((255, 0, 255))
    foreground.set_colorkey((255, 0, 255))

    with open(cache, 'wb') as f:
        pickle.dump((
            pygame.image.tostring(foreground, 'RGB'),
            collisions,
            pygame.image.tostring(background, 'RGB'),
            fs,
            bs
        ), f)

    return foreground, collisions, background


def black(_, r):
    surface = pygame.Surface(r, pygame.SRCALPHA)
    surface.fill((0, 0, 0, int(255 * _)))
    return surface


def curve(x, length, e=2):
    return 1 - ((x - length) / length) ** e


def scaletup(_: tuple[int, int], __: int):
    return tuple((___ * __ for ___ in _))

