import json

from lib.enchant import Enchant

enchants = {}

with open("./data/config/enchants.json") as file:
    data = json.load(file)
    enchants = {d["id"]: Enchant(d) for d in data}
