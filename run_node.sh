#!/bin/bash

re='^[0-9]+$'

if [ -z "$1" ]
    then 
        echo "Please provide container name!"
        exit 1
fi

if [ -z "$2" ] || ! [[ $2 =~ $re ]] || [ $2 -lt 1 ] || [ $2 -gt 4 ]
    then 
        echo "Please provide port order (1, 2, 3, 4)"
        exit 1
fi

sudo docker run -it --name $1 \
  -p 5005$2:50051 \
  -p 1000$2:10001 \
  -v $(pwd):/opt/iroha_data \
  -v blockstore1:/tmp/block_store \
  --network=iroha-network \
  --entrypoint=/bin/bash \
  hyperledger/iroha:develop
