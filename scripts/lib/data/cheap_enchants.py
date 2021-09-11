import json

cheap_enchants = set()

with open("./data/config/cheap_enchants.json") as file:
    data = json.load(file)
    cheap_enchants = {d["id"] for d in data}
