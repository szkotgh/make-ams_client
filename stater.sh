#!bin/bash

SERVICE_NAME="MAKE; AMS Client"
DIR="$( cd "$( dirname "$0" )" && pwd -P )"

# Get the path of the script
echo $SERVICE_NAME Path=\'$DIR\'
cd "$DIR"

# # Check if the script is running as root
# if [ "$(id -u)" -ne 0 ]; then
#     echo "$SERVICE_NAME stater must be run as root."
#     echo "Try 'sudo bash $0'"
#     exit 1
# fi

# if git is installed, pull the latest changes
echo "Checking updating..."
if command -v git &> /dev/null; then
    if git pull; then
        echo "Update complete"
    else
        echo "Update Fail"
    fi
else
    echo "$SERVICE_NAME git not found, skipping pull . . ."
fi

# Start Script
python3 app.py