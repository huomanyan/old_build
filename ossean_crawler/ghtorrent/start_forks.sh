#!/bin/bash
for ((i=0; i<150000; i=i+30000)); do
touch forks_log/info_$i.log
python forksIncre.py $i 30000 >> forks_log/info_$i.log 2>&1 &
done