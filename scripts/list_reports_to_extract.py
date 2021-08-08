import datetime
import os

from lib.wcl import authenticate, fetch_reports

authenticate()
now = datetime.datetime.now()
seven_days_ago = now + datetime.timedelta(days=-7)
reports = []
for zone_id in (1008, 1007):
    reports += fetch_reports(
        guild_id=516114,
        start_time=int(seven_days_ago.timestamp()) * 1000,
        end_time=int(now.timestamp()) * 1000,
    )
reports_set = set()
for report in reports:
    if os.path.isfile(f"./raid-data/{report['code']}.json"):
        continu
    reports_set.add(report["code"])
for report_code in reports_set:
    print(report_code)
