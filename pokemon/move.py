from abc import ABC, abstractmethod, abstractproperty
from pokemon.pokemon import Pokemon


class PokemonMove(ABC):
    def __init__(self, base_power, accuracy, category, type_):
        self.base_power = base_power
        self.accuracy = accuracy
        self.category = category
        self.crit_ratio = 1/16
        self.type = type_

    def damage(self, attacker: Pokemon, defender: Pokemon):
        damage = 2 +  ((((2 * attacker.level) / 5) + 2)
                  * self.base_power * (attacker.stats['atk'] / defender.stats['def'])) / 50

        stab = 1.5 if self.type in attacker.types else 1

        return damage*stab


