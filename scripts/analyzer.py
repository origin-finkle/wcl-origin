import os
import json
import requests
import sys
from urllib.parse import urlencode
import xml.etree.ElementTree as ET

from lib.consumable import Consumable
from lib.gem import Gem
from lib.temporary_enchant import TemporaryEnchant

if len(sys.argv) != 2:
    sys.stderr.write(f"Usage: {sys.argv[0]} FILE\n")
    exit(1)

CHEAP_GEM_QUALITY_LOWER_BOUND = 3  # Rare gems at least
SLOTS_TO_ENCHANT = {
    "Tête",
    "Épaule",
    "Torse",
    "Jambes",
    "Pieds",
    "Poignets",
    "Mains",
    "Main droite",
    "Deux mains",
    "Dos",
    "À une main",
}
SLOTS_WITH_TEMPORARY_ENCHANT = {
    "Main droite",
    "Deux mains",
    "À une main",
}
cheap_enchants = set()
consumables = {}
wowhead = {}
gems = {}

players = {}


with open("./data/config/cheap_enchants.json") as file:
    data = json.load(file)
    cheap_enchants = {d["id"] for d in data}

with open("./data/config/wowhead.json") as file:
    wowhead = json.load(file)

with open("./data/config/consumables.json") as file:
    consumables = {d["id"]: Consumable(d) for d in json.load(file)}

with open("./data/config/temporary_enchants.json") as file:
    temporary_enchants = {d["id"]: TemporaryEnchant(d) for d in json.load(file)}

with open("./data/config/gems.json") as file:
    gems = {d["id"]: Gem(d) for d in json.load(file)}

filename = sys.argv[1]


def benefits_from_windfury_totem(player, player_fight):
    if player["subType"] in ("Warrior", "Rogue"):
        return True
    if player["subType"] == "Shaman":
        # has more point in enhancement
        return (
            player_fight["talents"][1]["id"] > player_fight["talents"][0]["id"]
            and player_fight["talents"][1]["id"] > player_fight["talents"][2]["id"]
        )
    if player["subType"] == "Paladin":
        # has more points in vindicte
        return (
            player_fight["talents"][2]["id"] > player_fight["talents"][0]["id"]
            and player_fight["talents"][2]["id"] > player_fight["talents"][1]["id"]
        )
    return False


def get_wowhead_data(item_id=None, gem_id=None):
    global wowhead

    if item_id:
        if item := wowhead["items"].get(f"{item_id}"):
            return item

        print(f"Loading item {item_id} from wowhead")
        r = requests.get(f"https://fr.tbc.wowhead.com/item={item_id}&xml")
        if r.status_code != 200:
            raise Exception(r.text)
        root = ET.fromstring(r.text)
        item = {}
        for item_data in root.findall("item"):
            item["name"] = item_data.find("name").text
            item["slot"] = item_data.find("inventorySlot").text
            json_data = f"{{{item_data.find('jsonEquip').text}}}"
            item["sockets"] = json.loads(json_data).get("nsockets", 0)
            break
        wowhead["items"][f"{item_id}"] = item
        return item

    if gem_id:
        if gem := wowhead["gems"].get(f"{gem_id}"):
            return gem

        print(f"Loading gem {gem_id} from wowhead")
        r = requests.get(f"https://fr.tbc.wowhead.com/item={gem_id}&xml")
        if r.status_code != 200:
            raise Exception(r.text)
        root = ET.fromstring(r.text)
        gem = {}
        for item_data in root.findall("item"):
            gem["name"] = item_data.find("name").text
            gem["quality"] = int(item_data.find("quality").attrib["id"])
            break
        wowhead["gems"][f"{gem_id}"] = gem
        return gem


