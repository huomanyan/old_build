#!/bin/bash
for ((i=0; i<150000; i=i+30000)); do
touch commits_log/info_$i.log
python commitsIncre.py $i 30000 >> commits_log/info_$i.log 2>&1 &
done