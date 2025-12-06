#!/bin/bash

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
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# Run the CLI
echo "Running parser..."
python -m cli.main

# Deactivate venv
echo "Deactivating virtual environment..."
deactivate

# Finished
echo "Done!"
