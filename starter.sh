#!/bin/bash
set -e

dhclient
sleep 1
chmod 0600 /usr/local/bin/keyfile 
chown mongodb:mongodb /usr/local/bin/keyfile
exec $@
