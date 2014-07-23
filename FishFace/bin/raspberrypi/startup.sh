#!/usr/bin/bash

# which address should the Pyro nameserver run on?
PYRO_HOST_IP='192.168.0.1'

# Session name argument
SES_NAME='FishFaceStartup'

# start in detached mode
screen -dmS $SES_NAME

# set up the Pyro4 nameserver window
export PYRO_SERIALIZERS_ACCEPTED=serpent,json,marshal,pickle
screen -S $SES_NAME -p 0 -X exec python -m Pyro4.naming --host=$PYRO_HOST_IP

# wait 5 seconds to make sure Pyro has had time to start up
sleep 5

# set up the imagery server
screen -S $SES_NAME -X screen
screen -S $SES_NAME -X exec python imageryserver.py
