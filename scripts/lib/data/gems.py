import json

from lib.gem import Gem

gems = {}

with open("./data/config/gems.json") as file:
    gems = {d["id"]: Gem(d) for d in json.load(file)}


def load_gem(gem_id):
    # do not store those gems as we may want to reorganize them correctly and restrict them. will print a message saying it's loading
    from .wowhead import get_wowhead_data

    data = get_wowhead_data(gem_id=gem_id)
    for name, color in _name_to_color.items():
        if name in data["name"]:
            data["color"] = color
            break
    gem = Gem(data)
    gems[gem.id] = gem
    return gem


_name_to_color = {"Pierre d'aube": "yellow"}
