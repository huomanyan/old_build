#!/bin/bash
for ((i=0; i<150000; i=i+30000)); do
touch issues_log/info_$i.log
python issueRepair.py $i 30000 >> issues_log/info_$i.log 2>&1 &
done