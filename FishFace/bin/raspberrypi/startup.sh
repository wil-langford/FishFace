#!/bin/bash

export PYRO_SERIALIZERS_ACCEPTED=serpent,json,marshal,pickle

# which address should the Pyro nameserver run on?
PYRO_HOST_IP='mystaticip'

# Session name argument
SES_NAME='FishFaceStartup'

# start in detached mode
/usr/bin/screen -dmS $SES_NAME /usr/bin/python -m Pyro4.naming --host=$PYRO_HOST_IP

# wait 4 seconds to make sure Pyro has had time to start up
sleep 4

# set up the imagery server
/usr/bin/screen -S $SES_NAME -X screen /usr/bin/python /home/pi/imageryserver.py