def process_gear_item(player, player_fight, item):
    wowhead_qs = {
        "domain": "fr.tbc",
        "item": item["id"],
    }
    wowhead_data = get_wowhead_data(item_id=item["id"])
    # gems added to the equipment
    if item.get("gems"):
        for gem in item["gems"]:
            wowhead_gem_data = get_wowhead_data(gem_id=gem["id"])
            if wowhead_gem_data["quality"] < CHEAP_GEM_QUALITY_LOWER_BOUND or (
                (gem_i := gems.get(gem["id"]))
                and gem_i.is_restricted(player=player, fight=player_fight)
            ):
                player_fight["remarks"].append(
                    {
                        "wowhead_attr": f"domain=fr.tbc&item={gem['id']}",
                        "type": "cheap_gem",
                        "item_wowhead_attr": f"domain=fr.tbc&item={item['id']}",
                    }
                )
        wowhead_qs["gems"] = ":".join(f"{gem['id']}" for gem in item["gems"])

    # missing gems on gem slots
    if len(item.get("gems", [])) != wowhead_data["sockets"]:
        player_fight["remarks"].append(
            {
                "type": "missing_gems",
                "item_wowhead_attr": f"domain=fr.tbc&item={item['id']}",
                "count": wowhead_data["sockets"] - len(item.get("gems", [])),
            }
        )

    if item.get("permanentEnchant"):
        if item["permanentEnchant"] in cheap_enchants:
            player_fight["remarks"].append(
                {
                    "wowhead_attr": f"domain=fr.tbc&spell={item['permanentEnchant']}",
                    "type": "cheap_enchant",
                    "item_wowhead_attr": f"domain=fr.tbc&item={item['id']}",
                }
            )
        wowhead_qs["ench"] = item["permanentEnchant"]
    elif wowhead_data["slot"] in SLOTS_TO_ENCHANT:
        player_fight["remarks"].append(
            {
                "type": "no_enchant",
                "item_wowhead_attr": f"domain=fr.tbc&item={item['id']}",
            }
        )
    item["wowhead_attr"] = urlencode(wowhead_qs)

    if item.get("temporaryEnchant"):
        if te := temporary_enchants.get(item["temporaryEnchant"]):
            if te.is_restricted(player=player, fight=player_fight):
                player_fight["remarks"].append(
                    {
                        "type": "invalid_temporary_enchant",
                        "item_wowhead_attr": f"domain=fr.tbc&item={item['id']}&ench={item['temporaryEnchant']}",
                    }
                )
        else:
            player_fight["remarks"].append(
                {
                    "type": "invalid_temporary_enchant",
                    "item_wowhead_attr": f"domain=fr.tbc&item={item['id']}&ench={item['temporaryEnchant']}",
                }
            )
            print(
                f"[{filename}] Unknown temporary enchant {item['temporaryEnchant']} on player {player['name']} and fight {player_fight['name']}"
            )
    elif wowhead_data["slot"] in SLOTS_WITH_TEMPORARY_ENCHANT:
        # could be due to windfury in the group, so this would apply only to melee classes
        if benefits_from_windfury_totem(
            player=player, player_fight=player_fight
        ) and any(
            # at least one shaman is in the raid and participated to the fight
            p["subType"] == "Shaman" and player_fight["name"] in p.get("fights", {})
            for p in players.values()
        ):
            player_fight["remarks"].append(
                {
                    "type": "no_temporary_enchant_but_windfury",
                    "item_wowhead_attr": f"domain=fr.tbc&item={item['id']}",
                }
            )
        else:
            player_fight["remarks"].append(
                {
                    "type": "no_temporary_enchant",
                    "item_wowhead_attr": f"domain=fr.tbc&item={item['id']}",
                }
            )


def aggregate_remarks(player):
    remarks = {}
    for fight in player.get("fights", {}).values():
        for remark in fight["remarks"]:
            remarks.setdefault(remark["type"], [])
            data = {
                "fight": fight["name"],
            }
            data.update(remark)
            remarks[remark["type"]].append(data)
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
    player["remarks"] = _sort_remarks(remarks=remarks.values())


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
            players.setdefault(player_id, logs["masterData"]["actors"][player_id])
        for event in fight["events"]:
            player_id = event.get("sourceID", event.get("source"))
            if player_id not in players:
                continue
            player_fight = (
                players[player_id]
                .setdefault("fights", {})
                .setdefault(
                    fight["name"],
                    {"name": fight["name"], "auras": {}, "remarks": [], "talents": []},
                )
            )
            if event["type"] == "combatantinfo":
                player_fight["talents"] = event["talents"]
                player_fight["auras"] = {
                    aura["ability"]: aura for aura in event["auras"]
                }
                for aura in player_fight["auras"].values():
                    aura["events"] = []
                player_fight["gear"] = [
                    gear
                    for gear in event["gear"]
                    if not gear["icon"].startswith("inv_shirt_") and gear["id"] > 0
                ]
                for item in player_fight["gear"]:
                    process_gear_item(
                        player=players[player_id], player_fight=player_fight, item=item
                    )
            elif event["type"] in ("applybuff",) and player_fight["auras"].get(
                event["abilityGameID"]
            ):
                player_fight["auras"][event["abilityGameID"]]["events"].append(
                    {"type": "applybuff", "time": event["timestamp"]}
                )
            elif event["type"] in ("removebuff",) and player_fight["auras"].get(
                event["abilityGameID"]
            ):
                player_fight["auras"][event["abilityGameID"]]["events"].append(
                    {"type": "removebuff", "time": event["timestamp"]}
                )
                pass
    for player in players.values():
        for player_fight in player.get("fights", {}).values():
            if player_fight["name"] == "Chess Event":
                # nothing wrong with having no consumables during chess event
                continue
            missing = {"battle_elixir", "guardian_elixir", "food"}
            invalid = set()
            for aura in player_fight["auras"].values():
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
                player_fight["remarks"].append(
                    {
                        "type": f"missing_{missing_consumable}",
                    }
                )
            for invalid_consumable in invalid:
                player_fight["remarks"].append(
                    {
                        "type": f"invalid_{invalid_consumable[0]}",
                        "wowhead_attr": f"domain=fr.tbc&spell={invalid_consumable[1]}",
                    }
                )
        aggregate_remarks(player=player)

with open("./data/config/wowhead.json", "w") as file:
    json.dump(wowhead, file)

try:
    os.mkdir(f"./data/raids/{logs['code']}", mode=0o775)
except FileExistsError:
    pass

with open(f"./data/raids/{logs['code']}/analysis.json", "w+") as file:
    json.dump(players, file, indent=4)  # indenting so we can identify what changes

with open(f"./data/raids/{logs['code']}/logs.json", "w+") as file:
    json.dump(
        {
            "startTime": logs["startTime"],
            "title": logs["title"],
            "actors": [player["name"] for player in players.values()],
            "zoneID": logs["zone"]["id"] if logs["zone"] else 0,
        },
        file,
    )
