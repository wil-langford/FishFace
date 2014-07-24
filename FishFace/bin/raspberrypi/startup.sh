#!/bin/bash

export PYRO_SERIALIZERS_ACCEPTED=serpent,json,marshal,pickle

# which address should the Pyro nameserver run on?
PYRO_HOST_IP='192.168.0.1'

# Session name argument
SES_NAME='FishFaceStartup'

# start in detached mode
/usr/bin/screen -dmS $SES_NAME /usr/bin/python -m Pyro4.naming --host=$PYRO_HOST_IP

# set up the Pyro4 nameserver window
# /usr/bin/screen -S $SES_NAME -p 0 -X exec /usr/bin/python -m Pyro4.naming --host=$PYRO_HOST_IP

# wait 2 seconds to make sure Pyro has had time to start up
sleep 2

# set up the imagery server
/usr/bin/screen -S $SES_NAME -X screen /usr/bin/python /home/pi/imageryserver.py
