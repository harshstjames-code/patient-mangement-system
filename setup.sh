#!/bin/bash

# Patient Management System - Setup Script for Linux/Mac

echo "========================================"
echo "Patient Management System Setup"
echo "========================================"
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.7+ from https://www.python.org/"
    exit 1
fi

echo "[1/5] Python found. Creating virtual environment..."
python3 -m venv venv || {
    echo "ERROR: Failed to create virtual environment"
    exit 1
}

echo "[2/5] Activating virtual environment..."
source venv/bin/activate

echo "[3/5] Installing dependencies..."
pip install -r requirements.txt || {
    echo "ERROR: Failed to install dependencies"
    exit 1
}

echo "[4/5] Generating datasets..."
cd model
python create_dataset.py || {
    echo "ERROR: Failed to create training dataset"
    exit 1
}
cd ..

cd database
python create_hospital_data.py || {
    echo "ERROR: Failed to create hospital dataset"
    exit 1
}
cd ..

echo "[5/5] Training ML model... (This may take a minute)"
cd model
python train_model.py || {
    echo "ERROR: Failed to train model"
    exit 1
}
cd ..

echo
echo "========================================"
echo "Setup Complete!"
echo "========================================"
echo
echo "To start the application, run:"
echo "  python app.py"
echo
echo "Then open your browser and go to:"
echo "  http://localhost:5000"
echo
