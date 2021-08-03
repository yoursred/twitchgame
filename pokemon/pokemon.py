"""
Pokemon class definition
"""

import pokemon.dex as dex
from pokemon.constants import NATURES
from pokemon.helpers import normalize_name, random_set

import random


def exp(group, n):
    e = {
        'erratic': lambda _: ((_ ** 3) * (100 - _)) / 50 if _ < 50 else
        ((_ ** 3) * (150 - _)) / 100 if 50 <= _ < 68 else
        ((_ ** 3) * ((1911 - 10 * _) // 3)) / 500 if 68 <= _ < 98 else
        ((_ ** 3) * (160 - _)) / 100,
        'fast': lambda _: 0.8 * (_ ** 3),
        'mediumfast': lambda _: _ ** 3,
        'mediumslow': lambda _: 1.2 * (_ ** 3) - 15*(_ ** 2) + 100 * _ - 140,
        'slow': lambda _: 1.25 * (_ ** 3),
        'fluctuating': lambda _: (_ ** 3) * ((((_ + 1) / 3) + 24) // 50) if _ < 15 else
        (_ ** 3) * ((_ + 14) / 50) if 15 <= _ < 36 else
        (_ ** 3) * (((_ // 2) + 32) / 50)
    }[group](n)

    if e < 1:
        e = 0

    return int(e)


class Pokemon:
    def __init__(self, dex_id=None, name=None, ivs=None, evs=None, lvl=1, nickname=None):
        if dex_id is None and name is None:
            dex_id = 1
        if dex_id is not None and name is not None:
            raise ValueError('Pass only one of dex_id or name')
        if dex_id is not None:
            mon = dex.mons_by_dex[dex_id]
        else:
            mon = dex.mons[name]
        self.dex = mon['national_id']
        self.species = normalize_name(mon['names']['en'])
        self.types = [_.lower() for _ in mon['types']]
        self.base_stats = mon['base_stats']
        self._expgroup = normalize_name(mon['leveling_rate'])
        self.nature = random.choice([*NATURES.keys()])
        if nickname is None:
            self.name = mon['names']['en']
        else:
            self.name = nickname

        if ivs is None:
            self.ivs = random_set(0, 31, 6)
        else:
            self.ivs = ivs

        if evs is None:
            self.evs = [0]*6
        else:
            self.evs = evs

        self._level = 1
        self._expchange = 0


    @property
    def level(self):
        return self._level

    @property
    def experience(self):
        return exp(self._expgroup, self._level) + self._expchange

    def levelup(self, lvls=1):
        self._expchange = 0
        self._level += lvls

    def expgain(self, amount):
        exp_ =  self.experience + amount
        if self._level == 100:
            return
        if exp_ < exp(self._expgroup, self._level + 1):
            self._expchange += amount
        elif exp_ >= exp(self._expgroup, 100):
            self._level = 100
            self._expchange = 0
        else:
            i = 1
            while exp_ >= exp(self._expgroup, self.level + i) and self.level + i < 100:
                i += 1
            self._expchange = exp_ - exp(self._expgroup, self.level + i - 1)
            self._level = self._level + i - 1



    @property
    def stats(self):
        def poop(x, iv, ev):
            if x[0] == 'hp':
                stat = (((2 * x[1] + iv + (ev // 4)) * self.level) // 100) + self.level + 10
                return int(stat)
            else:
                stat = ((((2 * x[1] + iv + (ev // 4)) * self.level) // 100) + 5) * NATURES[self.nature][x[0]]
                return int(stat//1)

        stats = [*map(
            poop,
            [*self.base_stats.items()],
            self.ivs,
            self.evs
        )]
        return stats

