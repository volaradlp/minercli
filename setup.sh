#!/bin/bash

poetry install

# Get the absolute directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

echo "export PATH=$SCRIPT_DIR/bin:\$PATH" >> ~/.zshrc

echo "export PATH=$SCRIPT_DIR/bin:\$PATH" >> ~/.bashrc

export PATH=$SCRIPT_DIR/bin:$PATH

echo 'Volara setup successful.'