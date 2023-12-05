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


# Check if NVIDIA Container Toolkit is functional
if nvidia-container-cli -k list --libraries > /dev/null 2>&1; then
    echo "NVIDIA Container Toolkit is already installed and functional."
    exit 0
fi

# Update the package lists for upgrades and package dependencies
echo "Updating package lists..."
sudo apt-get update || error_exit "Failed to update package lists."

# Install the necessary prerequisites
echo "Installing prerequisites..."
sudo apt-get install -y curl gnupg lsb-release || error_exit "Failed to install prerequisites."

# Add the NVIDIA GPG key
echo "Adding the NVIDIA GPG key..."
yes | curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add - || error_exit "Failed to add NVIDIA GPG key."

# Add the repository configuration
FILE=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
if [ -f "$FILE" ]; then
    sudo rm "$FILE"
fi
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg

curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

sudo apt-get update


# Install the NVIDIA Container Toolkit packages
echo "Installing the NVIDIA Container Toolkit packages..."
sudo apt-get install -y nvidia-container-toolkit || error_exit "Failed to install the NVIDIA Container Toolkit packages."

sudo nvidia-ctk runtime configure --runtime=docker || error_exit "Failed to configure docker with the NVIDIA Container Toolkit packages."

# Restart the Docker daemon
echo "Restarting the Docker daemon..."
sudo systemctl restart docker || error_exit "Failed to restart the Docker daemon."

echo "Installation completed successfully."
