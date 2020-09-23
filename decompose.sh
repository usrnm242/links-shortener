#!/usr/bin/env bash

docker ps -a  # list of active images

docker-compose down
rm -rf ./mysql/data  # u need to do backup before
