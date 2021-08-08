#!/bin/bash
set -e

source venv/bin/activate
echo "Doing report $1"
python scripts/report_extracter.py $1
python scripts/analyzer.py raid-data/$1.json
python scripts/characters.py
hugo new --kind=raid raids/$1.md
echo "Done"
