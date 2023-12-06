#!/bin/bash

# Set the script to exit immediately on any command error
# set -e

# Get the directory of the current script
SCRIPT_DIR="$(dirname "$0")"

# Get the current working directory
WORKING_DIR="$(pwd)"

# Check for the -force flag
FORCE_RESET=false
for arg in "$@"; do
    if [ "$arg" == "-force" ]; then
        FORCE_RESET=true
        break
    fi
done

# Refresh conda env
/opt/miniconda/bin/conda init
. ~/.bashrc

# Create or reset environment from conda.yaml located in the script's directory
if [ ! -d "$WORKING_DIR/.direnv" ] || [ "$FORCE_RESET" = true ]; then
    if [ "$FORCE_RESET" = true ] && [ -d "$WORKING_DIR/.direnv" ]; then
        echo "Removing existing .direnv directory..."
        conda env remove -p "$WORKING_DIR/.direnv"
    fi

    echo "Creating or resetting Conda environment from $SCRIPT_DIR/conda-environment.yml..."
    conda env create -f "$SCRIPT_DIR/conda-environment.yml" -p "$WORKING_DIR/.direnv"
else
    echo "Environment directory .direnv already exists. Use -force to reset. Skipping environment creation."
fi

echo "Script execution completed."
