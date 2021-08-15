#!/bin/bash
set -e

for file in $(ls data/characters/)
do
    filename=${file%.*}
    if [[ ! -f "content/characters/${filename}.md" ]]
    then
        hugo new --kind=character "content/characters/${filename}.md"
    fi
done