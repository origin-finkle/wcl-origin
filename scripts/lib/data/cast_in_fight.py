import json

cast_in_fight = {}

with open("./data/config/cast_in_fight.json") as file:
    cast_in_fight = {int(k): v for (k, v) in json.load(file).items()}
