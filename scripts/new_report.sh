#!/bin/bash
set -e

source venv/bin/activate
echo "Doing report $1"
python scripts/report_extracter.py $1
python scripts/analyzer.py raid-data/$1.json
python scripts/characters.py
if [[ -f ./data/raids/$1/logs.json ]];
then
    python scripts/generate_hugo_files.py $1
fi
echo "Done"
