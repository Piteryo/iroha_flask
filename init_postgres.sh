#!/bin/bash

sudo docker stop $(sudo docker ps -aq)
sudo docker system prune --volumes

rm -rf *@test.priv

sudo docker volume create blockstore1
sudo docker volume create blockstore2
sudo docker volume create blockstore3
sudo docker volume create blockstore4

sudo docker network create iroha-network --subnet=192.168.80.0/16

sudo docker run --name iroha-postgres1 \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=mysecretpassword \
  -p 5432:5432 \
  --network=iroha-network \
  -d postgres:9.5

sudo docker run --name iroha-postgres2 \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=mysecretpassword \
  -p 5433:5432 \
  --network=iroha-network \
  -d postgres:9.5

sudo docker run --name iroha-postgres3 \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=mysecretpassword \
  -p 5434:5432 \
  --network=iroha-network \
  -d postgres:9.5

sudo docker run --name iroha-postgres4 \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=mysecretpassword \
  -p 5435:5432 \
  --network=iroha-network \
  -d postgres:9.5
