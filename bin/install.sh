#!/bin/bash
pip install -r requirements.txt
cd mdownotes/vite-project
npm install
sudo apt update
sudo apt install -y sqlite3
sudo apt install -y libsqlite3-dev
cd ../../