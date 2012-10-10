#!/bin/bash

tty="/dev/ttyACM0"
stty -F $tty speed 9600
v=`cat $tty`
s='
{
  "timestamp":"`date +%FT%T`",
  "value":$v
}'


echo s > /tmp/datafile

curl --request POST --data-binary @datafile.txt --header "U-ApiKey: YOUR_API_KEY_HERE"  http://api.yeelink.net/v1.0/device/515/sensor/640/datapoints


