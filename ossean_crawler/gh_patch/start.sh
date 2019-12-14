#!/bin/bash
for ((i=0; i<35000; i=i+7000)); do
touch log/info_$i.log
python **.py $i 7000 >> log/info_$i.log 2>&1 &
done