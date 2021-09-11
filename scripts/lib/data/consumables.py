import json

from lib.consumable import Consumable

consumables = {}


with open("./data/config/consumables.json") as file:
    consumables = {d["id"]: Consumable(d) for d in json.load(file)}
