#!/bin/bash
cd /root/parser
python3 parser.py
python3 analyzer.py
python3 plot_trends.py
cp database.db ./output/database.db
