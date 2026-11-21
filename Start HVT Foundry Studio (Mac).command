#!/bin/bash
# Double-click to start HVT Foundry Studio on a Mac.
cd "$(dirname "$0")"
if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3 is not installed. Get it from https://www.python.org/downloads/ then try again."
  read -p "Press Enter to close."; exit 1
fi
python3 studio/app.py
