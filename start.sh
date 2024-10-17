#!/bin/bash

# Name of the container
CONTAINER_NAME="volara_miner"

# Function to check if the container exists
container_exists() {
    docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"
}

# Function to check if the container is running
is_container_running() {
    docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"
}

# Function to run the container if it doesn't exist
run_container() {
    echo "Running ${CONTAINER_NAME} container interactively..."
    docker run -it -e VANA_PRIVATE_KEY=${VANA_PRIVATE_KEY} --name ${CONTAINER_NAME} volara/miner
}

# Function to start the container if it exists but is not running
start_container() {
    echo "Starting ${CONTAINER_NAME} container interactively..."
    docker start -i ${CONTAINER_NAME}
}

# Function to attach to a running container
attach_container() {
    echo "Attaching to ${CONTAINER_NAME} container..."
    docker attach --sig-proxy=false ${CONTAINER_NAME}
}

# Main script
if ! container_exists; then
    run_container
elif ! is_container_running; then
    start_container
else
    echo "${CONTAINER_NAME} container is already running."
    attach_container
fi

# Trap to handle SIGINT (Ctrl+C) gracefully
trap 'echo "Detached from container. To stop it, use: docker stop ${CONTAINER_NAME}"; exit' SIGINT

# Keep the script running to maintain the container connection
while true; do
    sleep 1
done