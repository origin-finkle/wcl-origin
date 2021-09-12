import datetime
import json
import os


def get_raid_lockouts():
    cursor = datetime.datetime(year=2021, month=6, day=2)
    now = datetime.datetime.now()
    lockouts = []
    while cursor < now:
        lockouts.append(cursor)
        cursor += datetime.timedelta(days=7)
    return lockouts


def compute_attendance(raids):
    lockouts = get_raid_lockouts()
    data = {
        "kharazan": {
            "percentage": 0,
            "details": {},
        },
        "gruul": {
            "percentage": 0,
            "details": {},
        },
        "magtheridon": {
            "percentage": 0,
            "details": {},
        },
    }
    idx = 0
    for raid in raids:
        while (
            idx < len(lockouts) and lockouts[idx].timestamp() * 1000 < raid["startTime"]
        ):
            idx += 1
        idx -= 1
        if idx >= len(lockouts):
            break
        # assuming lockouts[idx] is in use
        if "High King Maulgar" in raid["bosses"]:
            data["gruul"]["details"].setdefault(
                lockouts[idx].date().isoformat(), []
            ).append(raid["reportCode"])
        if "Magtheridon" in raid["bosses"]:
            data["magtheridon"]["details"].setdefault(
                lockouts[idx].date().isoformat(), []
            ).append(raid["reportCode"])
        if "Moroes" in raid["bosses"]:
            data["kharazan"]["details"].setdefault(
                lockouts[idx].date().isoformat(), []
            ).append(raid["reportCode"])
    for raid in ("kharazan", "gruul", "magtheridon"):
        data[raid]["percentage"] = sum(
            1 for lockout in data[raid]["details"].values() if lockout
        ) / len(lockouts)
    return data


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
        json.dump(
            {
                "raids": raids,
                "attendance": compute_attendance(raids=raids),
                "name": name,
            },
            file,
            indent=4,
        )

with open("./data/config/lockouts.json", "w+") as file:
    json.dump([lockout.date().isoformat() for lockout in get_raid_lockouts()], file)
