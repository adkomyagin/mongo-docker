#!/bin/bash
set -e

dhclient
sleep 1
#exec mongod --smallfiles --logpath /data/mongod.log $@ 
exec mongos --logpath /data/mongos.log $@
