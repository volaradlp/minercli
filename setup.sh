#!/bin/bash

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if Python is installed
if ! command_exists python3; then
    echo "Python 3 is not installed. Please install Python 3 and try again."
    exit 1
fi

# Check if Poetry is installed
if ! command_exists poetry; then
    echo "Poetry is not installed. Installing Poetry..."
    curl -sSL https://install.python-poetry.org | python3 -
fi

# Install dependencies using Poetry
echo "Installing dependencies..."
poetry install

# Get the absolute directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Add the bin directory to PATH in both .zshrc and .bashrc
echo "export PATH=$SCRIPT_DIR/bin:\$PATH" >> ~/.zshrc
echo "export PATH=$SCRIPT_DIR/bin:\$PATH" >> ~/.bashrc

# Update current session's PATH
export PATH=$SCRIPT_DIR/bin:$PATH

# Inform success
GREEN='\033[0;32m'
NC='\033[0m' # No Color
printf "${GREEN}### Volara setup successful ###${NC}\n"
echo 'Please restart your terminal or run 'source ~/.zshrc' or 'source ~/.bashrc' to use the 'volara' command.'
echo 'Start mining with `./bin/volara mine start`'