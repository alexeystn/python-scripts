#!/bin/bash
cd /root/parser
python3 task_parser.py
python3 task_analyzer.py
python3 task_trends.py
cp database.db ./output/database.db
