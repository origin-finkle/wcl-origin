import os
import logging
import json
import sys
import enum

from lib.base import Base
from lib.player import Player
from lib.events.event import Event
from lib.data import (
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
        fight.remarks = sorted(
            fight.remarks,
            key=lambda x: (
                x.fight if hasattr(x, "fight") else "0",
                x.type,
                x.item_wowhead_attr if hasattr(x, "item_wowhead_attr") else "0",
            ),
        )
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
            player_fight = players[player_id].get_fight(
                name=fight["internal_name"],
            )
            Event.process(
                player=players[player_id],
                player_fight=player_fight,
                event=event,
            )
    for player in players.values():
        for player_fight in player.fights.values():
            player_fight.post_process()
        aggregate_remarks(player=player)

with open("./data/config/wowhead.json", "w") as file:
    json.dump(wowhead, file, indent=4)

try:
    os.mkdir(f"./data/raids/{logs['code']}", mode=0o775)
except FileExistsError:
    pass


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Base):
            return obj.as_json()
        elif isinstance(obj, enum.Enum):
            return obj.value
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
                fight["internal_name"]: {
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
