#!/bin/bash
for ((i=0; i<15; i=i+1)); do
touch log/info_$i.log
python commits_get.py  >> log/info_$i.log 2>&1 &
done
