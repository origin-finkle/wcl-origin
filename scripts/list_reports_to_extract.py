import datetime
import os

from lib.wcl import authenticate, fetch_reports

authenticate()
now = datetime.datetime.now()
fourteen_days_ago = now + datetime.timedelta(days=-14)
reports = fetch_reports(
    guild_id=516114,
    start_time=int(fourteen_days_ago.timestamp()) * 1000,
    end_time=int(now.timestamp()) * 1000,
)
reports_set = set()
for report in reports:
    if os.path.isfile(f"./raid-data/{report['code']}.json"):
        continue
    activity_x_ago = now.timestamp() - (report["endTime"] / 1000)
    if activity_x_ago >= 30 * 60:  # no activity in the last 30min
        reports_set.add(report["code"])
for report_code in reports_set:
    print(report_code)
