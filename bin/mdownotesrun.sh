#!/bin/bash

set -Eeuo pipefail
set -x 
cd ~/mdownotespublic
if [ -e "var/mdownotes.sqlite3" ]; then
    set -x
    # build the vite project embbedded in this application
    cd ~/mdownotespublic/mdownotes/vite-project
    npm run build
    rm -rf ../static/assets
    mv dist/assets ../static/assets/
    # swtich back and then run the app
    cd ~/mdownotespublic
    flask --app mdownotes --debug run --host 0.0.0.0 --port 8000
else
    echo "Error: can't find database var/mdownotes.sqlite3"
    echo "Try: ./bin/mdownotesdb create"
    exit 1
fi