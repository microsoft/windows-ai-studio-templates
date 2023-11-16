#!/bin/bash

# Set the script to exit immediately on any command error
# set -e

# Check for OS version to be Ubuntu 22.04 LTS
source /etc/os-release

if [[ "$NAME" != "Ubuntu" ]] || [[ "$VERSION_ID" != "22.04" && "$VERSION_ID" != "20.04" && "$VERSION_ID" != "18.04" ]]; then
    echo "This script is designed for Ubuntu 22.04, 20.04, or 18.04 LTS. Exiting."
    exit 1
else
    echo "Valid OS version detected."
fi


# Validate that CUDA runtime is present
if ! ldconfig -p | grep libcudart.so &> /dev/null; then
    echo "CUDA runtime is not detected on the system. Please install the CUDA runtime and try again."
    exit 1
else
    echo "CUDA Runtime detected."
fi

###################################
# Prerequisites

# Get the directory of the current script
SCRIPT_DIR="$(dirname "$0")"

# Get the current working directory
WORKING_DIR="$(pwd)"

# Update the list of packages
echo "Updating package list..."
sudo apt-get update

# Install pre-requisite packages.
echo "Installing prerequisite packages..."
sudo apt-get install -y wget apt-transport-https ca-certificates curl software-properties-common


###################################
# Install Conda

# Check if Conda is not already installed
if [ ! -f "$HOME/miniconda/bin/conda" ]; then
    echo "Downloading Miniconda installer..."
    wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh

    echo "Installing Miniconda..."
    bash Miniconda3-latest-Linux-x86_64.sh -b -p $HOME/miniconda

    echo "Removing installer..."
    rm Miniconda3-latest-Linux-x86_64.sh

    # Initialize Conda for bash shell
    echo "Initializing Conda for bash..."
    eval "$($HOME/miniconda/bin/conda shell.bash hook)"
    
    # Optionally, add Conda to PATH (depends on your preferences)
    echo "Adding Conda to PATH in ~/.bashrc..."
    echo 'export PATH="$HOME/miniconda/bin:$PATH"' >> ~/.bashrc
else
    echo "Conda is already installed. Skipping installation."
fi

# refresh PATH to use Conda
. ~/.bashrc

# Check for the -force flag
FORCE_RESET=false
for arg in "$@"; do
    if [ "$arg" == "-force" ]; then
        FORCE_RESET=true
        break
    fi
done

# Create or reset environment from conda.yaml located in the script's directory
if [ ! -d "$WORKING_DIR/.direnv" ] || [ "$FORCE_RESET" = true ]; then
    if [ "$FORCE_RESET" = true ] && [ -d "$WORKING_DIR/.direnv" ]; then
        echo "Removing existing .direnv directory..."
        conda env remove -p "$WORKING_DIR/.direnv"
    fi

    echo "Creating or resetting Conda environment from $SCRIPT_DIR/conda-environment.yaml..."
    $HOME/miniconda/bin/conda env create -f "$SCRIPT_DIR/conda-environment.yaml" -p "$WORKING_DIR/.direnv"
else
    echo "Environment directory .direnv already exists. Use -force to reset. Skipping environment creation."
fi

echo "Script execution completed."
