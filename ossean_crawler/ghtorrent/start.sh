#!/bin/bash
for ((i=0; i<150000; i=i+30000)); do
touch log/info_$i.log
python **.py $i 30000 >> log/info_$i.log 2>&1 &
done