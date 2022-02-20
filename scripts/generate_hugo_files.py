import json
import sys
import os
import datetime
import re
import pytz

report_code = sys.argv[1]
prefix = f"./content/raids/{report_code}"
try:
    os.mkdir(prefix)
except FileExistsError:
    pass


def sanitize_fight_name(name):
    d_sanitized = name.replace(" ", "-")
    d_sanitized = re.sub(r"[^a-zA-Z0-9\.\-_]", "", d_sanitized).lower()
    while (d2 := d_sanitized.replace("--", "-")) and d2 != d_sanitized:
        d_sanitized = d2
    return d_sanitized


with open(f"./data/raids/{report_code}/logs.json") as f:
    data = json.load(f)
    date = datetime.datetime.fromtimestamp(
        data["startTime"] / 1000, pytz.UTC
    ).isoformat()
    with open(f"{prefix}/_index.md", "w+") as w_file:
        w_file.write(
            f"""---
title: "{data['title']} | {report_code}"
reportCode: "{report_code}"
date: {date}
---
"""
        )
    for d in data.get("fights"):
        d_sanitized = sanitize_fight_name(d)
        try:
            os.mkdir(f"{prefix}/fight-{d_sanitized}")
        except FileExistsError:
            pass
        with open(f"{prefix}/fight-{d_sanitized}/_index.md", "w+") as w_file:
            w_file.write(
                f"""---
title: "{d}"
reportCode: "{report_code}"
fight: "{d}"
date: {date}
---
"""
            )

    for d in data["actors"]:
        try:
            os.mkdir(f"{prefix}/player-{d.lower()}")
        except FileExistsError:
            pass
        with open(f"{prefix}/player-{d.lower()}/_index.md", "w+") as w_file:
            w_file.write(
                f"""---
title: "{d}"
reportCode: "{report_code}"
player: "{d}"
date: {date}
---
"""
            )

with open(f"./data/raids/{report_code}/analysis.json") as f:
    data = json.load(f)
    for player in data.values():
        for fight_name in player.get("fights", {}).keys():
            fight_name_sanitized = sanitize_fight_name(fight_name)
            with open(
                f"{prefix}/player-{player['name'].lower()}/{fight_name_sanitized}.md",
                "w+",
            ) as w_file:
                w_file.write(
                    f"""---
title: "{fight_name}"
reportCode: "{report_code}"
player: "{player['name']}"
fight: "{fight_name}"
date: {date}
---
"""
                )
            with open(
                f"{prefix}/fight-{fight_name_sanitized}/{player['name'].lower()}.md",
                "w+",
            ) as w_file:
                w_file.write(
                    f"""---
title: "{player['name']}"
reportCode: "{report_code}"
player: "{player['name']}"
fight: "{fight_name}"
date: {date}
---
"""
                )
