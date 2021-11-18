from engine.engine import Engine
from engine.npc import Player, sd_from_directory
from maps import get_all_maps


# TODO: implement ledges, quirky collision in general
# TODO: implement npcs
# TODO: clean up
# TODO: optimize
#       TODO: optimize rendering (only render what's needed in a scalable tile)
#       TODO: make animated tiles use a global ticked value
#       TODO: map caching
# TODO: add connectivity with smogon servers
# TODO: menu ui
# TODO: fps independent game speed

engine = Engine(None, None, 'pallet_town', res=(288, 160))
maps = get_all_maps()
d = sd_from_directory('/home/yoursred/Documents/Projects/twitchgame/sample_resources/player')
print(d)
player = Player(d)
engine.player = player
engine.player.parent = engine
engine.maps = maps

# print(engine)
if __name__ == '__main__':
    try:
        engine.run(True)
    except KeyboardInterrupt:
        engine.running = False