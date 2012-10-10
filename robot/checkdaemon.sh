#!/bin/bash

count=`ps -ef | grep xtalk | wc -l`

echo $count
if [ $count -gt 1 ]; then
    echo "exist"
else
    echo "not exist"
    nohup ./xtalk.py &
fi
