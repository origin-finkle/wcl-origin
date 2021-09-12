import json

from lib.cast_in_fight import CastInFight

cast_in_fight = {}

with open("./data/config/cast_in_fight.json") as file:
    cast_in_fight = {
        int(k): CastInFight(spell_id=k, **v) for (k, v) in json.load(file).items()
    }
