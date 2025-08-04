#!/bin/bash

# Define a function to display an error message and exit
error_exit() {
    echo "$1" 1>&2
    exit 1
}

# Check for Ubuntu or Debian
if ! (grep -q 'Ubuntu' /etc/issue || grep -q 'Debian' /etc/issue); then
    error_exit "This script is only supported on Ubuntu and Debian."
fi

# Purge the NVIDIA Container Toolkit packages
echo "Purging the NVIDIA Container Toolkit packages..."
sudo apt-get purge -y nvidia-container-toolkit || error_exit "Failed to purge the NVIDIA Container Toolkit packages."

# Remove the repository configuration
echo "Removing repository configuration..."
sudo rm -f /etc/apt/sources.list.d/nvidia-container-toolkit.list
sudo rm -f /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg || error_exit "Failed to remove repository configuration."

# Autoremove to clean up dependencies
echo "Removing unused packages..."
sudo apt-get autoremove -y || error_exit "Failed to remove unused packages."

# Update the package lists after removal
echo "Updating package lists..."
sudo apt-get update || error_exit "Failed to update package lists."

echo "Uninstallation completed successfully."
