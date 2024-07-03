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

# Todo make the name be dynamic with the project.
# Create or reset environment from conda.yaml located in the script's directory
echo "Creating or resetting Conda environment from $SCRIPT_DIR/conda-environment.yml..."
/opt/miniconda/bin/conda env create -f "$SCRIPT_DIR/conda-environment.yml"

echo "Script execution completed."
