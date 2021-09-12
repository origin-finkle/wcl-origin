import os
import logging
import json
import sys

from lib.base import Base
from lib.player import Player
from lib.events.event import Event
from lib.data import (
    consumables,
    wowhead,
    players,
)

if len(sys.argv) != 2:
    sys.stderr.write(f"Usage: {sys.argv[0]} FILE\n")
    exit(1)


filename = sys.argv[1]

lh = logging.StreamHandler()
lh.setFormatter(logging.Formatter(f"[{filename}] - %(message)s"))
logging.getLogger("default").addHandler(lh)


def aggregate_remarks(player):
    remarks = {}
    for fight in player.fights.values():
        for remark in fight.remarks:
            remarks.setdefault(remark.type, [])
            data = {
                "fight": fight.name,
            }
            data.update(remark.as_json())
            remarks[remark.type].append(data)
    # and now depending on the type we squash the duplicates
    _remove_duplicated_remarks(
        remarks=remarks, remark_type="missing_gems", unique_key="item_wowhead_attr"
    )
    _remove_duplicated_remarks(
        remarks=remarks, remark_type="cheap_gem", unique_key="item_wowhead_attr"
    )
    _remove_duplicated_remarks(
        remarks=remarks, remark_type="no_enchant", unique_key="item_wowhead_attr"
    )
    _remove_duplicated_remarks(
        remarks=remarks, remark_type="cheap_enchant", unique_key="item_wowhead_attr"
    )
    player.remarks = _sort_remarks(remarks=remarks.values())


def _sort_remarks(remarks):
    return sorted(
        [r for remark in remarks for r in remark],
        key=lambda x: (x.get("fight", "0"), x["type"], x.get("item_wowhead_attr", "0")),
    )


def _remove_duplicated_remarks(remarks, remark_type, unique_key):
    unique_dict = {}
    for value in remarks.get(remark_type, []):
        if "fight" in value:
            del value["fight"]  # since we're aggregating
        unique_dict.setdefault(value[unique_key], value)
    remarks[remark_type] = unique_dict.values()


with open(filename) as file:
    logs = json.load(file)
    if not logs["zone"]:
        print("Logs did not contain any fight")
        exit(0)

    for fight in logs["fights"]:
        if fight["name"] in ("Chess Event",):
            continue  # chess don't have anything to report...
        for player_id in fight["friendlyPlayers"]:
            if player_id not in players:
                players[player_id] = Player(logs["masterData"]["actors"][player_id])
        for event in fight["events"]:
            player_id = event.get("sourceID", event.get("source"))
            if player_id not in players:
                continue
            player_fight = players[player_id].get_fight(name=fight["name"])
            Event.process(
                player=players[player_id],
                player_fight=player_fight,
                event=event,
            )
    for player in players.values():
        for player_fight in player.fights.values():
            if player_fight.name == "Chess Event":
                # nothing wrong with having no consumables during chess event
                continue
            missing = {"battle_elixir", "guardian_elixir", "food"}
            invalid = set()
            for aura in player_fight.auras.values():
                consumable = consumables.get(aura["ability"])
                if not consumable:
                    continue
                if consumable.is_battle_elixir():
                    missing.remove("battle_elixir")
                    if consumable.is_restricted(player=player, fight=player_fight):
                        invalid.add(("battle_elixir", consumable.id))
                if consumable.is_guardian_elixir():
                    missing.remove("guardian_elixir")
                    if consumable.is_restricted(player=player, fight=player_fight):
                        invalid.add(("guardian_elixir", consumable.id))
                if consumable.is_food():
                    missing.remove("food")
                    if consumable.is_restricted(player=player, fight=player_fight):
                        invalid.add(("food", consumable.id))
            for missing_consumable in missing:
                player_fight.add_remark(
                    type=f"missing_{missing_consumable}",
                )
            for invalid_consumable in invalid:
                player_fight.add_remark(
                    type=f"invalid_{invalid_consumable[0]}",
                    wowhead_attr=f"domain=fr.tbc&spell={invalid_consumable[1]}",
                )
        aggregate_remarks(player=player)

with open("./data/config/wowhead.json", "w") as file:
    json.dump(wowhead, file)

try:
    os.mkdir(f"./data/raids/{logs['code']}", mode=0o775)
except FileExistsError:
    pass


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Base):
            return obj.as_json()
        return super().default(obj)


with open(f"./data/raids/{logs['code']}/analysis.json", "w+") as file:
    json.dump(
        players, file, indent=4, cls=JSONEncoder
    )  # indenting so we can identify what changes

with open(f"./data/raids/{logs['code']}/logs.json", "w+") as file:
    json.dump(
        {
            "startTime": logs["startTime"],
            "title": logs["title"],
            "actors": [player.name for player in players.values()],
            "zoneID": logs["zone"]["id"] if logs["zone"] else 0,
            "fights": {
                fight["name"]: {
                    "startTime": fight["startTime"],
                    "endTime": fight["endTime"],
                }
                for fight in logs["fights"]
            },
        },
        file,
        indent=4,
        cls=JSONEncoder,
    )
