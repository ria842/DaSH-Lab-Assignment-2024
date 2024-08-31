#!/bin/bash

# Number of clients to start
NUM_CLIENTS=5



# Allow server to start
sleep 2

# Launch the specified number of clients
for i in $(seq 1 $NUM_CLIENTS)
do
    python3 client.py $i &
done

# Wait for all background jobs to finish
wait
