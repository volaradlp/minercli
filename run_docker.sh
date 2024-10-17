#!/bin/bash

echo -e "
@@@                                      @@@
@@@@@@                                @@@@@@
@@@@@@@@@                          @@@@@@@@@
@@ @@@@@@@@                      @@@@@@@@ @@
@@@@@ @@@@@@@@                 @@@@@@@  @@@@
@@@@@@@@ @@@@@@              @@@@@@@ @@@@@@@
           @@@@@@          @@@@@@@ @@@@@@@@@
    @@@@@    @@@@@@       @@@@@  @@@@@@ @@@@
  @@@@  @@@  @ @@@@@     @@@@  @@@@@@ @@@@@ 
 @@@   @@  @@ @ @@@@@   @@@@ @@@@@ @@@@@@   
  @@  @@  @@ @@@  @@@@ @@@ @@@@ @@@@@@@ @@  
   @  @@  @@ @@ @  @@@@@@   @@@@@@@  @@@@@  
      @@  @@  @@ @@ @@@@ @@@@@@  @@@@@@@    
      @@  @@  @@@  @@ @   @@@@@@@@@@@       
      @@@ @@@   @@@  @@@@@         @@@      
       @@  @@ @@  @@@@   @@@@@@@@@@@        
         @  @@ @@    @@@@@@                 
            @@@ @@@@     @@@@@@@@@          
              @@  @@@@@                     
               @@@   @@@@@@@@               
                 @@@@@                      
                    @@@@                    
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
▗▖  ▗▖ ▗▄▖ ▗▖    ▗▄▖ ▗▄▄▖  ▗▄▖ 
▐▌  ▐▌▐▌ ▐▌▐▌   ▐▌ ▐▌▐▌ ▐▌▐▌ ▐▌
▐▌  ▐▌▐▌ ▐▌▐▌   ▐▛▀▜▌▐▛▀▚▖▐▛▀▜▌
 ▝▚▞▘ ▝▚▄▞▘▐▙▄▄▖▐▌ ▐▌▐▌ ▐▌▐▌ ▐▌
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"

CONTAINER_NAME="volara_miner"

# Function to check if the container exists
container_exists() {
    sudo docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"
}

# Function to check if the container is running
is_container_running() {
    sudo docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"
}

# Function to run the container if it doesn't exist
run_container() {
    echo "Running ${CONTAINER_NAME} container interactively..."
    sudo docker run -it -e VANA_PRIVATE_KEY=${VANA_PRIVATE_KEY} --name ${CONTAINER_NAME} volara/miner
}

# Function to start the container if it exists but is not running
start_container() {
    echo "Starting ${CONTAINER_NAME} container interactively..."
    sudo docker start -i ${CONTAINER_NAME}
}

# Function to attach to a running container
attach_container() {
    echo "Attaching to ${CONTAINER_NAME} container..."
    sudo docker attach --sig-proxy=false ${CONTAINER_NAME}
}

BOLD=$(tput bold)
NORMAL=$(tput sgr0)
PINK='\033[1;35m'

show() {
    case $2 in
        "error")
            echo -e "${PINK}${BOLD}❌ $1${NORMAL}"
            ;;
        "progress")
            echo -e "${PINK}${BOLD}⏳ $1${NORMAL}"
            ;;
        *)
            echo -e "${PINK}${BOLD}✅ $1${NORMAL} "
            ;;
    esac
}

check_docker_installed() {
    if command -v docker >/dev/null 2>&1; then
        show "Docker is already installed."
        return 0
    else
        return 1
    fi
}

pull_volara_image() {
    show "Pulling Volara image..." "progress"
    sudo docker pull volara/miner > /dev/null 2>&1
    show "Volara image pulled successfully."
}

install_docker() {
    show "Installing Docker..." "progress"
    source <(wget -O - "https://raw.githubusercontent.com/zunxbt/installation/98a351c5ff781415cbb9f1a250a6d2699cb814c7/docker.sh")
}

prompt_user_input() {
    read -p "Enter your burner wallet's private key: " VANA_PRIVATE_KEY
}

run_docker_containers() {
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
}

if ! check_docker_installed; then
    install_docker
fi

pull_volara_image

prompt_user_input

show "Running Docker containers..." "progress"
run_docker_containers
echo