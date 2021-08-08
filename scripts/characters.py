import json
import os

characters = {}
prefix = "./data/raids"
for filename in os.listdir(prefix):
    with open(os.path.join(prefix, filename, "analysis.json")) as analysis_file:
        with open(os.path.join(prefix, filename, "logs.json")) as logs_file:
            data = json.load(analysis_file)
            logs_data = json.load(logs_file)
            for character in data.values():
                characters.setdefault(character["name"], []).append(
                    {
                        "zoneID": logs_data["zoneID"],
                        "startTime": logs_data["startTime"],
                        "reportCode": filename,
                        "bosses": list(character.get("fights", {}).keys()),
                    }
                )


for (name, raids) in characters.items():
    raids = sorted(raids, key=lambda x: x["startTime"])
    with open(f"./data/characters/{name}.json", "w+") as file:
        json.dump(raids, file)
