import json

from lib.temporary_enchant import TemporaryEnchant

temporary_enchants = {}

with open("./data/config/temporary_enchants.json") as file:
    temporary_enchants = {d["id"]: TemporaryEnchant(d) for d in json.load(file)}
