#!/bin/bash
set -e

source venv/bin/activate
for report_id in $(python scripts/list_reports_to_extract.py)
do
    bash ./scripts/new_report.sh $report_id
    python scripts/characters.py
    bash scripts/characters.sh
done