#!/bin/bash
cd "$(dirname "$0")"
( sleep 1.5; open "http://localhost:8080/admin" ) &
python3 server.py
