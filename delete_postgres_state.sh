#!/bin/bash

docker container rm $(docker container ls -a | grep postgis | awk '{print $1}')
docker volume rm house_trend_discovery_pgdata
