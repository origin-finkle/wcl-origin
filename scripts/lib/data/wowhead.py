import json
import requests
import xml.etree.ElementTree as ET

wowhead = {}

with open("./data/config/wowhead.json") as file:
    wowhead = json.load(file)


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
