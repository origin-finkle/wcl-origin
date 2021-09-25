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
try:
    os.mkdir(f"{prefix}/fight")
except FileExistsError:
    pass
try:
    os.mkdir(f"{prefix}/player")
except FileExistsError:
    pass

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
    for d in data["fights"]:
        d_sanitized = d.replace(" ", "-")
        d_sanitized = re.sub(r"[^a-zA-Z0-9\.\-_]", "", d_sanitized).lower()
        while (d2 := d_sanitized.replace("--", "-")) and d2 != d_sanitized:
            d_sanitized = d2
        try:
            os.mkdir(f"{prefix}/fight/{d_sanitized}")
        except FileExistsError:
            pass
        with open(f"{prefix}/fight/{d_sanitized}/_index.md", "w+") as w_file:
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
            os.mkdir(f"{prefix}/player/{d.lower()}")
        except FileExistsError:
            pass
        with open(f"{prefix}/player/{d.lower()}/_index.md", "w+") as w_file:
            w_file.write(
                f"""---
title: "{d}"
reportCode: "{report_code}"
player: "{d}"
date: {date}
---
"""
            )
