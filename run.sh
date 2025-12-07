#!/bin/bash

if [ $# -ge 1 ]; then
    INPUT_FILE="$1"
else
    INPUT_FILE="$DEFAULT_FILE"
fi

echo "=== Smart Financial Parser ==="

# Go to project root (location of this script)
cd "$(dirname "$0")"

# Create venv if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip & install dependencies
echo "Installing dependencies..."
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

# Run the CLI
echo "Running parser..."
python3 -m cli.main $INPUT_FILE

# Deactivate venv
echo "Deactivating virtual environment..."
deactivate

# Finished
echo "Done!"
