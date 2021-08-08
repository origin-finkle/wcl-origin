import json
import sys

from lib.wcl import query, authenticate, fetch_report

if len(sys.argv) != 2:
    sys.stderr.write(f"Usage: {sys.argv[0]} REPORTID\n")
    exit(1)


def log_debug(str):
    sys.stderr.write(f"{str}\n")


def fetch_report_events(report, fight, start_time, end_time):
    fight["events"] = []
    while 42:
        log_debug(f"Page: {start_time}")

        response = query(
            f"""
        query getReportEvents {{
            reportData{{
                report(code: "{report["code"]}")
                {{
                    events(startTime: {start_time}, endTime: {end_time}, limit: 10000, dataType: CombatantInfo)
                    {{
                        data
                        nextPageTimestamp
                    }}
                }}
            }}
        }}
            """
        )

        fight["events"] += response.json()["data"]["reportData"]["report"]["events"][
            "data"
        ]
        next_timestamp = response.json()["data"]["reportData"]["report"]["events"][
            "nextPageTimestamp"
        ]
        if not next_timestamp:
            break
        start_time = next_timestamp


authenticate()
report_id = sys.argv[1]
report = fetch_report(report_id=report_id)
for fight in report["fights"]:
    log_debug(f"Doing fight: {fight['name']}")
    fetch_report_events(
        report=report,
        fight=fight,
        start_time=fight["startTime"],
        end_time=fight["endTime"],
    )

with open(f"./raid-data/{report['code']}.json", "w+") as file:
    json.dump(report, file, indent=4)
