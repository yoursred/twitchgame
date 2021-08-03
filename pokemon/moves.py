from pokemon.move import PokemonMove

class pound(PokemonMove):
    def __init__(self):
        super(pound, self).__init__(35, 100, 'physical', 'normal')
