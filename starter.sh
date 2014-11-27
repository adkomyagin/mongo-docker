#!/bin/bash
set -e

dhclient
sleep 1
exec $@
