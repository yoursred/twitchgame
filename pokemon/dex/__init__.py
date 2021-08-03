import json
import os

mons = {}
mons_by_dex = {}

for mon in os.listdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mons')):
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'mons/{mon}')) as f:
        mons[mon[:-5]] = json.load(f)
        mons_by_dex[mons[mon[:-5]]['national_id']] = mons[mon[:-5]]
