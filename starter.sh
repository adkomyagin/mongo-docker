#!/bin/bash
set -e

dhclient
sleep 1
#exec mongod --smallfiles $@ 
exec mongos $@
