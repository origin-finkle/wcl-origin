import json

from lib.gem import Gem

gems = {}

with open("./data/config/gems.json") as file:
    gems = {d["id"]: Gem(d) for d in json.load(file)}
